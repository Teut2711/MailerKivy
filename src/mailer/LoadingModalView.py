import functools
import subprocess
from datetime import datetime

import kivy.properties as P
from kivy.app import App
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.uix.modalview import ModalView

from mailer.license_exceptions import LicenseExpiredError, InvalidSystemIDError


class LoadingModalView(ModalView):
    time = P.NumericProperty(0)

    def on_open(self):
        Clock.schedule_interval(self.update_time, 0)

    def update_time(self, dt):

        self.time += dt
