from PyPDF2 import PdfReader
import os
import shutil
import sys
import contextlib


with open(os.devnull, 'w') as devnull:
    with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
        import ironpdf


class PDF:
    def __init__(self, file):
        self.path = file
        self.name = os.path.basename(self.path)[:-4]
        self.type = "PDF"
        self.pages = 0
        self.current_page = 0
        self.size = round(os.path.getsize(self.path) / (1024 * 1024), 2)
        self.folder_path = f"images/{self.name}"
        self.image_paths = []

        self.check_pdf_info()
        self.convert_pdf_to_images()

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, PDF):
            return self.path == other.path
        return False

    def show_info(self):
        return f'''
        Name: {self.name}\n
        Type: PDF\n
        Path: {self.path}\n
        Pages: {self.pages}\n
        Size: {self.size} Mb\n
        '''

    def check_pdf_info(self):
        with open(self.path, "rb") as file:
            pdf_reader = PdfReader(file)
            self.pages = len(pdf_reader.pages)

    def convert_pdf_to_images(self):
        pdf = ironpdf.PdfDocument.FromFile(self.path)
        pdf.RasterizeToImageFiles(os.path.join(self.folder_path, "*.png"))

        for filename in os.listdir(self.folder_path):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                self.image_paths.append(os.path.join(self.folder_path, filename))

    def remove_files(self):
        shutil.rmtree(self.folder_path)
