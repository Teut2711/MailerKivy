import csv
import smtplib
import threading
import time

from kivy.app import App
from .prepare_message import PrepMessage
from queue import Queue
from smtplib import SMTPRecipientsRefused
from mailer.mailing_exceptions import FromMissingError, SubjectMissingError


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
        App.get_running_app().root.current_screen.update_info_area(
            "\nProcess Completed !"
        )

    def send_all_mails(self, spreadsheet_path, username, password):
        try:
            self.set_up_connections()

            self._set_total_row_count(spreadsheet_path)

        except smtplib.SMTPAuthenticationError:
            self.close_connections()
            raise smtplib.SMTPAuthenticationError
        else:
            self.smtp_connection.starttls()
            self.smtp_connection.login(username, password)
            App.get_running_app().root.current_screen.update_info_area(
                "Process Started...\n"
            )

            threading.Thread(
                target=self._make_mail_objects,
                args=(spreadsheet_path,),
                daemon=True,
            ).start()

            threading.Thread(
                target=self._send_a_mail, args=(spreadsheet_path,), daemon=True
            ).start()

    def _set_total_row_count(self, spreadsheet_path):

        with open(spreadsheet_path) as csvfile:
            self.total_rows = sum(1 for row in csv.reader(csvfile)) - 1
        app = App.get_running_app()
        app.root.current_screen.ids.progressbar.max = self.total_rows

    def _make_mail_objects(self, spreadsheet_path):

        app = App.get_running_app()
        mails_per_hour = app.config.getint("serverSettings", "mails_per_hour")

        with open(spreadsheet_path) as csvfile:
            reader = csv.DictReader(csvfile)

            for k, row in enumerate(reader, start=1):

                try:
                    email_message = self._get_mail_object_from_row(row)
                except (
                    SubjectMissingError,
                    FromMissingError,
                ) as error_message:
                    email_message = error_message

                finally:
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
            app.root.current_screen.update_info_area(
                "[b]Waiting for 1 hour...[/b]"
            )
            time.sleep(3600)

    def _send_a_mail(self, spreadsheet_path):

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
                app.root.current_screen.update_info_area(
                    f"Row {count+1}) Failed > {error_message}"
                )
            else:
                if failed_recipients:
                    app.root.current_screen.update_info_area(
                        f"Row {count+1}) Failed."
                    )
                else:
                    app.root.current_screen.update_info_area(
                        f"Row {count+1}) Mail sent."
                    )

            finally:
                app.root.current_screen.update_progressbar(count)
                app.root.current_screen.update_screen_progressvalue(
                    count, self.total_rows
                )
                count += 1
                self.mail_queue.task_done()

    def _get_mail_object_from_row(self, row):

        data = {k: v.strip() for k, v in row.items() if v.strip()}
        app = App.get_running_app()

        if not app.config.get("templates", "From") in data:
            raise FromMissingError

        if not app.config.get("templates", "Subject") in data:
            raise SubjectMissingError

        msg = PrepMessage()
        if app.config.get("templates", "From") in data:
            msg["From"] = data[app.config.get("templates", "From")]

        if app.config.get("templates", "Cc") in data:
            msg["Cc"] = data[app.config.get("templates", "Cc")]

        if app.config.get("templates", "Bcc") in data:
            msg["Bcc"] = data[app.config.get("templates", "Bcc")]

        if app.config.get("templates", "To") in data:

            msg["To"] = data[app.config.get("templates", "To")]
        if app.config.get("templates", "Subject") in data:

            msg["Subject"] = data[app.config.get("templates", "Subject")]
        if app.config.get("templates", "attachments") in data:

            msg.add_attachments(
                data[app.config.get("templates", "attachments")]
            )
        if app.config.get("templates", "template_path") in data:
            msg.add_message(
                docx_template_path=data[
                    app.config.get("templates", "template_path")
                ],
                context=data,
            )

        msg.email_message.add_header(
            "Disposition-Notification-To",
            app.config.get("serverSettings", "email_recepient"),
        )

        return msg

    def close_connections(self):
        self.smtp_connection.quit()
