try:
    import customtkinter
    import json
    import os
    from tkinter import filedialog
    from PIL import Image, ImageTk
    import pybanana
    from menus.ModMenu import ModMenu
    import os


    #BepInEx/MonoMod Detection vars:
    bepinex = False
    monomod = False


    defaults = {
        "theme": "system",
        "hollowknightpath": "",
        "silksongpath": ""
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
            self.iconbitmap("./icon.ico")
            self.settings = settings.copy()
            self.last_modified = os.path.getmtime(settings_path)


 
            
            self.label = customtkinter.CTkLabel(self, text='Please Choose Game', width=40, height=28, fg_color='transparent')
            self.label.pack(pady="10", padx="10")
            
            self.hollow_image = customtkinter.CTkImage(
                light_image=Image.open("images/HollowKnight.png"), 
                dark_image=Image.open("images/HollowKnight.png"),
                size=(200, 120)
            )
            
            self.silksong_image = customtkinter.CTkImage(
                light_image=Image.open("images/silksong.png"),
                dark_image=Image.open("images/silksong.png"),
                size=(200, 120)
            )

            self.hollow_button = customtkinter.CTkButton(
                self,
                text="", 
                image=self.hollow_image,
                width=220,
                height=140,
                command=self.work_hollow_button
            )
            self.hollow_button.pack(padx=80, pady=80) 

            self.silksong_button = customtkinter.CTkButton(
                self,
                text="",
                image=self.silksong_image,
                width=220,
                height=140
            )
            self.silksong_button.pack(padx=80, pady=80)

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
        
        def find_hollow_knight_dir(self):
            self.selected_dir = filedialog.askdirectory(
                title="Select The Hollow Knight Directory", 
                initialdir=r"C:\Program Files (x86)\Steam\steamapps\common\Hollow Knight"
            )
            return self.selected_dir
        def find_bepinex(self):
            bepinexfile = "winhttp.dll"
        def detect_monomod(self):
            monomod_files = [
                "MonoMod.exe",
                "Mono.Cecil.dll",
                "MonoMod.Common.dll",
                "MonoMod.Utils.dll",
                "MonoMod.RuntimeDetour.dll",
                "MonoMod.RuntimeDetour.HookGen.exe"
            ]
            
            found = []
            for root, _, files in os.walk(self.selected_dir):
                for f in files:
                    if f in monomod_files:
                        found.append(os.path.join(root, f))
            if found:
                bepinex = True
            

        
        def work_hollow_button(self):
            with open('settings.json', 'r') as set:
                data = json.load(set)
                hollowpath = data.get('hollowknightpath', '')
            if hollowpath != "":
                self.mod_menu = ModMenu(self)
            else:
                selected_path = self.find_hollow_knight_dir()
                if selected_path:
                    # Save the selected path
                    self.settings['hollowknightpath'] = selected_path
                    with open('settings.json', 'w') as set:
                        json.dump(self.settings, set, indent=4)
                    print("Saved path:", selected_path)
        
        def cycle_theme(self):
            """Cycle through themes: system -> light -> dark -> system"""
            themes = ["system", "light", "dark"]
            current_index = themes.index(self.settings.get("theme", "system"))
            next_theme = themes[(current_index + 1) % len(themes)]
            
            # Update settings
            self.settings["theme"] = next_theme
            
            # Save to file
            with open(settings_path, "w") as jw:
                json.dump(self.settings, jw, indent=4)
            
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
                    with open(settings_path, "r") as jr:
                        new_settings = json.load(jr)
                    
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