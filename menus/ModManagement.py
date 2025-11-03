import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import customtkinter
from oneclick.oneclick import GameBananaHandler

class ModManager(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("500x500")
        self.title("Mod Manager")

        self.tabs = customtkinter.CTkTabview(master=self, width=380, height=450)
        self.tabs.pack(padx=20, pady=20)
        self.tabs.add("Mods")
        self.tabs.add("Codes")

class InstallDialog(customtkinter.CTkToplevel):
    def __init__(self, parent, mod_info, url):
        super().__init__(parent)
        self.geometry("400x600")
        self.title("Install Mod")
        self.mod_info = mod_info
        self.url = url
        
        # Display mod info
        self.name_label = customtkinter.CTkLabel(self, text=mod_info['name'], font=("Arial", 20, "bold"))
        self.name_label.pack(pady=10)
        
        self.author_label = customtkinter.CTkLabel(self, text=f"by {mod_info['author']}")
        self.author_label.pack(pady=5)
        
        self.game_label = customtkinter.CTkLabel(self, text=f"Game: {mod_info['game']}")
        self.game_label.pack(pady=5)
        
        self.stats_label = customtkinter.CTkLabel(self, text=f"❤️ {mod_info['likes']} | ⬇️ {mod_info['downloads']} | 👁️ {mod_info['views']}")
        self.stats_label.pack(pady=5)
        
        # Description (scrollable)
        self.description = customtkinter.CTkTextbox(self, width=360, height=200)
        self.description.pack(pady=10, padx=20)
        self.description.insert("1.0", mod_info['description'])
        self.description.configure(state="disabled")
        
        # Progress bar
        self.progress = customtkinter.CTkProgressBar(self, width=360)
        self.progress.pack(pady=10, padx=20)
        self.progress.set(0)
        
        self.status_label = customtkinter.CTkLabel(self, text="Ready to install")
        self.status_label.pack(pady=5)
        
        # Install button
        self.install_button = customtkinter.CTkButton(self, text="Install", command=self.install_mod)
        self.install_button.pack(pady=20)
    
    def install_mod(self):
        self.install_button.configure(state="disabled")
        
        def progress_callback(current, total, message):
            self.progress.set(current / 100)
            self.status_label.configure(text=message)
            self.update()  # Force UI update
        
        handler = GameBananaHandler(install_path='./mods')
        success, result = handler.handle_url(self.url, progress_callback=progress_callback)
        
        if success:
            self.status_label.configure(text=f"✓ Installed to: {result['install_path']}") #type: ignore
            self.install_button.configure(text="Done", state="normal")
        else:
            self.status_label.configure(text=f"✗ Error: {result}")
            self.install_button.configure(state="normal")

if __name__ == "__main__":
    try:
        # Register protocol handler (one-time setup)
        handler = GameBananaHandler(install_path='./mods')
        handler.register_protocol_handler()
        
        root = customtkinter.CTk()
        
        # Check if launched via 1-click install
        if len(sys.argv) > 1 and sys.argv[1].startswith("hmm://"):
            url = sys.argv[1]
            
            # Parse and get mod info
            info = handler.parse_gamebanana_url(url)
            success, mod_info = handler.get_mod_info(info['mod_id'])  # type: ignore
            
            if success:
                # Show install dialog instead of main window
                root.withdraw()  # Hide main window
                dialog = InstallDialog(root, mod_info, url)  # type: ignore
                dialog.mainloop()
            else:
                print(f"Error fetching mod info: {mod_info}")
                input("Press Enter to exit...")
                root.destroy()
        else:
            # Normal launch - show mod manager
            root.withdraw()  # hide main window if you only want ModManager
            app = ModManager(root)
            app.mainloop()
            
    except Exception as e:
        import traceback
        print("="*60)
        print("ERROR OCCURRED:")
        print("="*60)
        print(f"\n{e}\n")
        print("Full traceback:")
        traceback.print_exc()
        print("="*60)
        input("\nPress Enter to exit...")