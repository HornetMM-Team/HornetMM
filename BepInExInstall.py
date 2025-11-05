import requests
import customtkinter
import zipfile
import platform

arch = platform.architecture()[0]
os = platform.system().lower()




class BepInExMenu(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("400x200")
        self.title("BepInEx Installer")

        self.label = customtkinter.CTkLabel(self, text="Install BepInEx for Hollow Knight")
        self.label.pack(pady=10)

        self.install_button = customtkinter.CTkButton(self, text="Install BepInEx", command=self.install_bepinex)
        self.install_button.pack(pady=10)

    def install_bepinex(self):
            
        # find os and get correct name for bepinex download
        if os == "windows":
            osbep = "win"
        elif os == "darwin":
            osbep = "macos"
        elif os == "linux":
            osbep = "linux"

        if arch == "64bit":
            beparch = "x64"
        elif arch == "32bit":
            beparch = "x86"

        # type:ignore just tells pylance to sybau and stop bitching


        chunk_size = 623 * 1024
        urlbep = rf"https://github.com/BepInEx/BepInEx/releases/download/v5.4.23.4/BepInEx_{osbep}_{beparch}_5.4.23.4.zip" #type:ignore
        urlmono = rf"https://github.com/MonoMod/MonoMod/releases/download/v22.07.31.01/MonoMod-22.07.31.01-net50.zip"
        bep = requests.get(urlbep, stream=True) 
        total_size = int(bep.headers['content-length'])


        self.progress = customtkinter.CTkProgressBar(self, width=360)
        self.progress.pack(pady=10, padx=20)
        

            with open("bepinex.zip", "wb") as f:
                for data in self.progress(): #type:ignore
                    
                    

if __name__ == "__main__":
    smth = customtkinter.CTk()
    smth.withdraw()
    app = BepInExMenu(smth)
    app.mainloop()






