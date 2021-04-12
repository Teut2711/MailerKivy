import base64
import binascii
from datetime import datetime
import json
import subprocess
import threading

import cryptography
from cryptography.fernet import Fernet
from dateutil.zoneinfo import gettz
from kivy.app import App
from kivy.factory import Factory
from kivy.uix.modalview import ModalView

from mailer.license_exceptions import (
    InvalidCredentialsError,
    InvalidSystemIDError,
    LicenseExpiredError,
    RegistrationTimeExpiredError,
)

from .Registration import Registration
from .Validation import Validation
import requests


class CurrentSystemIndependentDateTime:
    def __init__(self):
        try:
            self.datetime = self._get_datetime_from_word_time_api()
        except Exception:
            self.datetime = self._get_datetime_from_system()

    def get_datetime(self):
        return self.datetime

    def _get_datetime_from_word_time_api(self):

        return requests.get(
            "http://worldtimeapi.org/api/timezone/Asia/Kolkata",
        ).json()["datetime"]

    def _get_datetime_from_system(self):
        return datetime.now(tz=gettz("Asia/Kolkata")).isoformat()


class Licensing(Registration, Validation):
    def __init__(self, license_key, token):
        self.license_key = license_key
        self.token = token
        self.current_datetime = (
            CurrentSystemIndependentDateTime().get_datetime()
        )
        self.decypted_data = None

    def _check_system_id(self, system_id_from_token):
        if system_id_from_token != self._get_system_unique_id():
            raise InvalidSystemIDError

    def _check_registration_time_not_expired(
        self, registration_period, current_datetime
    ):
        if not (
            datetime.fromisoformat(registration_period["start"])
            <= datetime.fromisoformat(current_datetime)
            <= datetime.fromisoformat(registration_period["end"])
        ):
            raise RegistrationTimeExpiredError

    def register_new_user(self, license_key, token):
        post_registration_data = super().register_new_user(license_key, token)

        app = App.get_running_app()
        app.config.set(
            "licensing", "license_key", post_registration_data["license_key"]
        )
        app.config.set(
            "licensing",
            "token",
            post_registration_data["token"],
        )
        app.config.write()

    def validate_license_data(self) -> bool:
        return super().validate_license_data(self.license_key, self.token)

    def _get_system_unique_id(self):
        system_id = (
            subprocess.check_output("wmic csproduct get uuid")
            .decode("utf-8")
            .split("\n")[1]
            .strip()
        )
        return system_id

    def _decode_data(self):

        try:
            f = Fernet(self.license_key.encode("utf-8"))
            base64_encoded_data = f.decrypt(self.token.encode("utf-8"))
            json_data = base64.b64decode(base64_encoded_data).decode("utf-8")
            decrypted_data = json.loads(json_data)

        except (
            cryptography.exceptions.InvalidKey,
            cryptography.fernet.InvalidToken,
            binascii.Error,
            ValueError,
        ):
            raise InvalidCredentialsError

        else:
            return decrypted_data


class LicenseModalView(ModalView):
    def _process_license_key_and_token(self, license_key, token):
        try:
            licensing = Licensing(license_key, token)
            licensing.register_new_user(license_key, token)
        except (
            InvalidCredentialsError,
            InvalidSystemIDError,
            LicenseExpiredError,
            RegistrationTimeExpiredError,
        ) as error_message:
            self.loading_view.dismiss()
            self.ids.error_message_license.text = (
                f"[color=ff0000][b]{error_message}[/b][/color]"
            )
        else:
            self.loading_view.dismiss()
            self.dismiss()
            timedelta = licensing.calculate_days_remaining()
            App.get_running_app().root.current_screen.ids.days_remaining.text = (
                f"[color=ff0000][i]{timedelta.days} days remaining[/color][/i]"
                if timedelta.days > 2
                else f"[b]License will expire in {timedelta.days} day"
                "{'s' if timedelta.days!=1 else ''}.Buy a new one[/b]"
            )

    def load_loading_view_and_process_registration_data(
        self, license_key, token
    ):
        self.loading_view = Factory.LoadingModalView()
        self.loading_view.open()
        t = threading.Thread(
            target=self._process_license_key_and_token,
            args=(license_key, token),
        )
        t.start()
