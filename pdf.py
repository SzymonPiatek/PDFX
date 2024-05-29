from PyPDF2 import PdfReader
import os
import shutil
import ironpdf
from PIL import Image, ImageTk


class PDF:
    def __init__(self, file):
        self.path = file
        self.name = os.path.basename(self.path)[:-4]
        self.pages = 0
        self.current_page = 0
        self.size = 0
        self.image_paths = self.convert_pdf_to_images()

        self.check_pdf_info()

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, PDF):
            return self.path == other.path
        return False

    def show_info(self):
        return f'''
        Name: {self.name}\n
        Type: 'PDF'\n
        Path: {self.path}\n
        Pages: {self.pages}\n
        Size: {self.size} Mb\n
        '''

    def check_pdf_info(self):
        with open(self.path, "rb") as file:
            pdf_reader = PdfReader(file)
            self.pages = len(pdf_reader.pages)

        self.size = round(os.path.getsize(self.path) / (1024 * 1024), 2)

    def convert_pdf_to_images(self):
        pdf = ironpdf.PdfDocument.FromFile(self.path)
        folder_path = f"images/{self.name}"
        pdf.RasterizeToImageFiles(os.path.join(folder_path, "*.png"))
        image_paths = []

        for filename in os.listdir(folder_path):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                image_paths.append(os.path.join(folder_path, filename))
        return image_paths
