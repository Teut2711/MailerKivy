import csv
import smtplib
import threading
import time
from kivy.app import App
from .prepare_message import PrepMessage
from queue import Queue
from smtplib import SMTPRecipientsRefused
from mailer.mailing_exceptions import FromError, SubjectError, ToError


class Mailer:
    def __init__(self):
        self.queue_size = 100
        self.mail_queue = Queue(maxsize=self.queue_size)
        self.total_rows = None

    def set_up_connections(self):
        app = App.get_running_app()
        self.smtp_connection = smtplib.SMTP(
            app.config.get("serverSettings", "smtp_host"),
            app.config.getint("serverSettings", "smtp_port"),
        )

    def _show_finished_mailing_status(self):
        self.close_connections()
        App.get_running_app().root.current_screen.ids.info_area.update_info_area(
            "\nProcess Completed !"
        )

    def send_all_mails(self, spreadsheet_path, username, password):
        try:
            self.set_up_connections()

            self.smtp_connection.starttls()
            self.smtp_connection.login(username, password)

        except smtplib.SMTPAuthenticationError as e:
            self.close_connections()
            raise e
        else:
            self._set_total_row_count(spreadsheet_path)
            appscreen = App.get_running_app().root.current_screen.ids
            appscreen.start_mailing.disabled = True
            appscreen.info_area.update_info_area("Process Started...\n")

            threading.Thread(
                target=self._make_mail_objects,
                args=(spreadsheet_path)
            ).start()

            threading.Thread(target=self._send_a_mail).start()

    def _set_total_row_count(self, spreadsheet_path):

        with open(spreadsheet_path) as csvfile:
            self.total_rows = sum(1 for row in csv.reader(csvfile)) - 1
        app = App.get_running_app()
        app.root.current_screen.ids.progressbar_component.ids.progressbar.max = (
            self.total_rows
        )

    def _make_mail_objects(self, spreadsheet_path):

        app = App.get_running_app()
        mails_per_hour = app.config.getint("serverSettings", "mails_per_hour")

        with open(spreadsheet_path) as csvfile:
            reader = csv.DictReader(csvfile)

            for k, row in enumerate(reader, start=1):

                try:
                    email_message = self.get_mail_object_from_row(row)
                except (
                    SubjectError,
                    FromError,
                ) as error_message:
                    email_message = error_message

                self.mail_queue.put(email_message)
                self._update_waiting_status_and_sleep(k, mails_per_hour)

        self.mail_queue.join()
        self._show_finished_mailing_status()
        app.root.current_screen.ids.start_mailing.disabled = False

    def _is_limit_per_hour_reached(self, nth_row, mails_per_hour):
        return nth_row % mails_per_hour == 0

    def _update_waiting_status_and_sleep(self, nth_row, mails_per_hour):
        if (
            mails_per_hour > 0
            and self._is_limit_per_hour_reached(nth_row, mails_per_hour)
            and nth_row < self.total_rows
        ):
            app = App.get_running_app()
            app.root.current_screen.ids.info_area.update_info_area(
                "[b]Waiting for 1 hour...[/b]"
            )
            time.sleep(3600)

    def _send_a_mail(self):

        app = App.get_running_app()
        count = 1
        while True:

            message = self.mail_queue.get()  # get message or exception
            try:
                if isinstance(message, PrepMessage):
                    failed_recipients = self.smtp_connection.send_message(
                        message.email_message
                    )
                else:
                    raise message
            except Exception as error_message:
                app.root.current_screen.ids.info_area.update_info_area(
                    f"Row {count+1}) Failed > {error_message}"
                )
            else:
                if failed_recipients:
                    app.root.current_screen.ids.info_area.update_info_area(
                        f"Row {count+1}) Failed."
                    )
                else:
                    app.root.current_screen.ids.info_area.update_info_area(
                        f"Row {count+1}) Mail sent."
                    )

            finally:
                progressbar = app.root.current_screen.ids.progressbar_component
                progressbar.update_progressbar(count)
                progressbar.update_screen_progressvalue(count, self.total_rows)
                count += 1
                self.mail_queue.task_done()

    def get_mail_object_from_row(self, row):

        data = {k: v.strip() for k, v in row.items() if v.strip()}

        msg = PrepMessage()
        app = App.get_running_app()
        try:
            msg["From"] = data[app.config.get("templates", "From")]
        except KeyError:
            raise FromError
        try:
            msg["Subject"] = data[app.config.get("templates", "Subject")]
        except KeyError:
            raise SubjectError
        try:
            msg["Cc"] = data[app.config.get("templates", "Cc")]
        except KeyError:
            pass
        try:
            msg["Bcc"] = data[app.config.get("templates", "Bcc")]
        except KeyError:
            pass
        try:
            msg["To"] = data[app.config.get("templates", "To")]
        except KeyError:
            raise ToError
        try:
            msg.add_attachments(
                data[app.config.get("templates", "attachments")]
            )
        except KeyError:
            pass
        try:
            msg.add_message(
                docx_template_path=data[
                    app.config.get("templates", "template_path")
                ],
                context=data,
            )
        except KeyError:
            pass

        try:
            msg.email_message.add_header(
                "Disposition-Notification-To",
                app.config.get("serverSettings", "email_recepient"),
            )
        except Exception:
            pass

        return msg

    def close_connections(self):
        self.smtp_connection.quit()
