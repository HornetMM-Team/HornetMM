import requests #type:ignore
import customtkinter 
import zipfile
import platform
import os
import rootpath
import threading
import shutil

arch = platform.architecture()[0]
curos = platform.system().lower()
bepinex_dir = os.path.abspath(os.sep)


class BepInExMenu(customtkinter.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("BepInEx Installer")
        self.geometry("400x500")

        # Button
        self.install_button = customtkinter.CTkButton(
            self,
            text="Install BepInEx",
            command=self.download_bepinex
        )
        self.install_button.pack(pady=10)

        # Log box
        self.log = customtkinter.CTkTextbox(self, width=360, height=250)
        self.log.pack(pady=10, padx=20)
        self.log.configure(state="disabled")

        # Progress bar
        self.progress = customtkinter.CTkProgressBar(
            self, orientation="horizontal", mode="determinate", width=360
        )
        self.progress.pack(pady=10)
        self.progress.set(0)

        # Detect OS + architecture
        curos = platform.system().lower()
        arch = platform.architecture()[0]

        if "windows" in curos:
            self.osbep = "win"
        elif "darwin" in curos:
            self.osbep = "macos"
        elif "linux" in curos:
            self.osbep = "linux"
        else:
            self.osbep = "unknown"

        if self.osbep == "unknown":
            self.log_message("❌ Unsupported OS detected.")
            self.install_button.configure(state="disabled")

        self.beparch = "x64" if "64" in arch else "x86"

        if self.beparch == "x86":
            self.log_message("❌ Unsupported architecture detected.")
            self.install_button.configure(state="disabled")

    def log_message(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.configure(state="disabled")
        self.log.see("end")

    def download_bepinex(self):
            urlbep = rf"https://github.com/BepInEx/BepInEx/releases/download/v5.4.23.4/BepInEx_{self.osbep}_{self.beparch}_5.4.23.4.zip"
            urlmono = rf"https://github.com/MonoMod/MonoMod/releases/download/v22.07.31.01/MonoMod-22.07.31.01-net50.zip"
            urlhkapi = rf"https://github.com/hk-modding/api/releases/download/1.5.78.11833-74/ModdingApi{self.osbep}.zip"
            temp = os.path.join(rootpath.detect(), "temp") #type:ignore


            files = [
                ("BepInEx", urlbep),
                ("MonoMod", urlmono),
                ("HKAPI", urlhkapi)
            ]

            for name, url in files:
                self.log_message(f"Downloading {name}...")
                self.progress.set(0)
                self.update_idletasks()

                response = requests.get(url, stream=True)
                total = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(os.path.join(temp, f"{name}.zip"), "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if not chunk:
                            continue
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            percent = downloaded / total
                            self.progress.set(percent)
                            self.update_idletasks()

                self.log_message(f"✅ {name} downloaded!")

            self.log_message("All downloads complete!")
            self.progress.set(1)
            self.log_message("Extracting files...")
            self.progress.destroy()

            root = os.path.join(rootpath.detect(), "hmm") #type:ignore

            with open(os.path.join(root, "settings.json")) as f:
                import json
                settings = json.load(f) 
                path = settings.get("hollowknightpath")
            
            # Create separate folders for each extraction
            bepinex_extract = os.path.join(temp, "BepInEx_extracted")
            monomod_extract = os.path.join(temp, "MonoMod_extracted")
            hkapi_extract = os.path.join(temp, "HKAPI_extracted")
            
            os.makedirs(bepinex_extract, exist_ok=True)
            os.makedirs(monomod_extract, exist_ok=True)
            os.makedirs(hkapi_extract, exist_ok=True)
            
            try:
                with zipfile.ZipFile(os.path.join(temp, "BepInEx.zip"), 'r') as zip_ref:
                    zip_ref.extractall(bepinex_extract)
                self.log_message("✅ BepInEx extracted!")
            except zipfile.BadZipFile:
                self.log_message("❌ Failed to extract BepInEx.zip. The file may be corrupted.")
                return
            except FileNotFoundError:
                self.log_message("❌ BepInEx.zip not found in the temp directory.")
                return
            except Exception as e:
                self.log_message(f"❌ An unexpected error occurred while extracting BepInEx.zip: {e}")
                return
            
            try:
                with zipfile.ZipFile(os.path.join(temp, "MonoMod.zip"), 'r') as zip_ref:
                    zip_ref.extractall(monomod_extract)
                self.log_message("✅ MonoMod extracted!")
            except zipfile.BadZipFile:
                self.log_message("❌ Failed to extract MonoMod.zip. The file may be corrupted.")
                return
            except FileNotFoundError:
                self.log_message("❌ MonoMod.zip not found in the temp directory.")
                return
            except Exception as e:
                self.log_message(f"❌ An unexpected error occurred while extracting MonoMod.zip: {e}")
                return
            
            try:
                with zipfile.ZipFile(os.path.join(temp, "HKAPI.zip"), 'r') as zip_ref:
                    zip_ref.extractall(hkapi_extract)
                self.log_message("✅ HKAPI extracted!")
            except zipfile.BadZipFile:
                self.log_message("❌ Failed to extract HKAPI.zip. The file may be corrupted.")
                return
            except FileNotFoundError:
                self.log_message("❌ HKAPI.zip not found in the temp directory.")
                return
            except Exception as e:
                self.log_message(f"❌ An unexpected error occurred while extracting HKAPI.zip: {e}")
                return

            self.log_message("✅ All extractions complete!")
            self.log_message(f"Moving files to Hollow Knight Directory {path}...")
            
            try:
                # Move BepInEx files
                for item in os.listdir(bepinex_extract):
                    s = os.path.join(bepinex_extract, item)
                    d = os.path.join(path, item)
                    if os.path.isdir(s):
                        if os.path.exists(d):
                            shutil.rmtree(d)
                        shutil.copytree(s, d)
                    else:
                        os.makedirs(os.path.dirname(d), exist_ok=True)
                        shutil.copy2(s, d)

                # Move MonoMod inside BepInEx
                bepinex_target = os.path.join(path, "BepInEx")
                monomod_dest = os.path.join(bepinex_target, "MonoMod")

                os.makedirs(monomod_dest, exist_ok=True)

                for item in os.listdir(monomod_extract):
                    s = os.path.join(monomod_extract, item)
                    d = os.path.join(monomod_dest, item)
                    if os.path.isdir(s):
                        if os.path.exists(d):
                            shutil.rmtree(d)
                        shutil.copytree(s, d)
                    else:
                        shutil.copy2(s, d)

                # Move HKAPI files
                for item in os.listdir(hkapi_extract):
                    s = os.path.join(hkapi_extract, item)
                    d = os.path.join(path, item)
                    if os.path.isdir(s):
                        if os.path.exists(d):
                            shutil.rmtree(d)
                        shutil.copytree(s, d)
                    else:
                        os.makedirs(os.path.dirname(d), exist_ok=True)
                        shutil.copy2(s, d)

                self.log_message("✅ BepInEx, MonoMod, and HKAPI installed successfully!")
                
                # Optional: Clean up temp files
                self.log_message("Cleaning up temporary files...")
                shutil.rmtree(bepinex_extract, ignore_errors=True)
                shutil.rmtree(monomod_extract, ignore_errors=True)
                shutil.rmtree(hkapi_extract, ignore_errors=True)
                os.remove(os.path.join(temp, "BepInEx.zip"))
                os.remove(os.path.join(temp, "MonoMod.zip"))
                os.remove(os.path.join(temp, "HKAPI.zip"))
                self.log_message("✅ Installation complete!")
                
            except Exception as e:
                self.log_message(f"❌ An error occurred while moving files: {e}")

            

            self.log_message("✅ Extraction complete!")
    

        

        
        
            
bob = os.path.join(rootpath.detect(), "temp") #type:ignore

# --- Proper root window setup ---
if __name__ == "__main__":
    if not os.path.isdir(bob): #type:ignore
        os.makedirs(bob)  #type:ignore
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")

    root = customtkinter.CTk()
    root.title("BepInEx Downloader")
    root.withdraw()  # Hide the main window

    app = BepInExMenu(root)

    root.mainloop()