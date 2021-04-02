import functools
import subprocess
from datetime import datetime

import kivy.properties as P
from kivy.app import App
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.uix.modalview import ModalView

from mailer.license_exceptions import LicenseKeyExpiredError, InvalidSystemIDError
from mailer.utils import decode_data


class LoadingModalView(ModalView):
    time = P.NumericProperty(0)

    def on_open(self):
        Clock.schedule_interval(self.update_time, 0)
        self._is_license_valid()

    def _failure(self, decrypted_data, req, result):

        timedelta = datetime.fromisoformat(
            decrypted_data["end_date"]
        ) - datetime.fromisoformat(datetime.now().isoformat() + "+05:30")
        try:
            if timedelta.seconds < 0:
                raise LicenseKeyExpiredError

        except LicenseKeyExpiredError as e:

            self.ids.error_message_license.text = (
                f"[color=ff0000][b]{e.message}.[/b][/color]"
            )
        else:
            App.get_running_app().root.current_screen.ids.days_remaining.text = (
                f"[color=ff0000][i]{timedelta.days} days remaining[/color][/i]"
                if timedelta.days > 0
                else "License will expire today.Buy a new one"
            )
            self.dismiss()

    def _success(self, decrypted_data, req, result):
        timedelta = datetime.fromisoformat(
            decrypted_data["end_date"]
        ) - datetime.fromisoformat(result["datetime"])
        try:
            if timedelta.seconds < 0:
                raise LicenseKeyExpiredError

        except LicenseKeyExpiredError as e:

            self.ids.error_message_license.text = (
                f"[color=ff0000][b]{e.message}.[/b][/color]"
            )
        else:
            App.get_running_app().root.current_screen.ids.days_remaining.text = (
                f"[color=ff0000][i]{timedelta.days} days remaining[/color][/i]"
                if timedelta.days > 0
                else "[b]License will expire today.Buy a new one[/b]"
            )

            self.dismiss()

    def _is_license_valid(self):

        data = {
            "license_key": App.get_running_app().config.get("licensing", "license_key"),
            "token": App.get_running_app().config.get("licensing", "token"),
        }
        decrypted_data = decode_data(data)

        try:

            system_id = (
                subprocess.check_output("wmic csproduct get uuid")
                .decode("utf-8")
                .split("\n")[1]
                .strip()
            )
            if decrypted_data["system_id"] != system_id:
                raise InvalidSystemIDError

        except InvalidSystemIDError as e:
            self.ids.error_message_license.text = (
                f"[color=ff0000][b]{e.message}.[/b][/color]"
            )

        UrlRequest(
            "http://worldtimeapi.org/api/timezone/Asia/Kolkata",
            on_success=functools.partial(self._success, decrypted_data),
            on_failure=functools.partial(self._failure, decrypted_data),
        )

    def update_time(self, dt):

        self.time += dt
