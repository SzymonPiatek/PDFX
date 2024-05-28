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

        self.pdf_files = []
        self.pdf_buttons = {}

        self.create_menubar()
        self.create_pdf_menubar()

    def create_menubar(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Otwórz", command=self.load_pdf_file)
        file_menu.add_command(label="Zapisz", command=self.test)

        menubar.add_cascade(label="Plik", menu=file_menu)

        self.config(menu=menubar)

    def create_pdf_menubar(self):
        self.pdf_menubar_frame = tk.Frame(self, bd=1, relief=tk.SUNKEN, pady=4)
        self.pdf_menubar_frame.pack(side=tk.TOP, fill=tk.X)

        self.create_none_pdf_label()

    def create_none_pdf_label(self):
        self.none_pdf_label = tk.Label(self.pdf_menubar_frame,
                                       text="Brak wybranych plików")
        self.none_pdf_label.pack(side=tk.LEFT)

    def load_pdf_file(self):
        ask_pdf_file = filedialog.askopenfilename(title="Wybierz plik PDF", filetypes=(("Pliki PDF", "*.pdf"),))

        if ask_pdf_file:
            pdf_file = PDF(ask_pdf_file)
            if pdf_file not in self.pdf_files:
                self.pdf_files.append(pdf_file)
                self.update_pdf_menubar()
            else:
                messagebox.showinfo("Informacja", "Ten plik PDF jest już na liście.")

    def update_pdf_menubar(self):
        if self.pdf_files:
            self.none_pdf_label.pack_forget()
        for file in self.pdf_files:
            if file.name not in self.pdf_buttons:
                frame = tk.Frame(self.pdf_menubar_frame)
                frame.pack(side=tk.LEFT, padx=2)

                button = tk.Button(frame, text=file.name, command=lambda: print(file.name))
                button.pack(side=tk.LEFT)

                close_button = tk.Button(frame, text="X", command=lambda file=file: self.remove_pdf_file(file))
                close_button.pack(side=tk.LEFT)

                self.pdf_buttons[file.name] = frame

    def remove_pdf_file(self, file):
        self.pdf_files.remove(file)
        self.pdf_buttons[file.name].destroy()
        del self.pdf_buttons[file.name]

        if not self.pdf_files:
            self.create_none_pdf_label()

    def test(self):
        print("test")


if __name__ == "__main__":
    app = Window(config=configuration)
    app.mainloop()
