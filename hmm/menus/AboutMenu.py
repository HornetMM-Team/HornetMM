import customtkinter as ctk


class AboutMenu(ctk.CTkToplevel):
    """About Menu for HornetMM Application"""
    def __init__(self, parent):
        super().__init__(parent)
        self.withdraw()
        self.geometry("300x200")
        self.title("About HornetMM")
        self.deiconify()

        self.label = ctk.CTkLabel(self, text="HornetMM\nVersion 1.0\n© 2024 HornetMM Team")
        self.label.pack(pady=20)

        self.close_button = ctk.CTkButton(self, text="Close", command=self.close)
        self.close_button.pack(pady=10)

    def close(self):
        self.withdraw()

    def show_again(self):
        self.deiconify()
if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()
    app = AboutMenu(root)
    app.deiconify()
    app.mainloop()