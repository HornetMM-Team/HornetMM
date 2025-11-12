import requests  # type: ignore
import customtkinter
import zipfile
import platform
import os
import tempfile
import threading
import shutil
import json
import time


class BepInExMenu(customtkinter.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("BepInEx Installer")
        self.geometry("400x500")

        # Button
        self.install_button = customtkinter.CTkButton(
            self,
            text="Install BepInEx",
            command=lambda: threading.Thread(target=self.download_bepinex).start()
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

        temp = os.path.join(tempfile.gettempdir(), "hornetmm_temp")
        os.makedirs(temp, exist_ok=True)
        self.log_message(f"Temporary folder: {temp}")

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
            start_time = time.time()

            zip_path = os.path.join(temp, f"{name}.zip")
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=65536):  # 64 KB chunks
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        percent = downloaded / total
                        self.progress.set(percent)
                        self.update_idletasks()

                    # Optional: show speed in log every ~1s
                    elapsed = time.time() - start_time
                    if elapsed > 1 and total > 0:
                        speed = downloaded / 1024 / elapsed  # KB/s
                        self.log_message(f"{name} download speed: {speed:.1f} KB/s")
                        start_time = time.time()

            self.log_message(f"✅ {name} downloaded!")

        self.log_message("All downloads complete!")
        self.progress.set(1)
        self.log_message("Extracting files...")
        self.progress.destroy()

        # Load Hollow Knight install path from settings.json
        root = os.path.join(os.getcwd(), "hmm")
        with open(os.path.join(root, "settings.json")) as f:
            settings = json.load(f)
            path = settings.get("hollowknightpath")

        bepinex_extract = os.path.join(temp, "BepInEx_extracted")
        monomod_extract = os.path.join(temp, "MonoMod_extracted")
        hkapi_extract = os.path.join(temp, "HKAPI_extracted")

        os.makedirs(bepinex_extract, exist_ok=True)
        os.makedirs(monomod_extract, exist_ok=True)
        os.makedirs(hkapi_extract, exist_ok=True)

        def extract_zip(zip_name, extract_to):
            try:
                with zipfile.ZipFile(os.path.join(temp, f"{zip_name}.zip"), 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
                self.log_message(f"✅ {zip_name} extracted!")
            except FileNotFoundError:
                self.log_message(f"❌ {zip_name}.zip not found in {temp}.")
                raise
            except zipfile.BadZipFile:
                self.log_message(f"❌ {zip_name}.zip is corrupted.")
                raise

        for name, folder in [("BepInEx", bepinex_extract), ("MonoMod", monomod_extract), ("HKAPI", hkapi_extract)]:
            extract_zip(name, folder)

        self.log_message("✅ All extractions complete!")
        self.log_message(f"Moving files to Hollow Knight directory: {path}...")

        try:
            # Move BepInEx
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
            monomod_dest = os.path.join(path, "BepInEx", "MonoMod")
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

            # Move HKAPI
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

        except Exception as e:
            self.log_message(f"❌ Error while moving files: {e}")
            return

        # Clean up
        self.log_message("Cleaning up temporary files...")
        shutil.rmtree(temp, ignore_errors=True)

        # Final message + disable button
        self.log_message("✅ Everything is installed!")
        self.install_button.configure(state="disabled", text="Installed ✔️")
        self.log_message("✅ Installation complete!")


# --- Proper root window setup ---
if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")

    root = customtkinter.CTk()
    root.title("BepInEx Downloader")
    root.withdraw()  # Hide the main window

    app = BepInExMenu(root)

    root.mainloop()
