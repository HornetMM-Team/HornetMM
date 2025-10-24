import os
import platform
import requests
import zipfile
import io
import threading
import customtkinter
from tkinter import filedialog, messagebox
import json

# GitHub API endpoints
BEPINEX_API_URL = "https://api.github.com/repos/BepInEx/BepInEx/releases/latest"
MONOMOD_API_URL = "https://api.github.com/repos/MonoMod/MonoMod/releases/latest"
HKAPI_URL = "https://api.github.com/repos/hk-modding/api/releases/latest"

SETTINGS_FILE = "settings.json"

# ----------------- Settings Handling -----------------
def load_hollow_knight_path():
    """Load Hollow Knight path from settings.json in the root folder."""
    if not os.path.exists(SETTINGS_FILE):
        return None
    
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
        return settings.get("hollowknightpath")
    except Exception as e:
        print(f"Failed to load settings.json: {e}")
        return None

def save_hollow_knight_path(path):
    """Save the Hollow Knight path to settings.json."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({"hollowknightpath": path}, f, indent=4)
    except Exception as e:
        print(f"Failed to save settings.json: {e}")

# ----------------- GitHub / Download Helpers -----------------
def get_latest_release(repo_url):
    """Fetch latest release info from a GitHub repo."""
    try:
        response = requests.get(repo_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch release info: {str(e)}")

def get_platform_filename():
    """Return correct BepInEx zip filename pattern for your system."""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    if system == "windows":
        if "64" in arch or "amd64" in arch or "x86_64" in arch:
            return "BepInEx_win_x64"
        else:
            return "BepInEx_win_x86"
    elif system == "linux":
        if "64" in arch or "amd64" in arch or "x86_64" in arch:
            return "BepInEx_linux_x64"
        else:
            return "BepInEx_linux_x86"
    elif system == "darwin":
        return "BepInEx_macos_x64"
    else:
        raise Exception(f"Unsupported OS: {system}")

def verify_hollow_knight_directory(directory):
    """Check if directory contains Hollow Knight installation."""
    if not directory:
        return False
    
    indicators = [
        "hollow_knight.exe",
        "hollow_knight_Data",
        "Hollow Knight.exe",
        "Hollow Knight_Data"
    ]
    
    for item in indicators:
        if os.path.exists(os.path.join(directory, item)):
            return True
    return False

def detect_installed_mods(directory):
    """Detect which mod loaders are already installed."""
    bepinex = os.path.exists(os.path.join(directory, "BepInEx"))
    monomod = os.path.exists(os.path.join(directory, "Mods")) or \
              os.path.exists(os.path.join(directory, "hollow_knight_Data", "Managed", "Assembly-CSharp.mm.dll"))
    hkapi = os.path.exists(os.path.join(directory, "hollow_knight_Data", "Managed", "Assembly-CSharp.Modding.dll"))
    
    return bepinex, monomod, hkapi

def download_and_extract(url, install_dir, progress_callback=None):
    """Download and extract ZIP file to the specified directory."""
    os.makedirs(install_dir, exist_ok=True)
    
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    chunks = []
    
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            chunks.append(chunk)
            downloaded += len(chunk)
            if progress_callback and total_size > 0:
                progress_callback(downloaded / total_size)
    
    content = b''.join(chunks)
    with zipfile.ZipFile(io.BytesIO(content)) as zip_ref:
        zip_ref.extractall(install_dir)

# ----------------- Mod Installer GUI -----------------
class ModInstaller(customtkinter.CTkToplevel):
    def __init__(self, parent, install_path=None):
        super().__init__(parent)
        self.title("Hollow Knight Mod Installer")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Load path from settings.json if not provided
        if install_path is None:
            install_path = load_hollow_knight_path()
        self.install_dir = install_path

        self.bepinex = False
        self.monomod = False
        self.hkapi = False

        # Title
        self.label = customtkinter.CTkLabel(
            self, 
            text="Hollow Knight Mod Installer",
            font=("Arial", 20, "bold")
        )
        self.label.pack(pady=20)

        # Directory frame
        self.dir_frame = customtkinter.CTkFrame(self)
        self.dir_frame.pack(pady=10, padx=20, fill="x")
        
        self.dir_label = customtkinter.CTkLabel(
            self.dir_frame, 
            text=f"Selected: {self.install_dir}" if self.install_dir else "No directory selected",
            wraplength=400
        )
        self.dir_label.pack(pady=10)
        
        self.select_dir_button = customtkinter.CTkButton(
            self.dir_frame, 
            text="Select Hollow Knight Folder",
            command=self.select_directory
        )
        self.select_dir_button.pack(pady=10)

        # Status display
        self.status_frame = customtkinter.CTkFrame(self)
        self.status_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.status_text = customtkinter.CTkTextbox(self.status_frame, height=150)
        self.status_text.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Progress bar
        self.progress = customtkinter.CTkProgressBar(self)
        self.progress.pack(pady=10, padx=20, fill="x")
        self.progress.set(0)

        # Install button
        self.install_button = customtkinter.CTkButton(
            self, 
            text="Install/Update Mods",
            command=self.start_install,
            state="disabled"
        )
        self.install_button.pack(pady=20)

        # If path exists, auto-detect mods
        if self.install_dir and verify_hollow_knight_directory(self.install_dir):
            self.bepinex, self.monomod, self.hkapi = detect_installed_mods(self.install_dir)
            self.log("=== Detection Results ===")
            self.log(f"BepInEx: {'✅ Installed' if self.bepinex else '❌ Not found'}")
            self.log(f"MonoMod: {'✅ Installed' if self.monomod else '❌ Not found'}")
            self.log(f"HK API: {'✅ Installed' if self.hkapi else '❌ Not found'}")
            self.log("")
            self.install_button.configure(state="normal")

    def log(self, message):
        self.status_text.insert("end", message + "\n")
        self.status_text.see("end")
        self.update()

    def select_directory(self):
        directory = filedialog.askdirectory(title="Select Hollow Knight Installation Folder")
        if not directory:
            return
        
        if not verify_hollow_knight_directory(directory):
            messagebox.showerror(
                "Invalid Directory",
                "This doesn't appear to be a Hollow Knight installation directory.\n\n"
                "Please select the folder containing Hollow Knight.exe or hollow_knight.exe"
            )
            return
        
        self.install_dir = directory
        self.dir_label.configure(text=f"Selected: {directory}")
        save_hollow_knight_path(directory)
        
        self.bepinex, self.monomod, self.hkapi = detect_installed_mods(directory)
        self.log("=== Detection Results ===")
        self.log(f"BepInEx: {'✅ Installed' if self.bepinex else '❌ Not found'}")
        self.log(f"MonoMod: {'✅ Installed' if self.monomod else '❌ Not found'}")
        self.log(f"HK API: {'✅ Installed' if self.hkapi else '❌ Not found'}")
        self.log("")
        self.install_button.configure(state="normal")

    def update_progress(self, value):
        self.progress.set(value)
        self.update()

    def start_install(self):
        self.install_button.configure(state="disabled")
        self.select_dir_button.configure(state="disabled")
        thread = threading.Thread(target=self.install_mods, daemon=True)
        thread.start()

    def install_mods(self):
        try:
            if not self.bepinex:
                self.log("📦 Installing BepInEx...")
                bepinex_info = get_latest_release(BEPINEX_API_URL)
                filename_pattern = get_platform_filename()
                
                asset_url = None
                for asset in bepinex_info["assets"]:
                    if (filename_pattern in asset["name"] and 
                        asset["name"].endswith(".zip") and
                        "Patcher" not in asset["name"]):
                        asset_url = asset["browser_download_url"]
                        self.log(f"Found: {asset['name']}")
                        break
                
                if not asset_url:
                    self.log(f"❌ Could not find matching BepInEx release for {filename_pattern}")
                    self.log("Available assets:")
                    for asset in bepinex_info["assets"]:
                        self.log(f"  - {asset['name']}")
                    return
                
                download_and_extract(asset_url, self.install_dir, self.update_progress)
                self.bepinex = True
                self.log("✅ BepInEx installed successfully!\n")
            else:
                self.log("ℹ️ BepInEx already installed\n")

            if self.bepinex and not self.monomod:
                self.log("📦 Installing MonoMod...")
                self.progress.set(0)
                monomod_info = get_latest_release(MONOMOD_API_URL)
                mono_url = None
                for asset in monomod_info["assets"]:
                    if asset["name"].endswith(".zip"):
                        mono_url = asset["browser_download_url"]
                        break
                
                if mono_url:
                    download_and_extract(mono_url, self.install_dir, self.update_progress)
                    self.monomod = True
                    self.log("✅ MonoMod installed successfully!\n")
                else:
                    self.log("⚠️ Could not find MonoMod release\n")

            if not self.hkapi:
                self.log("📦 Installing Hollow Knight API...")
                self.progress.set(0)
                hkapi_info = get_latest_release(HKAPI_URL)
                hkapi_url = None
                for asset in hkapi_info["assets"]:
                    if asset["name"].endswith(".zip"):
                        hkapi_url = asset["browser_download_url"]
                        break
                
                if hkapi_url:
                    download_and_extract(hkapi_url, self.install_dir, self.update_progress)
                    self.hkapi = True
                    self.log("✅ HK API installed successfully!\n")
                else:
                    self.log("⚠️ Could not find HK API release\n")
            else:
                self.log("ℹ️ HK API already installed\n")

            self.log("=" * 30)
            self.log("🎉 Installation complete!")
            self.log("You can now install mods to the BepInEx/plugins folder")
            self.progress.set(1)
            
        except Exception as e:
            self.log(f"\n❌ Error during installation: {str(e)}")
            self.progress.set(0)
        finally:
            self.install_button.configure(state="normal")
            self.select_dir_button.configure(state="normal")

# ----------------- Main -----------------
if __name__ == "__main__":
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("blue")
    
    app = customtkinter.CTk()
    app.withdraw()  # Hide main window
    
    installer = ModInstaller(app)
    installer.mainloop()
