##  BEWARE OF EVALS
import csv
import smtplib
import threading
import time

from kivy.app import App
from .prepare_message import PrepMessage
from queue import Queue
from smtplib import SMTPRecipientsRefused


class Mailer:
    def __init__(self):
        self.mail_queue = Queue()
        self.max_mails = 100
        self.is_queue_processed_fully = False

    def set_up_connections(self):
        self.smtp_connection = smtplib.SMTP(
            App.get_running_app().config.get("serverSettings", "smtp_host"),
            App.get_running_app().config.getint("serverSettings", "smtp_port"),
        )

    def send_all_mails(self, spreadsheet_path, username, password):
        try:
            self.set_up_connections()

        except smtplib.SMTPAuthenticationError:
            self.mailer.close_connections()
        else:
            self.smtp_connection.starttls()
            self.smtp_connection.login(username, password)

            t1 = threading.Thread(
                target=lambda: self.make_mail_objects(spreadsheet_path)
            )
            t1.daemon = True
            t1.start()

            t2 = threading.Thread(
                target=lambda: self.send_mail_and_update_gui(spreadsheet_path)
            )
            t2.daemon = True
            t2.start()

        if self.is_queue_processed_fully:
            t1.join()
            t2.join()
            self.close_connections()
            App.get_running_app().root.current_screen.update_info_area(
                "Process Completed !"
            )

    def make_mail_objects(self, spreadsheet_path):
        with open(spreadsheet_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if self.mail_queue.qsize() <= self.max_mails:
                    self.mail_queue.put(self.get_mail_object_from_row(row))

    def send_mail_and_update_gui(self, spreadsheet_path):
        def sent_mails_less_than_limit(nth_row):
            return nth_row % mails_per_hour == 0

        mails_per_hour = App.get_running_app().config.getint(
            "serverSettings", "mails_per_hour"
        )
        nth_row = 0

        with open(spreadsheet_path) as csvfile:
            total_rows = sum(1 for row in csv.reader(csvfile))

        App.get_running_app().root.current_screen.ids.progressbar.max = total_rows

        while nth_row != total_rows:
            try:
                message = self.mail_queue.get().msg
                failed_recipients = self.smtp_connection.send_message(message)

            except SMTPRecipientsRefused as e:
                App.get_running_app().root.current_screen.update_progressbar(nth_row)
                App.get_running_app().root.current_screen.update_info_area(
                    "Failed: " + str(list(e.recipients.keys()))
                )

            else:
                nth_row += 1

                App.get_running_app().root.current_screen.update_progressbar(nth_row)
                App.get_running_app().root.current_screen.update_screen_progressvalue(
                    nth_row, total_rows
                )
                App.get_running_app().root.current_screen.update_info_area(
                    (
                        "Failed: " + str(list(failed_recipients.keys()))
                        if failed_recipients
                        else ""
                    )
                    + "\n"
                    + f"Sent to: {message['To']}"
                )

            if mails_per_hour > 0 and sent_mails_less_than_limit(nth_row):
                App.get_running_app().root.current_screen.update_info_area(
                    "Waiting for 1 hour..."
                )
                time.sleep(3600)

        else:
            self.is_queue_processed_fully = True

    def get_mail_object_from_row(self, row):
        data = {k: v.strip() for k, v in row.items() if v.strip()}
        msg = PrepMessage()
        if App.get_running_app().config.get("templates", "From") in data:
            msg["From"] = data[App.get_running_app().config.get("templates", "From")]

        if App.get_running_app().config.get("templates", "Cc") in data:
            msg["Cc"] = data[App.get_running_app().config.get("templates", "Cc")]

        if App.get_running_app().config.get("templates", "Bcc") in data:
            msg["Bcc"] = data[App.get_running_app().config.get("templates", "Bcc")]

        if App.get_running_app().config.get("templates", "To") in data:

            msg["To"] = data[App.get_running_app().config.get("templates", "To")]
        if App.get_running_app().config.get("templates", "Subject") in data:

            msg["Subject"] = data[
                App.get_running_app().config.get("templates", "Subject")
            ]
        if App.get_running_app().config.get("templates", "attachments") in data:

            msg.add_attachments(
                data[App.get_running_app().config.get("templates", "attachments")]
            )
        if App.get_running_app().config.get("templates", "template_path") in data:
            msg.add_message(
                docx_template_path=data[
                    App.get_running_app().config.get("templates", "template_path")
                ],
                context=data,
            )

        msg.msg.add_header("Disposition-Notification-To", "hivax71254@aramidth.com")
        return msg

    # def show_html_in_browser(self, html_file_path):
    #     webbrowser.open(html_file_path)

    def close_connections(self):
        self.smtp_connection.quit()

        # self.imap_connection.close()
