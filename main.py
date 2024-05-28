import tkinter as tk
from configure import configuration


class Window(tk.Tk):
    def __init__(self, config):
        super().__init__()
        self.title(config["title"])
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        if config["fullscreen"]:
            self.attributes('-fullscreen', True)
        else:
            self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
            self.state('zoomed')
            self.attributes('-fullscreen', False)

        self.create_menu()

    def create_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Otwórz", command=self.test)
        file_menu.add_command(label="Zapisz", command=self.test)

        menubar.add_cascade(label="Plik", menu=file_menu)

        self.config(menu=menubar)

    def test(self):
        print("test")


if __name__ == "__main__":
    app = Window(config=configuration)
    app.mainloop()
