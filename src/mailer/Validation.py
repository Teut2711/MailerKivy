from datetime import datetime

from kivy.logger import Logger

from mailer.license_exceptions import (
    LicenseExpiredError,
    UserNotRegisteredError,
)


class Validation:
    def validate_license_data(self, license_key, token):

        self.license_key = license_key
        self.token = token
        if not self.license_key and not self.token:
            raise UserNotRegisteredError
        self.decrypted_data = self._decode_data()

        self._check_system_id(self.decrypted_data["system_id"])
        Logger.debug(self.decrypted_data)
        self._check_license_expired(
            self.decrypted_data["start_datetime"],
            self.decrypted_data["end_datetime"],
        )

    def _check_license_expired(self, start_datetime, end_datetime):
        if not (start_datetime <= self.current_datetime <= end_datetime):
            raise LicenseExpiredError

    def calculate_days_remaining(self):

        return datetime.fromisoformat(
            self.decrypted_data["end_datetime"]
        ) - datetime.fromisoformat(self.current_datetime)
