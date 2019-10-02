import sys
from cx_Freeze import setup, Executable
import os
import sys

os.environ['TCL_LIBRARY'] = r'D:\Python35\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'D:\Python35\tcl\tk8.6'

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
# if sys.platform == "win32":
#     base = "Win32GUI"
base = "Console"

#path_platforms = ( "D:\Python35\Lib\site-packages\PyQt5\plugins\platforms\qwindows.dll", "platforms\qwindows.dll" )


#packages = ["os","tkinter","numpy","matplotlib"]
packages = ["os","numpy","matplotlib"]
includes = ["atexit","PyQt5.QtCore","PyQt5.QtGui", "PyQt5.QtWidgets"]
#includefiles = [path_platforms,"images/main.gif"]
includefiles = ["qrc_resources.py","images/","file/","caal.exe"]
excludes = [""]
    
executables = [
    Executable('mainWindow.pyw', base=base, targetName = "caalAPP.exe")
]

# Dependencies are automatically detected, but it might need fine tuning.
#build_exe_options = {"packages": packages,"includes": includes,"include_files": includefiles}
build_exe_options = {"packages": packages,"includes": includes,"include_files":includefiles}



setup(  name = "caalApp",
        version = "0.1",
        description = "CAAL GUI Application",
        options = {"build_exe": build_exe_options},
        executables = executables)
