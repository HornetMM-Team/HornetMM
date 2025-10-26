import sys
import os
import urllib.parse
import requests
import zipfile

class GameBananaHandler:
    """Handler for GameBanana 1-click install functionality"""
    
    def __init__(self, install_path='./mods'):
        self.install_path = install_path
        os.makedirs(self.install_path, exist_ok=True)
    
    def register_protocol_handler(self, script_path=None):
        """Register gamebanana:// protocol handler"""
        if script_path is None:
            script_path = os.path.abspath(__file__)
        
        if sys.platform == 'win32':
            import winreg
            
            python_path = sys.executable
            key_path = r'Software\Classes\gamebanana'
            
            try:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, 'URL:GameBanana Protocol')
                winreg.SetValueEx(key, 'URL Protocol', 0, winreg.REG_SZ, '')
                
                command_key = winreg.CreateKey(key, r'shell\open\command')
                command = f'"{python_path}" "{script_path}" "%1"'
                winreg.SetValueEx(command_key, '', 0, winreg.REG_SZ, command)
                
                winreg.CloseKey(command_key)
                winreg.CloseKey(key)
                return True, "Protocol handler registered successfully!"
            except Exception as e:
                return False, f"Error registering protocol: {e}"
        elif sys.platform == 'linux':
            return False, "Linux protocol registration not implemented yet"
        elif sys.platform == 'darwin':
            return False, "macOS protocol registration not implemented yet"
        else:
            return False, f"Unsupported platform: {sys.platform}"
    
    def parse_gamebanana_url(self, url):
        """Parse gamebanana:// URL to extract mod information"""
        parsed = urllib.parse.urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        return {
            'action': path_parts[0] if path_parts else None,
            'mod_id': path_parts[1] if len(path_parts) > 1 else None,
            'params': urllib.parse.parse_qs(parsed.query)
        }
    
    def get_mod_info(self, mod_id):
        """
        Get detailed information about a mod
        
        Args:
            mod_id: The GameBanana mod ID
        
        Returns:
            tuple: (success, mod_info_dict_or_error_message)
        """
        try:
            # Get basic mod info
            api_url = f"https://api.gamebanana.com/Core/Item/Data"
            params = {
                'itemtype': 'Mod',
                'itemid': mod_id,
                'fields': 'name,Owner().name,screenshots,likes,views,downloads,description,Game().name,Rootcategory().name,date,Files().aFiles()'
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            
            if not response.ok:
                return False, f"API request failed: {response.status_code}"
            
            data = response.json()
            
            # Parse the response
            mod_info = {
                'mod_id': mod_id,
                'name': data[0] if len(data) > 0 else 'Unknown',
                'author': data[1] if len(data) > 1 else 'Unknown',
                'screenshots': data[2] if len(data) > 2 else [],
                'likes': data[3] if len(data) > 3 else 0,
                'views': data[4] if len(data) > 4 else 0,
                'downloads': data[5] if len(data) > 5 else 0,
                'description': data[6] if len(data) > 6 else '',
                'game': data[7] if len(data) > 7 else 'Unknown',
                'category': data[8] if len(data) > 8 else 'Unknown',
                'date': data[9] if len(data) > 9 else 0,
                'files': data[10] if len(data) > 10 else []
            }
            
            return True, mod_info
            
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {e}"
        except Exception as e:
            return False, f"Error fetching mod info: {e}"
    
    def download_mod(self, mod_id, progress_callback=None):
        """
        Download mod from GameBanana
        
        Args:
            mod_id: The GameBanana mod ID
            progress_callback: Optional callback function(current, total, message)
        
        Returns:
            tuple: (success, filename_or_error_message)
        """
        try:
            api_url = f"https://gamebanana.com/apiv11/Mod/{mod_id}/DownloadPage"
            
            if progress_callback:
                progress_callback(0, 100, f"Fetching mod info...")
            
            response = requests.get(api_url, timeout=10)
            
            if not response.ok:
                return False, f"API request failed: {response.status_code}"
            
            data = response.json()
            files = data.get('_aFiles', [])
            
            if not files or not isinstance(files, list) or len(files) == 0:
                return False, "No files found in API response"
            
            first_file = files[0]
            if not isinstance(first_file, dict):
                return False, "Invalid file data format"
            
            download_url = first_file.get('_sDownloadUrl')
            if not download_url:
                return False, "No download URL found"
            
            if progress_callback:
                progress_callback(10, 100, "Starting download...")
            
            # Download with progress tracking
            file_response = requests.get(download_url, stream=True, timeout=30)
            
            if not file_response.ok:
                return False, f"Download failed: {file_response.status_code}"
            
            filename = f"mod_{mod_id}.zip"
            filepath = os.path.join(self.install_path, filename)
            
            # Get file size for progress
            total_size = int(file_response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in file_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = 10 + int((downloaded / total_size) * 80)
                            progress_callback(progress, 100, f"Downloading... {downloaded}/{total_size} bytes")
            
            if progress_callback:
                progress_callback(90, 100, "Download complete!")
            
            return True, filename
            
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {e}"
        except Exception as e:
            return False, f"Error downloading mod: {e}"
    
    def install_mod(self, mod_file, extract=True, progress_callback=None):
        """
        Install/extract the downloaded mod
        
        Args:
            mod_file: Filename of the downloaded mod
            extract: Whether to extract the zip file
            progress_callback: Optional callback function(current, total, message)
        
        Returns:
            tuple: (success, extract_path_or_error_message)
        """
        try:
            filepath = os.path.join(self.install_path, mod_file)
            
            if not os.path.exists(filepath):
                return False, f"File not found: {filepath}"
            
            if not extract:
                return True, filepath
            
            if not zipfile.is_zipfile(filepath):
                return False, f"{mod_file} is not a valid zip file"
            
            if progress_callback:
                progress_callback(90, 100, "Extracting...")
            
            extract_path = os.path.join(self.install_path, f"mod_{mod_file.replace('.zip', '')}")
            os.makedirs(extract_path, exist_ok=True)
            
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            if progress_callback:
                progress_callback(100, 100, "Installation complete!")
            
            return True, extract_path
            
        except Exception as e:
            return False, f"Error installing mod: {e}"
    
    def handle_url(self, url, progress_callback=None, extract=True):
        """
        Complete handler for GameBanana URL
        
        Args:
            url: GameBanana URL (gamebanana://install/12345)
            progress_callback: Optional callback function(current, total, message)
            extract: Whether to extract the downloaded mod
        
        Returns:
            tuple: (success, result_dict_or_error_message)
        """
        if not url.startswith('gamebanana://'):
            return False, "Invalid URL format"
        
        info = self.parse_gamebanana_url(url)
        
        if info['action'] != 'install' or not info['mod_id']:
            return False, f"Unsupported action or missing mod ID"
        
        # Download
        success, result = self.download_mod(info['mod_id'], progress_callback)
        if not success:
            return False, result
        
        mod_file = result
        
        # Install
        success, result = self.install_mod(mod_file, extract, progress_callback)
        if not success:
            return False, result
        
        return True, {
            'mod_id': info['mod_id'],
            'mod_file': mod_file,
            'install_path': result
        }


# Standalone CLI functionality
def main():
    print("GameBanana 1-Click Handler")
    print("-" * 40)
    
    handler = GameBananaHandler()
    
    if len(sys.argv) == 1:
        print("\nUsage:")
        print("  Register protocol handler: python script.py --register")
        print("  Handle URL: python script.py gamebanana://install/12345")
        return
    
    if sys.argv[1] == '--register':
        success, message = handler.register_protocol_handler()
        print(message)
        return
    
    gamebanana_url = sys.argv[1]
    
    if gamebanana_url.startswith('gamebanana://'):
        def progress(current, total, message):
            print(f"[{current}/{total}] {message}")
        
        success, result = handler.handle_url(gamebanana_url, progress_callback=progress)
        
        if success:
            print("\n✓ Mod installed successfully!")
            print(f"Mod ID: {result['mod_id']}") #type: ignore
            print(f"Location: {result['install_path']}") #type: ignore
        else:
            print(f"\n✗ Failed: {result}")
    else:
        print(f"Invalid URL format. Expected gamebanana:// URL")


if __name__ == "__main__":
    main()