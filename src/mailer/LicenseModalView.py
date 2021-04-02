from dateutil.relativedelta import relativedelta
from cryptography.fernet import Fernet
from mailer.utils import decode_data 
from mailer.license_exceptions import RegistrationTimeExpiredError
import json
import datetime
import subprocess
from kivy.network.urlrequest import UrlRequest
from kivy.app import App
import functools
from kivy.uix.modalview import ModalView

class LicenseModalView(ModalView):
    def _get_new_token(self, decrypted_data, current_time):
        
        f = Fernet(decrypted_data["license_key"])
        new_token = f.encrypt(
            json.dumps(
                {   "license_key":decrypted_data["license_key"], 
                    "system_id": decrypted_data["system_id"],
                    "start_date": current_time,
                    "end_date": datetime.isoformat(relativedelta(
                        years=decrypted_data["validity_period"]["years"],
                        months=decrypted_data["validity_period"]["months"],
                    )
                    + datetime.fromisoformat(current_time)),
                }
            ).encode("utf-8")
        ).decode("utf-8")
        return new_token

    def _save_attributes(self, decrypted_data, req, result):
            
        try:
            if not(
                datetime.fromisoformat(decrypted_data["registration_start_time"])
                < datetime.fromisoformat(result["datetime"])
                < datetime.fromisoformat(decrypted_data["registration_end_time"])
            ):
                raise RegistrationTimeExpiredError
        except RegistrationTimeExpiredError as e:
           
            self.ids.error_message_license.text = "[color=ff0000][b]{message.e}[/b][/color]"      
        else:     
            App.get_running_app().config.set(
                "licensing", "license_key", decrypted_data["license_key"]
            )
            App.get_running_app().config.set(
                "licensing",
                "token",
                self._get_new_token(decrypted_data, result["datetime"])
            )
            App.get_running_app().config.write()

            self.dismiss()

    def _put_error_message(self, res, result):

        self.ids.error_message_license.text = "[color=ff0000][b]Invalid license key or token. Please enter again.[/b][/color]"
        
            
    def register_credentials_and_save_to_json(self, license_key, token):
    
        decrypted_data = decode_data({"license_key": license_key, "token": token})

        if decrypted_data:
            system_id = (
                subprocess.check_output("wmic csproduct get uuid")
                .decode("utf-8")
                .split("\n")[1]
                .strip()
            )
            if decrypted_data["system_id"] == system_id:
                
                UrlRequest( "http://worldtimeapi.org/api/timezone/Asia/Kolkata",
                           on_success= functools.partial(self._save_attributes,decrypted_data),
                           on_failure=self._put_error_message ) 
