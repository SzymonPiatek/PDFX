import shutil
import os


def on_closing(app):
    shutil.rmtree("images")
    app.destroy()


def create_temp_folder():
    if os.path.exists("images"):
        shutil.rmtree("images")
    os.makedirs("images")
