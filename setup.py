from cx_Freeze import setup, Executable
import os
import platform

# --- Helper to include entire folders ---
def include_folder(folder_name):
    folder_path = os.path.join(os.getcwd(), folder_name)
    return (folder_path, folder_name)

# --- Detect current OS ---
current_os = platform.system()
base = None
icon_file = None

if current_os == "Windows":
    base = "Win32GUI"
    icon_file = "icon.ico"
elif current_os == "Darwin":  # macOS
    icon_file = "icon_macos.icns"
elif current_os == "Linux":
    icon_file = "icon_linux.png"

# --- Build options ---
build_exe_options = {
    "packages": ["tkinter", "os", "json"],
    "include_files": [
        include_folder("menus"),
        include_folder("mods"),
        include_folder("images"),
        include_folder("oneclick"),
        "settings.json",
        "bepinex_install.json",
    ],
    "optimize": 2,
    "include_msvcr": True,  # Needed for Windows
}

# --- Setup configuration ---
setup(
    name="HornetMM",
    version="1.0.0",
    description="A Cross-Platform Mod Manager built by Barrett",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "base.py",  # main entry point
            base=base,
            icon=icon_file if os.path.exists(icon_file) else None,
        )
    ],
)
