import cx_Freeze
import sys

base = None
if sys.platform == 'win32':
    base="Win32GUI"

executables = [cx_Freeze.Executable("Log Split.py", base=base)]

cx_Freeze.setup(
    name="LogSplitter",
    options= {"build_exe": {"packages": ["tkinter"], "include_files":["logpic.ico"]}},
    version = "0.01",
    description = "Log splitting program",
    executables = executables
)