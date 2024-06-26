import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from configure import configuration
from pdf import PDF, merge_pdf_files_return
from functions import on_closing, create_temp_folder


class Window(tk.Tk):
    def __init__(self, config):
        super().__init__()
        self.cnfg = config
        self.title(self.cnfg["title"])
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        if self.cnfg["test"]:
            self.geometry("1200x800+1920+0")
        else:
            if not self.cnfg["fullscreen"]:
                self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
                self.state("zoomed")
            self.attributes("-fullscreen", self.cnfg["fullscreen"])

        self.pdf_files = []
        self.pdf_merge_files = []
        self.pdf_buttons = {}
        self.current_pdf = None
        self.image_id = None

        create_temp_folder()
        self.create_layout()

    def create_layout(self):
        self.configure(bg=self.cnfg["background_color"])

        self.top_frame = tk.Frame(master=self)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.bottom_frame = tk.Frame(master=self)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.left_frame = tk.Frame(master=self, bg=self.cnfg["background_color"])
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(master=self, padx=20)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.right_frame.pack_propagate(False)

        self.create_menubar()
        self.create_pdf_menubar()
        self.create_pdf_canvas()
        self.create_pdf_info_frame()
        self.create_pdf_merge_frame()
        self.create_pdf_functions_bar()

    def create_menubar(self):
        menubar = tk.Menu(master=self.top_frame)

        file_menu = tk.Menu(master=menubar, tearoff=0)
        file_menu.add_command(label="Otwórz", command=self.load_pdf_file)

        menubar.add_cascade(label="Plik", menu=file_menu)

        self.config(menu=menubar)

    def create_pdf_menubar(self):
        self.pdf_menubar_container = tk.Frame(master=self.top_frame)
        self.pdf_menubar_container.pack(side=tk.TOP, fill=tk.X)

        self.pdf_menubar_canvas = tk.Canvas(master=self.pdf_menubar_container,
                                            bd=0,
                                            highlightthickness=0,
                                            bg=self.cnfg["second_color"])
        self.pdf_menubar_canvas.pack(side=tk.TOP, fill=tk.X, expand=True)

        self.pdf_menubar_scrollbar = tk.Scrollbar(master=self.pdf_menubar_container,
                                                  orient=tk.HORIZONTAL,
                                                  command=self.pdf_menubar_canvas.xview)
        self.pdf_menubar_scrollbar.pack(side=tk.TOP, fill=tk.X, expand=True)

        self.pdf_menubar_frame = tk.Frame(master=self.pdf_menubar_canvas, bd=1, relief=tk.SUNKEN, pady=4)
        self.pdf_menubar_frame.bind("<Configure>", self.update_pdf_menubar_scrollregion)

        self.pdf_menubar_canvas.configure(xscrollcommand=self.pdf_menubar_scrollbar.set)
        self.pdf_menubar_canvas.create_window((0, 0), window=self.pdf_menubar_frame, anchor=tk.NW)

        self.create_none_pdf_label()

    def create_pdf_info_frame(self):
        self.pdf_info_frame = tk.Frame(master=self.right_frame, padx=4, pady=4)
        self.pdf_info_frame.pack(side=tk.TOP, fill=tk.BOTH)

        self.pdf_info_label = tk.Label(master=self.pdf_info_frame, text="Właściwości")
        self.pdf_info_label.pack(side=tk.TOP, fill=tk.BOTH)

        self.pdf_info_table = ttk.Treeview(master=self.pdf_info_frame,
                                           columns=("Właściwość", "Wartość"),
                                           show="headings",
                                           height=5)
        self.pdf_info_table.pack(side=tk.TOP, fill=tk.BOTH)

        self.pdf_info_table.heading("Właściwość", text="Właściwość")
        self.pdf_info_table.heading("Wartość", text="Wartość")

        self.pdf_info_table.column("Właściwość", width=80)
        self.pdf_info_table.column("Wartość", width=250)

        self.update_pdf_info()

    def create_pdf_merge_frame(self):
        self.pdf_merge_frame = tk.Frame(master=self.right_frame, padx=4, pady=4)
        self.pdf_merge_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.pdf_merge_label = tk.Label(self.pdf_merge_frame, text="Scal pliki")
        self.pdf_merge_label.pack(side=tk.TOP)

        self.pdf_merge_list = tk.Listbox(master=self.pdf_merge_frame,
                                         selectmode=tk.SINGLE,
                                         exportselection=False,
                                         relief=tk.SOLID,
                                         height=10,
                                         takefocus=True)
        self.pdf_merge_list.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.pdf_merge_button = tk.Button(master=self.pdf_merge_frame,
                                          text="Połącz pliki",
                                          command=lambda: self.merge_pdf_files(self.pdf_merge_files))
        self.pdf_merge_button.pack(side=tk.BOTTOM, fill=tk.BOTH)

    def create_none_pdf_label(self):
        self.none_pdf_frame = tk.Frame(master=self.pdf_menubar_frame, borderwidth=0)
        self.none_pdf_frame.pack(side=tk.LEFT, padx=4, fill=tk.BOTH, expand=True)

        self.none_pdf_button = tk.Button(master=self.none_pdf_frame,
                                         text="Wgraj plik",
                                         command=lambda: self.load_pdf_file(),
                                         padx=20)
        self.none_pdf_button.pack()

        if hasattr(self, "previous_page_button"):
            self.update_pdf_page_button()

    def create_pdf_canvas(self):
        self.pdf_canvas = tk.Canvas(master=self.left_frame, bg=self.cnfg["background_color"])
        self.pdf_canvas.pack(fill=tk.BOTH, expand=True)
        self.pdf_canvas_image = None

    def create_pdf_functions_bar(self):
        self.pdf_functions_frame = tk.Frame(master=self.bottom_frame)
        self.pdf_functions_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.pdf_change_page_frame = tk.Frame(master=self.pdf_functions_frame)
        self.pdf_change_page_frame.pack(side=tk.LEFT)

        self.previous_page_button = tk.Button(master=self.pdf_change_page_frame,
                                              text="Poprzednia",
                                              command=lambda: self.change_pdf_page(-1),
                                              state="disabled")
        self.next_page_button = tk.Button(master=self.pdf_change_page_frame,
                                          text="Następna",
                                          command=lambda: self.change_pdf_page(1),
                                          state="disabled")
        self.page_info_label = tk.Label(master=self.pdf_functions_frame,
                                        text="")

        self.previous_page_button.pack(side=tk.LEFT)
        self.next_page_button.pack(side=tk.RIGHT)
        self.page_info_label.pack(side=tk.RIGHT)

    def update_pdf_menubar_scrollregion(self, event):
        self.pdf_menubar_canvas.configure(scrollregion=self.pdf_menubar_canvas.bbox("all"))
        self.pdf_menubar_canvas.update_idletasks()
        canvas_height = self.pdf_menubar_frame.winfo_height()
        self.pdf_menubar_canvas.configure(height=canvas_height)

    def update_pdf_page_button(self):
        if self.current_pdf:
            first_page = self.current_pdf.current_page == 0
            last_page = self.current_pdf.current_page == self.current_pdf.pages - 1

            self.previous_page_button.configure(state="disabled" if first_page else "normal")
            self.next_page_button.configure(state="disabled" if last_page else "normal")
            self.page_info_label.configure(
                text=f"Strona {self.current_pdf.current_page + 1} z {self.current_pdf.pages}")
        else:
            self.previous_page_button.configure(state="disabled")
            self.next_page_button.configure(state="disabled")
            self.page_info_label.configure(text="")

    def change_pdf_page(self, value):
        if self.current_pdf:
            self.current_pdf.current_page = max(0,
                                                min(self.current_pdf.pages - 1, self.current_pdf.current_page + value))

        self.update_pdf_page_button()

        self.display_pdf()

    def update_pdf_info(self):
        for row in self.pdf_info_table.get_children():
            self.pdf_info_table.delete(row)

        pdf_name = self.current_pdf.name if self.current_pdf else ""
        pdf_type = self.current_pdf.type if self.current_pdf else ""
        pdf_path = self.current_pdf.path if self.current_pdf else ""
        pdf_pages = self.current_pdf.pages if self.current_pdf else ""
        pdf_size = f"{self.current_pdf.size} Mb" if self.current_pdf else ""

        self.pdf_info_table.insert("", "end", values=("Nazwa", pdf_name))
        self.pdf_info_table.insert("", "end", values=("Typ", pdf_type))
        self.pdf_info_table.insert("", "end", values=("Ścieżka", pdf_path))
        self.pdf_info_table.insert("", "end", values=("Ilość stron", pdf_pages))
        self.pdf_info_table.insert("", "end", values=("Rozmiar pliku", pdf_size))

    def load_pdf_file(self):
        ask_pdf_file = filedialog.askopenfilename(title="Wybierz plik PDF", filetypes=(("Pliki PDF", "*.pdf"),))

        if ask_pdf_file:
            pdf_file = PDF(ask_pdf_file)
            self.current_pdf = pdf_file
            self.display_pdf()
            self.update_pdf_page_button()
            self.update_pdf_info()
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

            x_offset = (canvas_width + padding - scaled_width) / 2
            y_offset = (canvas_height + padding / 2 - scaled_height) / 2
            self.image_id = self.pdf_canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=self.pdf_canvas_image)

    def update_pdf_menubar(self):
        if self.pdf_files:
            self.none_pdf_frame.destroy()
        for file in self.pdf_files:
            if file.name not in self.pdf_buttons:
                frame = tk.Frame(master=self.pdf_menubar_frame, borderwidth=0)
                frame.pack(side=tk.LEFT, padx=4)

                button = tk.Button(master=frame,
                                   text=file.name,
                                   command=lambda file=file: self.switch_pdf(file),
                                   padx=20,
                                   relief=tk.FLAT)
                button.pack(side=tk.LEFT)

                plus_button = tk.Button(master=frame,
                                        text="+",
                                        command=lambda file=file: self.add_pdf_file_to_merge(file),
                                        padx=4)
                plus_button.pack(side=tk.LEFT)

                close_button = tk.Button(master=frame,
                                         text="X",
                                         command=lambda file=file: self.remove_pdf_file(file),
                                         padx=4)
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
        self.update_pdf_info()

    def add_pdf_file_to_merge(self, file):
        if file not in self.pdf_merge_files:
            self.pdf_merge_files.append(file)
            index = self.pdf_merge_files.index(file)
            self.pdf_merge_list.insert(tk.END, f"{index}. {file.name}")

    def update_pdf_merge_list(self):
        self.pdf_merge_list.delete(0, tk.END)
        for index, file in enumerate(self.pdf_merge_files):
            self.pdf_merge_list.insert(tk.END, f"{index}. {file.name}")

    def remove_pdf_file(self, file):
        file.remove_files()
        self.pdf_files.remove(file)
        self.pdf_buttons[file.name].destroy()
        del self.pdf_buttons[file.name]
        self.current_pdf = None

        self.delete_pdf_canvas_image()

        if not self.pdf_files:
            self.create_none_pdf_label()
            self.update_pdf_info()
        else:
            self.switch_pdf(self.pdf_files[0])

    def merge_pdf_files(self, pdf_merge_files):
        if pdf_merge_files:
            result = merge_pdf_files_return(pdf_merge_files)

            if result:
                messagebox.showinfo("Informacja", "Pliki PDF zostały połączone")
                self.pdf_merge_files = []
                self.pdf_merge_list.delete(0, tk.END)


if __name__ == "__main__":
    app = Window(config=configuration)
    app.protocol("WM_DELETE_WINDOW", lambda: on_closing(app))
    app.mainloop()
