import tkinter as tk
from tkinter import filedialog, messagebox
from configure import configuration
from pdf import PDF


class Window(tk.Tk):
    def __init__(self, config):
        super().__init__()
        self.title(config["title"])
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        if config["test"]:
            self.geometry("800x800+0+0")
        else:
            if config["fullscreen"]:
                self.attributes('-fullscreen', True)
            else:
                self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
                self.state("zoomed")
                self.attributes("-fullscreen", False)

        self.create_menubar()

    def create_menubar(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Otwórz", command=self.load_pdf_file)
        file_menu.add_command(label="Zapisz", command=self.test)

        menubar.add_cascade(label="Plik", menu=file_menu)

        self.config(menu=menubar)

    def load_pdf_file(self):
        ask_pdf_file = filedialog.askopenfilename(title="Wybierz plik PDF", filetypes=(("Pliki PDF", "*.pdf"),))

        if ask_pdf_file:
            pdf_file = PDF(ask_pdf_file)
            print(pdf_file.show_info())

    def test(self):
        print("test")


if __name__ == "__main__":
    app = Window(config=configuration)
    app.mainloop()
