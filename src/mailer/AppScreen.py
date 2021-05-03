import csv
import plyer
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
import functools
import os


def get_open_file_path(extension, *args, **kwargs):
    chooser = plyer.filechooser
    ret = chooser.open_file(filters=[f"*.{extension}"])
    if ret and ret[0]:

        ret = (
            ret[0]
            if ret[0].endswith(f".{extension}")
            else ret[0] + f".{extension}"
        )
        return ret


def get_save_file_path(extension, *args, **kwargs):
    chooser = plyer.filechooser
    ret = chooser.save_file(filters=[f"*.{extension}"])
    if ret and ret[0]:
        ret = (
            ret[0]
            if ret[0].endswith(f".{extension}")
            else ret[0] + f".{extension}"
        )
        return ret


class AppScreen(Screen):
    pass


class FileInputComponent(BoxLayout):
    def on_kv_post(self, base_widget):
        self.ids.browse_button.bind(on_release=self.set_opened_file_path)

    def set_opened_file_path(self, *args, **kwargs):
        file_path = get_open_file_path("csv")

        if file_path:
            self.ids.file_path.text = file_path


class InfoArea(TextInput):
    """
    Textinput for a log window. Wouldn't allow you to type or use backspace.
    Only readonly or copy text. This is unlike the default `readonly` which disables everything.
    """

    def insert_text(self, substring, from_undo=False):
        return True

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[0] != 8:  # backspace
            return super().keyboard_on_key_down(
                window, keycode, text, modifiers
            )
        return True

    def update_info_area(self, text, *args, **kwargs):
        """Put updates in the log window"""
        self.text += "\n" + text

    def generate_and_save_report(self):
        file_path = get_save_file_path("txt")
        with open(file_path, "w") as f:
            f.write(self.text)


class TemplateCsvFileButton(Button):
    def _get_fake_data(self):
        app = App.get_running_app()
        return {
            app.config.get("templates", "From"): [
                "abc@gmail.com",
                "aghgh@gmail.com",
            ],
            app.config.get("templates", "To"): [
                "bfg@gmail.com, abcgh@gmail.com",
                "bjhjfg@gmail.com, abnbbcgh@gmail.com",
            ],
            app.config.get("templates", "Cc"): [
                "bfg@gmail.com, abcgh@gmail.com",
                "bjhjfg@gmail.com, abnbbcgh@gmail.com",
            ],
            app.config.get("templates", "Bcc"): [
                "bfg@gmail.com, abcgh@gmail.com",
                "bjhjfg@gmail.com, abnbbcgh@gmail.com",
            ],
            app.config.get("templates", "Subject"): [
                "Hi there",
                "Bye there",
            ],
            app.config.get("templates", "attachments"): [
                r"C:/Users/Dell/abc.txt,C:/Users/Dell/abc.zip",
                r"C:/Users/Dell/ahhbc.png,C:/Users/Dell/ahbc.zip",
            ],
            app.config.get("templates", "template_path"): [
                r"C:/Users/Dell/abc.docx",
                r"C:/Users/Dell/abfgc.docx",
            ],
            "IMG_1": [
                'image_descriptor = r"C:/Users/Dell/abc.jpg"',
                ' image_descriptor= r"C:/Users/Dell/ahgjbc.jpg"',
            ],
        }

    def on_kv_post(self, base_widget):
        self._fake_data = self._get_fake_data()

    def on_release(self):

        file_save_path = get_save_file_path("csv")

        if file_save_path:
            self._save_csv_file(file_save_path)

    def _save_csv_file(self, file_path):
        """ "Save the csv file based on `file_path`"""

        with open(file_path, "w", newline="") as outfile:

            writer = csv.writer(outfile)
            writer.writerow(self._fake_data.keys())
            writer.writerows(zip(*self._fake_data.values()))


class ProgressBarComponent(BoxLayout):
    """A class containing a progressbar with a counter"""

    def update_progressbar(self, counter, *args, **kwargs):
        """Update progressbar counter on gui"""
        self.ids.progressbar.value = counter

    def update_screen_progressvalue(self, counter, total_counts):
        """Update counter label sent on gui"""
        self.ids.progress_value.text = f"{counter} of {total_counts} done"


class ImageButton(Button):
    image_path = os.path.join(os.path.dirname(__file__), "imgs", "gear.png")
