import codecs
import copy
import mimetypes
import os
import pathlib
import tempfile
from email.message import EmailMessage
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from os.path import basename, splitext
from datetime import datetime

import bs4
from docxtpl import DocxTemplate, InlineImage
from win32com import client as wc
from kivy.app import App
from mailer.mailing_exceptions import FromError, SubjectError, ToError


def validate_email(email):
    # NOT IMPLEMENTED:
    return email


class PrepMessage:
    def __init__(self):
        self.email_message = EmailMessage()
        self.templates = {}
        self.html_file_path = None

    def _get_template(self, template_path):

        try:
            return copy.deepcopy(self.templates[template_path])
        except KeyError:
            with open(template_path, "rb") as f:
                self.templates[template_path] = DocxTemplate(f)

            return self.templates[template_path]

    def __setitem__(self, name, val, *args, **kwargs):
        if name == "To":

            self.email_message["To"] = self._get_formatted_multiple_emails(val)
        elif name == "Subject":

            self.email_message["Subject"] = self._get_formatted_subject(val)

        elif name == "From":
            self.email_message["From"] = self._get_formatted_from(val)

        elif name == "Cc":
            self.email_message["Cc"] = self._get_formatted_multiple_emails(val)

        elif name == "Bcc":
            self.email_message["Bcc"] = self._get_formatted_multiple_emails(
                val
            )

    def _get_formatted_subject(self, subject):
        subject = subject.strip()
        if not subject:
            raise SubjectError
        return subject

    def _get_formatted_from(self, from_):
        from_ = from_.strip()
        validate_email(from_)
        return from_

    def _get_formatted_multiple_emails(self, comma_sep_vals):
        return ", ".join(
            [
                i.strip()
                for i in comma_sep_vals.split(",")
                if validate_email(i.strip())
            ]
        )

    def add_attachments(self, attachments):
        for file_ in [i.strip() for i in attachments.split(",") if i.strip()]:

            if os.path.exists(file_):
                with open(file_, "rb") as fp:
                    file_name = pathlib.Path(file_).name
                    maintype, subtype = self._get_mime(file_name).split("/")
                    self.email_message.add_attachment(
                        fp.read(),
                        maintype=maintype,
                        subtype=subtype,
                        filename=file_name,
                    )

    def _convert_docx_to_other_and_save_to_disk(
        self, docx_bytes_io, extension, enumeration
    ):

        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

        temporary_directory_path = tempfile.mkdtemp(
            prefix="tempdir-", suffix=dt_string
        )

        with open(
            os.path.join(temporary_directory_path, "word_template.docx"), "wb"
        ) as docx:
            docx.write(docx_bytes_io.getvalue())

        word = wc.Dispatch("Word.Application")
        doc = word.Documents.Open(
            os.path.join(temporary_directory_path, "word_template.docx")
        )
        doc.SaveAs(
            os.path.join(
                temporary_directory_path, f"word_template_filled.{extension}"
            ),
            enumeration,
        )

        doc.Close()
        word.Quit()
        self.html_file_path = os.path.join(
            temporary_directory_path, f"word_template_filled.{extension}"
        )
        return self.html_file_path

    def add_message(self, docx_template_path, context):
        template = self._get_template(docx_template_path)
        context = self._put_images_into_context(template, context)
        template.render(context)
        target_stream = BytesIO()
        template.save(target_stream)
        self._add_plain_text_message(target_stream)
        self._add_html_message(target_stream)

    def _add_plain_text_message(self, stream):

        with open(
            self._convert_docx_to_other_and_save_to_disk(stream, "txt", 2)
        ) as fp:
            text = fp.read()
        msgAlternative = MIMEMultipart("alternative")

        msgAlternative.attach(MIMEText(text, _charset="utf-8"))
        self.email_message.attach(msgAlternative)

    def _add_html_message(self, stream):

        with codecs.open(
            self._convert_docx_to_other_and_save_to_disk(stream, "html", 10)
        ) as fp:
            html = fp.read()
        html = self._put_images_in_email_message(html)
        msgAlternative = MIMEMultipart("alternative")

        msgAlternative.attach(
            MIMEText(html, _subtype="html", _charset="utf-8")
        )
        self.email_message.attach(msgAlternative)

    def _put_images_into_context(self, template, context):

        image_initial = App.get_running_app().config.get(
            "templates", "image_initial"
        )
        for k in list(context.keys()):
            if k.startswith(image_initial):
                image_attribs = dict(
                    [
                        [j.strip().strip("\"\'").strip()
                         for j in i.strip().split("=")]
                        for i in context[k].split(",")
                    ]
                )
                image_attribs = {
                    "image_descriptor": image_attribs.get("path", None),
                    "width": int(image_attribs.get("width", None))
                    if image_attribs.get("width", None)
                    else None,
                    "height": int(image_attribs.get("height", None))
                    if image_attribs.get("height", None)
                    else None,
                }

                if "image_descriptor" in image_attribs and os.path.exists(
                    image_attribs["image_descriptor"]
                ):
                    context[k] = InlineImage(template, **image_attribs)
                else:
                    context.pop(k)
        return context

    def _put_images_in_email_message(self, html_string):
        def get_image_path(html_path, img): return os.path.join(
            os.path.splitext(html_path)[0] + "_files",
            os.path.basename(img["src"]),
        )

        soup = bs4.BeautifulSoup(html_string, "lxml")

        for k, img in enumerate(soup.find_all("img")):
            image_name = splitext(basename(img["src"]))[0]
            with open(get_image_path(self.html_file_path, img), "rb") as fp:
                msgImage = MIMEImage(fp.read())

            img["src"] = "cid:" + f"{image_name}{k}"
            msgImage.add_header("Content-ID", f"<{image_name}{k}>")
            self.email_message.attach(msgImage)

        return str(soup)

    def _get_mime(self, path):
        mime = mimetypes.guess_type(path)[0]
        if mime:
            return mime
        elif path.endswith(".rar"):
            return "application/x-rar-compressed"
        else:
            raise TypeError("Filetype not supported invalid")
