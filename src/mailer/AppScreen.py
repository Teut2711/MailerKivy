import csv
import plyer
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput


class AppScreen(Screen):
    def update_info_area(self, text, *args, **kwargs):
        self.ids.info_area.text += "\n" + text

    def update_progressbar(self, counter, *args, **kwargs):
        self.ids.progressbar.value = counter

    def update_screen_progressvalue(self, counter, total_counts):
        self.ids.progress_value.text = f"{counter} of {total_counts} done"

    def show_file_select_dialog_and_set_file_path(self, *args, **kwargs):
        chooser = plyer.filechooser
        ret = chooser.open_file(filters=["*.csv"])
        if ret:
            self.ids.file_path.text = ret[0]

    def _make_and_save_csv_file(self, file_path):
        data = {
            App.get_running_app().config.get("templates", "From"): [
                "abc@gmail.com",
                "aghgh@gmail.com",
            ],
            App.get_running_app().config.get("templates", "To"): [
                "bfg@gmail.com, abcgh@gmail.com",
                "bjhjfg@gmail.com, abnbbcgh@gmail.com",
            ],
            App.get_running_app().config.get("templates", "Cc"): [
                "bfg@gmail.com, abcgh@gmail.com",
                "bjhjfg@gmail.com, abnbbcgh@gmail.com",
            ],
            App.get_running_app().config.get("templates", "Bcc"): [
                "bfg@gmail.com, abcgh@gmail.com",
                "bjhjfg@gmail.com, abnbbcgh@gmail.com",
            ],
            App.get_running_app().config.get("templates", "Subject"): [
                "Hi there",
                "Bye there",
            ],
            App.get_running_app().config.get("templates", "attachments"): [
                r"C:/Users/Dell/abc.txt,C:/Users/Dell/abc.zip",
                r"C:/Users/Dell/ahhbc.png,C:/Users/Dell/ahbc.zip",
            ],
            App.get_running_app().config.get("templates", "template_path"): [
                r"C:/Users/Dell/abc.docx",
                r"C:/Users/Dell/abfgc.docx",
            ],
            "IMG_1": [
                'image_descriptor = r"C:/Users/Dell/abc.jpg", width = 89 ,height= 67',
                ' image_descriptor= r"C:/Users/Dell/ahgjbc.jpg", width = 9 ,height= 7',
            ],
        }
        with open(
            file_path + ".csv" if not file_path.endswith(".csv") else "", "w"
        ) as outfile:

            writer = csv.writer(outfile)
            writer.writerow(data.keys())
            writer.writerows(zip(*data.values()))

    def show_dialog_and_save_starter_csv_file(self):
        chooser = plyer.filechooser
        ret = chooser.save_file(filters=["*.csv"])
        if ret:
            self._make_and_save_csv_file(file_path=ret[0])
            self.ids.file_path.text = (
                ret[0] + ".csv" if not ret[0].endswith(".csv") else ""
            )


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
