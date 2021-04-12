import base64
import json
from datetime import datetime

from cryptography.fernet import Fernet
from dateutil.relativedelta import relativedelta

from mailer.license_exceptions import RegistrationTimeExpiredError


class Registration:
    def register_new_user(self, license_key, token):

        self.license_key = license_key
        self.token = token
        try:
            new_token = self._create_new_token()
        except RegistrationTimeExpiredError:
            raise RegistrationTimeExpiredError
        else:
            return {"license_key": self.license_key, "token": new_token}

    def _create_new_token(self):
        self.decrypted_data = self._decode_data()

        self._check_system_id(self.decrypted_data["system_id"])

        self._check_registration_time_not_expired(
            self.decrypted_data["registration_period"], self.current_datetime
        )

        new_token = self._get_new_token()

        return new_token

    def _get_new_token(self):
        encrypter = Fernet(self.license_key.encode("utf-8"))

        end_date = datetime.isoformat(
            datetime.fromisoformat(self.current_datetime)
            + relativedelta(
                years=self.decrypted_data["validity_period"]["years"],
                months=self.decrypted_data["validity_period"]["months"],
            )
        )

        new_token = encrypter.encrypt(
            self._get_base64_encoded_json_token(end_date)
        ).decode("utf-8")

        return new_token

    def _get_base64_encoded_json_token(self, end_date):
        return base64.b64encode(
            json.dumps(
                {
                    "license_key": self.decrypted_data["license_key"],
                    "system_id": self.decrypted_data["system_id"],
                    "start_datetime": self.current_datetime,
                    "end_datetime": end_date,
                }
            ).encode("utf-8")
        )
