import shutil
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
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
        self.current_pdf = None
        self.image_id = None

        self.create_temp_folder()
        self.create_menubar()
        self.create_pdf_menubar()
        self.create_pdf_canvas()
        self.create_pdf_functions_bar()

    def create_temp_folder(self):
        if os.path.exists("images"):
            shutil.rmtree("images")
        os.makedirs("images")

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

        if hasattr(self, "previous_page_button"):
            self.update_pdf_page_button()

    def create_pdf_canvas(self):
        self.pdf_canvas = tk.Canvas(self, background="#bdbdbd")
        self.pdf_canvas.pack(fill=tk.BOTH, expand=True)
        self.pdf_canvas_image = None

    def create_pdf_functions_bar(self):
        self.pdf_change_page_frame = tk.Frame(self)
        self.pdf_change_page_frame.pack(side=tk.BOTTOM)

        self.previous_page_button = tk.Button(master=self.pdf_change_page_frame,
                                              text="Poprzednia",
                                              command=lambda: self.change_pdf_page(-1),
                                              state="disabled")
        self.next_page_button = tk.Button(master=self.pdf_change_page_frame,
                                          text="Następna",
                                          command=lambda: self.change_pdf_page(1),
                                          state="disabled")

        self.previous_page_button.pack(side=tk.LEFT)
        self.next_page_button.pack(side=tk.RIGHT)

    def update_pdf_page_button(self):
        if self.current_pdf:
            if self.current_pdf.current_page == 0:
                self.previous_page_button.configure(state="disabled")
            else:
                self.previous_page_button.configure(state="normal")

            if self.current_pdf.current_page == self.current_pdf.pages - 1:
                self.next_page_button.configure(state="disabled")
            else:
                self.next_page_button.configure(state="normal")
        else:
            self.previous_page_button.configure(state="disabled")
            self.next_page_button.configure(state="disabled")

    def change_pdf_page(self, value):
        if self.current_pdf:
            if value == -1:
                if self.current_pdf.current_page == 0:
                    return
                else:
                    self.current_pdf.current_page -= 1
            else:
                if self.current_pdf.current_page == self.current_pdf.pages - 1:
                    return
                else:
                    self.current_pdf.current_page += 1

        self.update_pdf_page_button()

        self.display_pdf()

    def load_pdf_file(self):
        ask_pdf_file = filedialog.askopenfilename(title="Wybierz plik PDF", filetypes=(("Pliki PDF", "*.pdf"),))

        if ask_pdf_file:
            pdf_file = PDF(ask_pdf_file)
            self.current_pdf = pdf_file
            self.display_pdf()
            self.update_pdf_page_button()
            if pdf_file not in self.pdf_files:
                self.pdf_files.append(pdf_file)
                self.update_pdf_menubar()
            else:
                messagebox.showinfo("Informacja", "Ten plik PDF jest już na liście.")

    def display_pdf(self):
        if self.current_pdf:
            image_path = self.current_pdf.image_paths[self.current_pdf.current_page]
            img = Image.open(image_path)

            padding = 40

            pdf_width, pdf_height = img.size
            canvas_width = self.pdf_canvas.winfo_width() - padding
            canvas_height = self.pdf_canvas.winfo_height() - padding

            scale = min(canvas_width / pdf_width, canvas_height / pdf_height)
            scaled_width = int(pdf_width * scale)
            scaled_height = int(pdf_height * scale)

            img = img.resize((scaled_width, scaled_height))
            self.pdf_canvas_image = ImageTk.PhotoImage(img)

            self.delete_pdf_canvas_image()

            x_offset = (canvas_width - scaled_width) / 2
            y_offset = (canvas_height + padding - scaled_height) / 2
            self.image_id = self.pdf_canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=self.pdf_canvas_image)

    def update_pdf_menubar(self):
        if self.pdf_files:
            self.none_pdf_label.pack_forget()
        for file in self.pdf_files:
            if file.name not in self.pdf_buttons:
                frame = tk.Frame(self.pdf_menubar_frame)
                frame.pack(side=tk.LEFT, padx=2)

                button = tk.Button(frame, text=file.name, command=lambda file=file: self.switch_pdf(file))
                button.pack(side=tk.LEFT)

                close_button = tk.Button(frame, text="X", command=lambda file=file: self.remove_pdf_file(file))
                close_button.pack(side=tk.LEFT)

                self.pdf_buttons[file.name] = frame

    def delete_pdf_canvas_image(self):
        if self.image_id:
            self.pdf_canvas.delete(self.image_id)
            self.image_id = None

    def switch_pdf(self, pdf_file):
        self.current_pdf = pdf_file
        self.display_pdf()
        self.update_pdf_page_button()

    def remove_pdf_file(self, file):
        file.remove_files()
        self.pdf_files.remove(file)
        self.pdf_buttons[file.name].destroy()
        del self.pdf_buttons[file.name]
        self.current_pdf = None

        self.delete_pdf_canvas_image()

        if not self.pdf_files:
            self.create_none_pdf_label()
        else:
            self.switch_pdf(self.pdf_files[0])

    def on_closing(self):
        shutil.rmtree("images")
        self.destroy()

    def test(self):
        print("test")


if __name__ == "__main__":
    app = Window(config=configuration)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
