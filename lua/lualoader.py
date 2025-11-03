from lupa import LuaRuntime
from pathlib import Path
import sys


class LuaModLoader:
    def __init__(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.mod_info = {}
        self.features = []
        
        # Set up the hmm (HollowKnight Mod Manager?) API
        self._setup_api()
    
    def _setup_api(self):
        """Create the hmm table and its methods in Lua"""
        # Create the hmm table
        self.lua.execute("hmm = {}")
        
        # Register Python functions that Lua can call
        self.lua.globals()['hmm']['setname'] = self._set_name
        self.lua.globals()['hmm']['setathour'] = self._set_author
        self.lua.globals()['hmm']['setdescription'] = self._set_description
        self.lua.globals()['hmm']['setversion'] = self._set_version
        self.lua.globals()['hmm']['addextfeaturevalue'] = self._add_feature_value
        self.lua.globals()['hmm']['addextfeature'] = self._add_feature
        
        # Set up package.preload so require("hmm") returns the hmm table
        self.lua.execute('''
            package.preload["hmm"] = function()
                return hmm
            end
        ''')
    
    def _set_name(self, name):
        """Set mod name"""
        self.mod_info['name'] = name
        print(f"Mod Name: {name}")
    
    def _set_author(self, author):
        """Set mod author"""
        self.mod_info['author'] = author
        print(f"Author: {author}")
    
    def _set_description(self, desc):
        """Set mod description"""
        self.mod_info['description'] = desc
        print(f"Description: {desc}")
    
    def _set_version(self, version=None):
        """Set mod version"""
        self.mod_info['version'] = version or "Unknown"
        print(f"Version: {self.mod_info['version']}")
    
    def _add_feature_value(self, feature):
        """Add a specific feature"""
        if feature:
            self.features.append(feature)
            print(f"Added feature: {feature}")
    
    def _add_feature(self, manualfeature):
        """Add manual features"""
        if manualfeature:
            # Convert Lua table to Python list if needed
            if hasattr(manualfeature, 'values'):
                features_list = list(manualfeature.values())
            else:
                features_list = [manualfeature]
            self.features.extend(features_list)
            print(f"Added manual features: {features_list}")
    
    def load_mod(self, lua_file_path):
        """Load a Lua mod file"""
        lua_path = Path(lua_file_path)
        
        if not lua_path.exists():
            print(f"Error: File {lua_file_path} not found!")
            return False
        
        print(f"\n{'='*50}")
        print(f"Loading mod from: {lua_path.name}")
        print(f"{'='*50}\n")
        
        try:
            # Execute the Lua file
            with open(lua_path, 'r', encoding='utf-8') as f:
                lua_code = f.read()
            
            self.lua.execute(lua_code)
            
            # Try to call hmm.info() if it exists
            if 'hmm' in self.lua.globals() and 'info' in self.lua.globals()['hmm']:
                print("\nCalling hmm.info()...")
                self.lua.globals()['hmm']['info']()
            
            # Try to call hmm.extfeatures() if it exists
            if 'hmm' in self.lua.globals() and 'extfeatures' in self.lua.globals()['hmm']:
                print("\nCalling hmm.extfeatures()...")
                self.lua.globals()['hmm']['extfeatures']()
            
            print(f"\n{'='*50}")
            print("Mod loaded successfully!")
            print(f"{'='*50}\n")
            
            return True
            
        except Exception as e:
            print(f"Error loading mod: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_mod_info(self):
        """Return the collected mod information"""
        return {
            'info': self.mod_info,
            'features': self.features
        }


def main():
    # Get the root directory
    curfilepath = Path(__file__)
    root = curfilepath.parent.parent.resolve()
    
    # Create loader instance
    loader = LuaModLoader()
    
    # Load the example mod
    mod_path = root / "lua" / "example.lua"
    
    if loader.load_mod(mod_path):
        # Print collected information
        info = loader.get_mod_info()
        print("\nCollected Mod Information:")
        print(f"  Info: {info['info']}")
        print(f"  Features: {info['features']}")
    

if __name__ == "__main__":
    main()