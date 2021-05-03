import pytest
from mailer.License import Licensing
from mailer.license_exceptions import (
    InvalidCredentialsError,
    InvalidSystemIDError,
    RegistrationTimeExpiredError,
)


class TestRegistration:
    def test_new_registration_with_registration_credentials(self):
        licensing = Licensing(None, None)  # initialize with None
        with pytest.raises(RegistrationTimeExpiredError):

            licensing.register_new_user(
                "2xWmh_9qoLfZDMrh-MnHdDWWclfxz607cbZo5KF-2No=",
                "gAAAAABgeFZ2fHe3LocmLtqowyKwiZJ25s5B1FlwLd4_huWmoua0rggCz-8UMuGaP8rSy52ne5hSO6zL099DL3wNVUnuyLWKpT4q3i-fmM5EU72BJoC9EYbrGoajzpz0XfIvttirlMnv3vJtVupLSEwjZgfjUt-PW8TohjAGGO3RWiu6dapVmj0wJ30Bw7rpE-Mr8a5Dccq3cRbbnMsEfL2ZrEP8En53SepjCVhOevws4vD-Ibyklkem3sYtOySxTGfGtSHQk5W-rB-BezjKLWaKjqQWWMwzelZPcWVwFi3T_PnLKVqf2HT4Ar4YEYYIkJP8tmAOcWyR3Qa7SeNXCY_BMsHTKczgeT71y5el4vPdzeGqVvq0iEHkrpSwprNvBoipj4oFUVA933lsCjuIjoG3OvhVVELHeVFWHwo0SXGiwePznGeTPFlYusAP8xoP62cIoHJY20de8iSJewq6ECS-y15PYIXh0cV6_v7Gw3QmpTwwb3VOxoyLima7iBUJucfBUAGLM9IC05vPUm-8oIpkQx-pP2CuMUPqdRZC4JNb6XlNozyHAOB7OfCUWZC4JeNozpT-xYXz",
            )

    def test_new_registration_with_invalid_credentials(self):
        licensing = Licensing(None, None)
        with pytest.raises(InvalidCredentialsError):
            licensing.register_new_user(
                "6VI1-05m3lsNcI2UMdLlGPtJ-oQz-PYeUeYKaRKtXAA=",
                "gAAAAABgeCPvk5kFF8mxQEZxyIYUiGT8Wo_cq8tDe8pREi_PwNHWP9h4Cp7tTX4DG4-qYWiH4axwQo-Rgx4tKemQZd9ii5j8-bJtO9gPdTwe4Zh-PJGa63w57hXe6ORxrsZUXGrgSys-RByUmglFODr4MQQ4GLlfYJ21N0RTAKQwNBLyabko8PQo6Uj4UTUF6RAsF4YZUQiCmObfeWYqxbVbmokenHc0yotEdvOCyWUhEop4ToZWDOD6a7-KHcUEB6apqZqOSJhT1FsPzBPkWTwTLhQ_zGSbHc0_Vd7n6pw-46U-Nn8-qFAUueJdVnMS2mGj8lPu9lsrAFjr56MphMRFudKOrTzERX2VYglQh9npFEStVC0u7tPLJUm14hvnFK08Z6psmVWGZamEbDruiwBj-M7_Ad4OVk4VUxl_3UHmeJcavYeMb70WvwGmJB5HJjsVoc94KFcI7ZUl7ZVVDnhEbJJFQsfdyyPZmE5EpSxssvpztQuPowba3fsRa4uXhGfoqCw3WbKub7m6k5joGFsVcxjoCm4_LEsGDPaZKON1NAyTjXw6ZZJ5TsLZKoudZygh6onKd9B_",
            )

    def test_new_registration_with_invalid_system_id(self):
        licensing = Licensing(None, None)
        with pytest.raises(InvalidSystemIDError):
            licensing.register_new_user(
                "3nXXMJoCPVAMl6ZR-TJfLd66At-s2brtacPsDuGln6Q=",
                "gAAAAABgeqVj-hPFTqEtYcHh2Eo-d4TPrqtg0zgmwUd7G2JXmr2NmtR125Mj6POEYcPfv5Wxr61IsrdB1PFYaW9cwpP3OXEEj8jrXfAcXwvFvQ6nib2HaSmvSxA3B_BjITbWKHpTpfkckUR-IbHualCiX6Q-5WuP7sZMAqkyP8n2rTKq7uZbCKzHuzOWJaKCAoGgaALsGdbTWKeczVLCngWWFDsmEXrxsPbRJaI7A7qkDwAmxeDZvAbZBnGkQyqBbeepvjtvb-3LXHm8w-7nvnHuiaRQzv_-bVAmWgZtGp9URteLxi5UfVpvtPlk0QsmERBglthCY8_-sSf61mG5gz8t7WaxXOTmM4Jj5fCH5GIU8UmZBtx4W2-tDKZLz-64BMWpUQZLI171irx3_ZQNow0BLCLALj3uFicD1Qh9pPftreNqla-NCLfh7ctCi1PCdCI1W0aV134j1xJQLrVdUlk04dSxt4Dl3ws4DsLmroClIIo0EtRqDTNXTJKIvY4BfeHvPDSbTg37--gMnZpjj5BnfZpwouGO8ZjjGdB9urwf2xKqOqDoZjZM-lxjkHskVUSvvBcqlRqb",
            )


class TestValidity:
    @pytest.mark.xfail(reason="May fail due to date getting expired")
    def test_validate_credentials_with_valid_data(self):

        licensing = Licensing(None, None)  # initialize with None
        post_registration_data = licensing.register_new_user(
            "2xWmh_9qoLfZDMrh-MnHdDWWclfxz607cbZo5KF-2No=",
            "gAAAAABgeFZ2fHe3LocmLtqowyKwiZJ25s5B1FlwLd4_huWmoua0rggCz-8UMuGaP8rSy52ne5hSO6zL099DL3wNVUnuyLWKpT4q3i-fmM5EU72BJoC9EYbrGoajzpz0XfIvttirlMnv3vJtVupLSEwjZgfjUt-PW8TohjAGGO3RWiu6dapVmj0wJ30Bw7rpE-Mr8a5Dccq3cRbbnMsEfL2ZrEP8En53SepjCVhOevws4vD-Ibyklkem3sYtOySxTGfGtSHQk5W-rB-BezjKLWaKjqQWWMwzelZPcWVwFi3T_PnLKVqf2HT4Ar4YEYYIkJP8tmAOcWyR3Qa7SeNXCY_BMsHTKczgeT71y5el4vPdzeGqVvq0iEHkrpSwprNvBoipj4oFUVA933lsCjuIjoG3OvhVVELHeVFWHwo0SXGiwePznGeTPFlYusAP8xoP62cIoHJY20de8iSJewq6ECS-y15PYIXh0cV6_v7Gw3QmpTwwb3VOxoyLima7iBUJucfBUAGLM9IC05vPUm-8oIpkQx-pP2CuMUPqdRZC4JNb6XlNozyHAOB7OfCUWZC4JeNozpT-xYXz",
        )
