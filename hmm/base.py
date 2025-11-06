try:
    import customtkinter
    import json
    import os
    from tkinter import filedialog
    from PIL import Image
    from hmm.menus.BepInExInstall import ModInstaller  # The class name is ModInstaller
    from menus.SettingsMenu import Settings
    from CTkMenuBar import CTkTitleMenu, CustomDropdownMenu
    import platform

    arch = platform.architecture()[0]
    if arch == "ARM64":
        print("x86/x64 only, If your on windows consider enabling Prism")
        exit(1)


    # Settings defaults
    defaults = {
        "theme": "system",
        "hollowknightpath": "",
    }

    settings_path = "settings.json"

    # --- Step 1: Check if file exists, otherwise create it ---
    if not os.path.exists(settings_path):
        with open(settings_path, "w") as j:
            json.dump(defaults, j, indent=4)
        print("Settings file created with defaults.")

    # --- Step 2: Load settings ---
    try:
        with open(settings_path, "r") as jr:
            settings = json.load(jr)
    except json.JSONDecodeError:
        print("Settings file corrupted. Restoring defaults.")
        settings = defaults.copy()
    except Exception as ex:
        print(f"Error reading settings: {ex}")
        settings = defaults.copy()

    # --- Step 3: Compare defaults vs current and fix missing/extra values ---
    changed = False
    
    # Add missing keys from defaults
    for key, value in defaults.items():
        if key not in settings:
            settings[key] = value
            changed = True
            print(f"Added missing setting: {key} = {value}")
    
    # Remove keys that aren't in defaults
    keys_to_remove = [key for key in settings if key not in defaults]
    for key in keys_to_remove:
        del settings[key]
        changed = True
        print(f"Removed unknown setting: {key}")

    # If any change was made, update the file
    if changed:
        with open(settings_path, "w") as jw:
            json.dump(settings, jw, indent=4)
        print("Settings file updated.")

    # --- Step 4: Apply theme ---
    customtkinter.set_appearance_mode(settings["theme"])
    print(f"Applied theme: {settings['theme']}")

    # --- Step 5: Create app ---
    class App(customtkinter.CTk):
        def __init__(self):
            super().__init__()
            self.geometry("560x650")
            self.title("Hornet Mod Manager")
            
            # Handle icon gracefully if it doesn't exist
            if os.path.exists("./icon.ico"):
                self.iconbitmap("./icon.ico")
            
            self.settings = settings.copy()
            self.last_modified = os.path.getmtime(settings_path)
            
            # Menu bar
            self.menu = CTkTitleMenu(master=self)
            self.button = self.menu.add_cascade("Menu")
            self.dropdown = CustomDropdownMenu(widget=self.button)
            self.dropdown.add_option("Quit", command=self.quit)
            self.submenu = self.dropdown.add_submenu("File")
            self.submenu.add_option("Open Hollow Knight™ Path", command=self.find_hollow_knight_dir)
            self.submenu.add_option("Open Hollow Knight: Silksong™ Path", command=self.find_silksong_dir)
            
            # Title label
            self.label = customtkinter.CTkLabel(
                self, 
                text='Please Choose Game', 
                width=40, 
                height=28, 
                fg_color='transparent'
            )
            self.label.pack(pady=10, padx=10)
            
            # Load images with error handling
            try:
                self.hollow_image = customtkinter.CTkImage(
                    light_image=Image.open("images/HollowKnight.png"), 
                    dark_image=Image.open("images/HollowKnight.png"),
                    size=(200, 120)
                )
            except Exception as e:
                print(f"Could not load Hollow Knight image: {e}")
                self.hollow_image = None
            
            try:
                self.silksong_image = customtkinter.CTkImage(
                    light_image=Image.open("images/silksong.png"),
                    dark_image=Image.open("images/silksong.png"),
                    size=(200, 120)
                )
            except Exception as e:
                print(f"Could not load Silksong image: {e}")
                self.silksong_image = None

            # Hollow Knight button
            self.hollow_button = customtkinter.CTkButton(
                self,
                text="Hollow Knight" if not self.hollow_image else "", 
                image=self.hollow_image,
                width=220,
                height=140,
                command=self.work_hollow_button
            )
            self.hollow_button.pack(padx=80, pady=20) 

            # Silksong button
            self.silksong_button = customtkinter.CTkButton(
                self,
                text="Silksong" if not self.silksong_image else "",
                image=self.silksong_image,
                width=220,
                height=140,
                command=self.work_silksong_button
            )
            self.silksong_button.pack(padx=80, pady=20)

            # Settings button
            self.settings_button = customtkinter.CTkButton(
                self,
                text="⚙️",
                width=40,
                height=40,
                corner_radius=8,
                hover_color=("gray85", "gray25"),
                fg_color="transparent",
                command=self.open_settings
            )
            self.settings_button.place(x=10, y=10)

            # Theme toggle button
            self.theme_button = customtkinter.CTkButton(
                self,
                text="🌓",
                width=40,
                height=40,
                corner_radius=8,
                command=self.cycle_theme,
                fg_color="transparent",
                hover_color=("gray85", "gray25")
            )
            self.theme_button.place(x=510, y=10)
            
            # Start monitoring settings file
            self.check_settings_update()

        def open_settings(self):
            """Open the settings menu"""
            try:
                settings_menu = Settings(self)
                settings_menu.show_again()
            except Exception as e:
                print(f"Failed to open settings menu: {e}")

        def find_hollow_knight_dir(self):
            """Open dialog to select Hollow Knight directory"""
            selected_dir = filedialog.askdirectory(
                title="Select The Hollow Knight Directory", 
                initialdir=r"C:\Program Files (x86)\Steam\steamapps\common\Hollow Knight"
            )
            if selected_dir:
                self.settings['hollowknightpath'] = selected_dir
                with open(settings_path, 'w') as f:
                    json.dump(self.settings, f, indent=4)
                print(f"Hollow Knight path saved: {selected_dir}")
            return selected_dir
        
        def find_silksong_dir(self):
            """Open dialog to select Silksong directory"""
            selected_dir = filedialog.askdirectory(
                title="Select The Hollow Knight Silksong Directory", 
                initialdir=r"C:\Program Files (x86)\Steam\steamapps\common\Hollow Knight Silksong"
            )
            if selected_dir:
                self.settings['silksongpath'] = selected_dir
                with open(settings_path, 'w') as f:
                    json.dump(self.settings, f, indent=4)
                print(f"Silksong path saved: {selected_dir}")
            return selected_dir
        
        def work_hollow_button(self):
            """Handle Hollow Knight button click"""
            try:
                with open('settings.json', 'r') as f:
                    data = json.load(f)
                    hollowpath = data.get('hollowknightpath', '')
                
                if hollowpath and os.path.exists(hollowpath):
                    # Path exists, open mod installer with saved path
                    mod_installer = ModInstaller(self, install_path=hollowpath)
                else:
                    # No path or invalid path, ask user to select
                    selected_path = self.find_hollow_knight_dir()
                    if selected_path:
                        # After saving, open mod installer with new path
                        mod_installer = ModInstaller(self, install_path=selected_path)
            except Exception as e:
                print(f"Error opening Hollow Knight mod menu: {e}")

        def work_silksong_button(self):
            """Handle Silksong button click"""
            try:
                with open('settings.json', 'r') as f:
                    data = json.load(f)
                    silksongpath = data.get('silksongpath', '')
                
                if silksongpath and os.path.exists(silksongpath):
                    # Path exists, open mod menu
                    mod_menu = ModInstaller(self)
                else:
                    # No path or invalid path, ask user to select
                    selected_path = self.find_silksong_dir()
                    if selected_path:
                        # After saving, open mod menu
                        mod_menu = ModInstaller(self)
            except Exception as e:
                print(f"Error opening Silksong mod menu: {e}")
        
        def cycle_theme(self):
            """Cycle through themes: system -> light -> dark -> system"""
            themes = ["system", "light", "dark"]
            current_index = themes.index(self.settings.get("theme", "system"))
            next_theme = themes[(current_index + 1) % len(themes)]
            
            # Update settings
            self.settings["theme"] = next_theme
            
            # Save to file
            with open(settings_path, "w") as f:
                json.dump(self.settings, f, indent=4)
            
            # Apply immediately
            customtkinter.set_appearance_mode(next_theme)
            
            # Update button icon
            icons = {"system": "🌓", "light": "☀️", "dark": "🌙"}
            self.theme_button.configure(text=icons[next_theme])
            
            print(f"Theme changed to: {next_theme}")
        
        def check_settings_update(self):
            """Check if settings file has been modified and reload if needed"""
            try:
                current_modified = os.path.getmtime(settings_path)
                
                if current_modified != self.last_modified:
                    self.last_modified = current_modified
                    
                    # Reload settings
                    with open(settings_path, "r") as f:
                        new_settings = json.load(f)
                    
                    # Check if theme changed
                    if new_settings.get("theme") != self.settings.get("theme"):
                        customtkinter.set_appearance_mode(new_settings["theme"])
                        print(f"Theme updated to: {new_settings['theme']}")
                    
                    self.settings = new_settings
                    
            except Exception as e:
                print(f"Error checking settings: {e}")
            
            # Check again in 500ms
            self.after(500, self.check_settings_update)

    
    if __name__ == "__main__":
        app = App()
        app.mainloop()

except KeyboardInterrupt:
    print("\nYou closed the app")
except Exception as e:
    print(f"An error has occurred: {e}")
    import traceback
    traceback.print_exc()