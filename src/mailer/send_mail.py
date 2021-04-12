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
        self.mail_queue = Queue()
        self.max_mails = 100
        self.total_rows = None

    def _set_total_row_count(self, spreadsheet_path):

        with open(spreadsheet_path) as csvfile:
            # -1 because total rows is all rows - the header
            self.total_rows = sum(1 for row in csv.reader(csvfile)) - 1

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
            self.mailer.close_connections()
            raise smtplib.SMTPAuthenticationError
        else:
            self.smtp_connection.starttls()
            self.smtp_connection.login(username, password)
            t1 = threading.Thread(
                target=self._make_mail_objects, args=(spreadsheet_path,)
            )
            t1.daemon = True
            t1.start()

            t2 = threading.Thread(
                target=self._send_a_mail, args=(spreadsheet_path,)
            )
            t2.daemon = True
            t2.start()

    def _make_mail_objects(self, spreadsheet_path):
        with open(spreadsheet_path) as csvfile:
            reader = csv.DictReader(csvfile)
            row = iter(reader)
            nth_row = 0

            while True:
                try:
                    if self.mail_queue.qsize() <= self.max_mails:
                        nth_row += 1
                        self.mail_queue.put(
                            self._get_mail_object_from_row(next(row), nth_row)
                        )
                except (
                    SubjectMissingError,
                    FromMissingError,
                ) as error_message:
                    App.get_running_app().root.current_screen.update_info_area(
                        "\n" + str(error_message) + "\n"
                    )

                except StopIteration:
                    return False

    def _send_a_mail(self, spreadsheet_path):
        app = App.get_running_app()
        mails_per_hour = app.config.getint("serverSettings", "mails_per_hour")
        nth_row = 0

        app.root.current_screen.ids.progressbar.max = self.total_rows

        while nth_row != self.total_rows:
            try:
                message = self.mail_queue.get().msg
                nth_row += 1
                failed_recipients = self.smtp_connection.send_message(message)
            except SMTPRecipientsRefused as e:
                app.root.current_screen.update_progressbar(nth_row)
                app.root.current_screen.update_info_area(
                    "Failed: " + str(list(e.recipients.keys()))
                )

            else:

                app.root.current_screen.update_progressbar(nth_row)
                app.root.current_screen.update_screen_progressvalue(
                    nth_row, self.total_rows
                )
                app.root.current_screen.update_info_area(
                    (
                        "Failed: " + str(list(failed_recipients.keys()))
                        if failed_recipients
                        else ""
                    )
                    + "\n"
                    + f"Sent to: {message['To']}"
                )
            self._update_waiting_status_and_sleep(mails_per_hour, nth_row)

        self.mail_queue.join()
        self._show_finished_mailing_status()

    def _update_waiting_status_and_sleep(self, mails_per_hour, nth_row):
        def is_limit_per_hour_reached(nth_row):
            return nth_row % mails_per_hour == 0

        app = App.get_running_app()

        if (
            mails_per_hour > 0
            and is_limit_per_hour_reached(nth_row)
            and nth_row < self.total_rows
        ):
            app.root.current_screen.update_info_area("Waiting for 1 hour...")
            time.sleep(3600)

    def _get_mail_object_from_row(self, row, nth_row):

        data = {k: v.strip() for k, v in row.items() if v.strip()}
        app = App.get_running_app()

        if not app.config.get("templates", "From") in data:
            raise FromMissingError(row_num=nth_row)

        if not app.config.get("templates", "Subject") in data:
            raise SubjectMissingError(row_num=nth_row)

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

        msg.msg.add_header(
            "Disposition-Notification-To",
            app.config.get("serverSettings", "email_recepient"),
        )

        return msg

    def close_connections(self):
        self.smtp_connection.quit()
