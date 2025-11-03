import os
import platform
import requests
import zipfile
import io
import threading
import customtkinter
from tkinter import filedialog, messagebox
import json
import shutil
import tempfile

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

def get_mods_install_path():
    """Get the mods installation path based on hollowknightpath from settings.json."""
    hk_path = load_hollow_knight_path()
    if not hk_path:
        return None
    
    mods_path = os.path.join(hk_path, "BepInEx", "plugins")
    return mods_path

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
    """Detect which mod loaders are already installed with proper checks."""
    
    # BepInEx detection - check for core files
    bepinex_installed = False
    bepinex_path = os.path.join(directory, "BepInEx")
    if os.path.exists(bepinex_path):
        # Check for core BepInEx files
        core_dll = os.path.join(bepinex_path, "core", "BepInEx.dll")
        config_file = os.path.join(bepinex_path, "config", "BepInEx.cfg")
        plugins_folder = os.path.join(bepinex_path, "plugins")
        
        if os.path.exists(core_dll) or os.path.exists(config_file) or os.path.exists(plugins_folder):
            bepinex_installed = True
    
    # MonoMod detection - check both BepInEx/monomod folder AND Managed folder
    monomod_installed = False
    
    # Check BepInEx/monomod folder (where patches go)
    monomod_folder = os.path.join(directory, "BepInEx", "monomod")
    if os.path.exists(monomod_folder):
        monomod_installed = True
    
    # Also check Managed folder for MonoMod runtime files
    if not monomod_installed:
        managed_paths = [
            os.path.join(directory, "hollow_knight_Data", "Managed"),
            os.path.join(directory, "Hollow Knight_Data", "Managed")
        ]
        
        for managed_path in managed_paths:
            if os.path.exists(managed_path):
                # Check for MonoMod.RuntimeDetour and other MonoMod DLLs
                monomod_files = [
                    "MonoMod.RuntimeDetour.dll",
                    "MonoMod.Utils.dll",
                    "MMHOOK_Assembly-CSharp.dll"
                ]
                
                for dll in monomod_files:
                    dll_path = os.path.join(managed_path, dll)
                    if os.path.exists(dll_path):
                        monomod_installed = True
                        break
                
                if monomod_installed:
                    break
    
    # Hollow Knight Modding API detection
    hkapi_installed = False
    
    # Check Managed folder paths
    managed_paths = [
        os.path.join(directory, "hollow_knight_Data", "Managed"),
        os.path.join(directory, "Hollow Knight_Data", "Managed")
    ]
    
    for managed_path in managed_paths:
        if os.path.exists(managed_path):
            # Check for modded Assembly-CSharp.dll (has .xml file as indicator)
            assembly_xml = os.path.join(managed_path, "Assembly-CSharp.xml")
            mmhook = os.path.join(managed_path, "MMHOOK_Assembly-CSharp.dll")
            
            # If either the XML or MMHOOK file exists, API is installed
            if os.path.exists(assembly_xml) or os.path.exists(mmhook):
                hkapi_installed = True
                break
    
    # Check for Modding API in BepInEx plugins (alternative location)
    if not hkapi_installed and os.path.exists(bepinex_path):
        bepinex_api_locations = [
            os.path.join(bepinex_path, "plugins", "Modding API.dll"),
            os.path.join(bepinex_path, "plugins", "MAPI"),
            os.path.join(bepinex_path, "Mods")
        ]
        
        for location in bepinex_api_locations:
            if os.path.exists(location):
                hkapi_installed = True
                break
    
    return bepinex_installed, monomod_installed, hkapi_installed

