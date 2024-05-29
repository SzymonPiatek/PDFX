from PyPDF2 import PdfReader
import os


class PDF:
    def __init__(self, file):
        self.path = file
        self.name = os.path.basename(self.path) if self.path else ""
        self.pages = 0
        self.current_page = 0
        self.size = 0

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
        Path: {self.path}\n
        Pages: {self.pages}\n
        Size: {self.size} Mb\n
        '''

    def check_pdf_info(self):
        with open(self.path, "rb") as file:
            pdf_reader = PdfReader(file)
            self.pages = len(pdf_reader.pages)

        self.size = round(os.path.getsize(self.path) / (1024 * 1024), 2)
