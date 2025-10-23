import customtkinter

class ModMenu(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("500x550")
        self.title("")


if __name__ == "__main__":
    # For testing the window standalone
    root = customtkinter.CTk()
    root.withdraw()  # Hide the root window
    app = ModMenu(root)
    app.mainloop()