def get_mod_details(directory):
    """Get detailed information about installed mods."""
    details = []
    
    bepinex_path = os.path.join(directory, "BepInEx")
    if os.path.exists(bepinex_path):
        # Check BepInEx core
        core_dll = os.path.join(bepinex_path, "core", "BepInEx.dll")
        if os.path.exists(core_dll):
            details.append("  • BepInEx core found")
        
        # Check plugins folder
        plugins = os.path.join(bepinex_path, "plugins")
        if os.path.exists(plugins):
            plugin_count = len([f for f in os.listdir(plugins) if f.endswith('.dll')])
            if plugin_count > 0:
                details.append(f"  • {plugin_count} plugin(s) in BepInEx/plugins")
    
    # Check MonoMod files in Managed
    managed_paths = [
        os.path.join(directory, "hollow_knight_Data", "Managed"),
        os.path.join(directory, "Hollow Knight_Data", "Managed")
    ]
    
    for managed_path in managed_paths:
        if os.path.exists(managed_path):
            monomod_files = [
                "MonoMod.RuntimeDetour.dll",
                "MonoMod.Utils.dll",
                "MMHOOK_Assembly-CSharp.dll"
            ]
            found_files = [f for f in monomod_files if os.path.exists(os.path.join(managed_path, f))]
            if found_files:
                details.append(f"  • MonoMod files in Managed: {', '.join(found_files)}")
            
            # Check for Modding API
            api_xml = os.path.join(managed_path, "Assembly-CSharp.xml")
            if os.path.exists(api_xml):
                details.append("  • Modding API installed (patched Assembly-CSharp)")
            break
    
    return details if details else ["  • No additional details available"]

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
        self.geometry("600x550")
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
        
        self.status_text = customtkinter.CTkTextbox(self.status_frame, height=200)
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
        self.install_button.pack(pady=10)
        

        def do_stuff(parent):
            self.withdraw()
            ModManagement.ModManager(parent)


        import ModManagement
        # Open ModManager button (only show if everything is installed)
        self.modmanager_button = customtkinter.CTkButton(
            self,
            text="Open Mod Manager",
            command=lambda: do_stuff(parent),
            state="disabled"
        )
        self.modmanager_button.pack(pady=10)

       

        # If path exists, auto-detect mods
        if self.install_dir and verify_hollow_knight_directory(self.install_dir):
            self.detect_and_display()

    def detect_and_display(self):
        """Detect installed mods and display detailed information."""
        self.bepinex, self.monomod, self.hkapi = detect_installed_mods(self.install_dir)
        
        self.log("=== Detection Results ===")
        self.log(f"BepInEx: {'✅ Installed' if self.bepinex else '❌ Not found'}")
        self.log(f"MonoMod: {'✅ Installed' if self.monomod else '❌ Not found'}")
        self.log(f"HK Modding API: {'✅ Installed' if self.hkapi else '❌ Not found'}")
        
        # Show detailed information
        details = get_mod_details(self.install_dir)
        if details:
            self.log("\n=== Installation Details ===")
            for detail in details:
                self.log(detail)
        
        self.log("")
        self.install_button.configure(state="normal")
        
        # Enable ModManager button if everything is installed
        if self.bepinex and self.monomod and self.hkapi:
            self.modmanager_button.configure(state="normal")
            self.log("✅ All components installed! You can open Mod Manager.")
        else:
            self.modmanager_button.configure(state="disabled")

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
        
        self.status_text.delete("1.0", "end")
        self.detect_and_display()

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

            if not self.hkapi:
                self.log("📦 Installing Hollow Knight Modding API...")
                self.progress.set(0)
                hkapi_info = get_latest_release(HKAPI_URL)
                
                # Determine platform-specific release
                system = platform.system().lower()
                if system == "windows":
                    target_name = "ModdingApiWin.zip"
                elif system == "linux":
                    target_name = "ModdingApiLinux.zip"
                elif system == "darwin":
                    target_name = "ModdingApiMac.zip"
                else:
                    self.log(f"⚠️ Unsupported platform: {system}\n")
                    return
                
                hkapi_url = None
                for asset in hkapi_info["assets"]:
                    if asset["name"] == target_name:
                        hkapi_url = asset["browser_download_url"]
                        self.log(f"Found: {asset['name']}")
                        break
                
                if hkapi_url:
                    self.log("Downloading and installing...")
                    
                    # Download to temp location first
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Download and extract to temp
                        download_and_extract(hkapi_url, temp_dir, self.update_progress)
                        
                        # Find the Managed folder
                        managed_path = os.path.join(self.install_dir, "hollow_knight_Data", "Managed")  # type: ignore
                        if not os.path.exists(managed_path):
                            managed_path = os.path.join(self.install_dir, "Hollow Knight_Data", "Managed")  # type: ignore
                        
                        if not os.path.exists(managed_path):  # type: ignore
                            self.log("❌ Error: Could not find hollow_knight_Data/Managed folder")
                            return
                        
                        self.log(f"Installing to: {managed_path}\n")
                        
                        # First, delete old files from root if they exist
                        old_files = ['Assembly-CSharp.dll', 'MonoMod.RuntimeDetour.dll', 'MonoMod.Utils.dll', 
                                     'MMHOOK_Assembly-CSharp.dll', 'MMHOOK_PlayMaker.dll', 'Mono.Cecil.dll']
                        for old_file in old_files:
                            old_path = os.path.join(self.install_dir, old_file)  # type: ignore
                            if os.path.exists(old_path):  # type: ignore
                                os.remove(old_path)  # type: ignore
                                self.log(f"  🗑️ Removed old file from root: {old_file}")
                        
                        # Copy all files to Managed folder
                        copied_count = 0
                        for item in os.listdir(temp_dir):
                            src = os.path.join(temp_dir, item)
                            dst = os.path.join(managed_path, item)  # type: ignore
                            
                            self.log(f"  Copying {item}...")
                            self.log(f"    From: {src}")
                            self.log(f"    To: {dst}")
                            
                            if os.path.isfile(src):
                                shutil.copy2(src, dst)
                                self.log(f"  ✓ {item}")
                                copied_count += 1
                        
                        self.log(f"\n✓ Installed {copied_count} files")
                        
                        # Create BepInEx/monomod folder for patches
                        monomod_folder = os.path.join(self.install_dir, "BepInEx", "monomod")  # type: ignore
                        os.makedirs(monomod_folder, exist_ok=True)  # type: ignore
                        self.log("\n✓ Created BepInEx/monomod folder for MonoMod patches")
                    
                    self.hkapi = True
                    self.log("✅ HK Modding API installed successfully!\n")
                else:
                    self.log(f"⚠️ Could not find {target_name} in releases\n")
            else:
                self.log("ℹ️ HK Modding API already installed\n")
            
            # Note about MonoMod
            if not self.monomod:
                self.log("\nℹ️ Note: MonoMod is included with the HK Modding API")
                self.log("   and will be automatically detected after installation.\n")

            self.log("=" * 30)
            self.log("🎉 Installation complete!")
            self.log("You can now install mods to the BepInEx/plugins folder")
            self.log("\nRe-scanning installation...")
            self.progress.set(1)
            
            # Re-detect to show updated status
            self.detect_and_display()
            
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