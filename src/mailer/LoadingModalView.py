import kivy.properties as P
from kivy.clock import Clock
from kivy.uix.modalview import ModalView


class LoadingModalView(ModalView):
    time = P.NumericProperty(0)

    def on_open(self):
        Clock.schedule_interval(self.update_time, 0)

    def update_time(self, dt):
        self.time += dt
