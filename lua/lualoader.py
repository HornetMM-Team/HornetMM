from lupa import LuaRuntime
from pathlib import Path


curfilepath = Path(__file__)
root = curfilepath.parent.parent.resolve()

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'mods\script.lua')
