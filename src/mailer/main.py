from kivy.clock import Clock

##  WARNING: EVALS ARE USED
import os
import smtplib
from mailer.License import LicenseModalView, Licensing
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
from mailer.license_exceptions import (
    InvalidCredentialsError,
    InvalidSystemIDError,
    LicenseExpiredError,
    RegistrationTimeExpiredError,
    UserNotRegisteredError,
)
import threading

Config.set("input", "mouse", "mouse,multitouch_on_demand")


class CredentialsModalView(ModalView):
    def display_credentials_modalview(self, error_message=None):

        self.ids.username.focus = True
        if error_message:
            self.ids.error_message_creds.text = error_message
        self.ids.error_message_creds.markup = True


class ImageButton(Button):
    image_path = os.path.join(os.path.dirname(__file__), "imgs", "gear.png")


class MailerApp(App):
    def _validate_license_data(self, licensing, loading_view):

        try:

            licensing.validate_license_data()

        except UserNotRegisteredError:
            loading_view.dismiss()
            license_view = Factory.LicenseModalView()
            license_view.open()

        except (
            InvalidCredentialsError,
            InvalidSystemIDError,
            LicenseExpiredError,
            RegistrationTimeExpiredError,
        ) as error_message:
            loading_view.dismiss()
            license_view = Factory.LicenseModalView()
            license_view.open()
            license_view.ids.error_message_license.text = (
                f"[color=ff0000][b]{error_message}[/b][/color]"
            )
        else:
            loading_view.dismiss()
            timedelta = licensing.calculate_days_remaining()
            self.root.current_screen.ids.days_remaining.text = (
                f"[color=ff0000][i]{timedelta.days} days remaining[/color][/i]"
                if timedelta.days > 2
                else "[b]License will expire in {timedelta.days} day{s if timedelta.days!=1 else}.Buy a new one[/b]"
            )

    def on_start(self):

        loading_view = Factory.LoadingModalView()
        loading_view.open()
        data = {
            "license_key": self.config.get("licensing", "license_key"),
            "token": self.config.get("licensing", "token"),
        }
        licensing = Licensing(**data)
        t = threading.Thread(
            target=self._validate_license_data, args=(licensing, loading_view)
        )
        t.start()

    def start_mailing(
        self,
        username,
        password,
    ):

        try:
            self.root.current_screen.manager.current = "mailing"

            if self.root.current_screen.ids.file_path.text:

                self.mailer.send_all_mails(
                    self.root.current_screen.ids.file_path.text,
                    username,
                    password,
                )
                self.root.current_screen.ids.start_mailing.disabled = True

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
                error_message=(
                    "[color=ff0000][b]Invalid username or password. Please enter again.[/b][/color]"
                )
            )
        except Exception as error_message:
            self.root.current_screen.update_info_area(
                f"[b]Process interrupted[/b] \n {error_message}\n"
            )

    def build(self):
        self.icon = os.path.join(
            os.path.dirname(__file__), "imgs", "mailer.png"
        )
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
                "email_recepient": "",
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
                "image_initial": "IMG",
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
            filename=os.path.join(os.path.dirname(__file__), "settings.json"),
        )


def main():
    MailerApp().run()
