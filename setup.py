from cx_Freeze import setup, Executable
import os
import platform
import sys

# --- Toggle this to True when debugging ---
DEBUG_MODE = False

# --- Helper to include folders ---
def include_folder(folder_name):
    folder_path = os.path.join(os.getcwd(), folder_name)
    return (folder_path, folder_name)

# --- OS detection ---
current_os = platform.system()
base = None
icon_file = None

if current_os == "Windows":
    base = None if DEBUG_MODE else "Win32GUI"  # show console in debug mode
    icon_file = "icon.ico"
elif current_os == "Darwin":
    icon_file = "icon_macos.icns"
elif current_os == "Linux":
    icon_file = "icon_linux.png"

# --- Build options ---
build_exe_options = {
    "packages": [
        "tkinter",
        "customtkinter",
        "os",
        "json",
        "sys",
        "subprocess"
    ],
    "include_files": [
        include_folder("menus"),
        include_folder("mods"),
        include_folder("images"),
        include_folder("oneclick"),
        "settings.json",
        "bepinex_install.json",
    ],
    "optimize": 2,
    "include_msvcr": True,  # include runtime DLLs on Windows
    "zip_include_packages": ["*"],  # include everything needed
    "zip_exclude_packages": [],
}

# --- Setup configuration ---
setup(
    name="HornetMM",
    version="1.0.0",
    description="A Cross-Platform Mod Manager built by Barrett",
    author="Sonic3Modder",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "base.py",
            base=base,
            icon=icon_file if os.path.exists(icon_file) else None,
        )
    ],
)
