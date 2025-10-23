import customtkinter
from pathlib import Path
from tkinter import filedialog
import json
import os

current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent

class Settings(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.withdraw()
        self.geometry("400x330")
        self.title("Settings")

        icon_path = root_dir / "icon.ico"
        if icon_path.exists():
            self.iconbitmap(icon_path)
        else:
            print("Icon file not found, skipping icon.")

        self.label = customtkinter.CTkLabel(self, text="Settings:")
        self.label.pack(pady=10)

        self.about_button = customtkinter.CTkButton(self, text="Open About Menu")
        self.about_button.pack(pady=10)

        # Create the button here in __init__, not inside the method
        self.change_hollow_path_button = customtkinter.CTkButton(
            self, text="Change hollow knight path", command=self.change_hollow_path
        )
        self.change_hollow_path_button.pack(pady=10)

    def change_hollow_path(self):
        new_path = filedialog.askdirectory(title="Change Current Path")
        if new_path:
            settings_file = os.path.join(root_dir, "settings.json")
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            settings['hollowknightpath'] = new_path
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            print(f"Hollow Knight path changed to: {new_path}")

    def show_again(self):
        self.deiconify()


if __name__ == "__main__":
    root = customtkinter.CTk()
    root.withdraw()
    app = Settings(root)
    app.deiconify()
    app.mainloop()
