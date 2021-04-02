from kivy.clock import Clock

##  BEWARE OF EVALS
import os
import smtplib
from mailer.LicenseModalView import LicenseModalView
from mailer.LoadingModalView import LoadingModalView
import traceback
from kivy.app import App
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import NoTransition, ScreenManager
from .send_mail import Mailer
from kivy.config import Config
from kivy.uix.button import Button
from kivy.factory import Factory
from mailer.AppScreen import AppScreen

Config.set("input", "mouse", "mouse,multitouch_on_demand")


class CredentialsModalView(ModalView):
    def display_credentials_modalview(self, error_message=None):

        self.ids.username.focus = True
        if error_message:
            self.ids.error_message.text = error_message
        self.ids.error_message.markup = True


class ImageButton(Button):
    image_path = os.path.join(os.path.dirname(__file__), "imgs", "gear.png")


class MailerApp(App):
    def on_start(self):

        data = {
            "license_key": App.get_running_app().config.get("licensing", "license_key"),
            "token": App.get_running_app().config.get("licensing", "token"),
        }

        if not all(data.values()):
            Factory.LicenseModalView().open()

        else:
            Factory.LoadingModalView().open()

    def start_mailing(
        self,
        username,
        password,
    ):

        try:
            self.root.current_screen.manager.current = "mailing"

            if self.root.current_screen.ids.file_path.text:
                self.root.current_screen.update_info_area("Process Started...")
                self.mailer.send_all_mails(
                    self.root.current_screen.ids.file_path.text, username, password
                )
            else:
                self.root.current_screen.ids.file_path.hint_text = (
                    "Please select a csv file"
                )
                self.root.current_screen.ids.file_path.hint_text_color = (
                    1,
                    0,
                    0,
                    1,
                )

        except smtplib.SMTPAuthenticationError:
            credentials = CredentialsModalView()
            credentials.open()
            credentials.display_credentials_modalview(
                error_message="[color=ff0000][b]Invalid username or password. Please enter again.[/b][/color]"
            )
        except Exception:
            self.root.current_screen.update_info_area(
                "[b]Process interrupted[\b]" + "\n" + traceback.format_exc()
            )

    def build(self):
        self.icon = os.path.join(os.path.dirname(__file__), "imgs", "mailer.png")
        self.mailer = Mailer()

        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(AppScreen(name="mailing"))

        return sm

    def build_config(self, config):
        config.setdefaults(
            "serverSettings",
            {
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "imap_host": "smtp.gmail.com",
                "imap_port": 993,
                "mails_per_hour": -1,
            },
        )
        config.setdefaults(
            "templates",
            {
                "folder_path": os.path.dirname(__file__),
                "From": "FROM",
                "To": "TO",
                "Cc": "CC",
                "Bcc": "BCC",
                "attachments": "FILE-ATTACHMENT",
                "template_path": "TEMPLATE-PATH",
                "Subject": "SUBJECT",
            },
        )
        config.setdefaults(
            "licensing",
            {"license_key": "", "token": ""},
        )

    def build_settings(self, settings):
        settings.add_json_panel(
            "Settings",
            self.config,
            filename=os.path.join(os.path.dirname(__file__), "server_settings.json"),
        )


def main():
    MailerApp().run()
