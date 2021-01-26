import os
import shutil
os.system("python3 -m venv env-macos")
os.system("./env-macos/bin/pip install -r requirements.txt")
shutil.copyfile("src/build/fix/macos/(pyinstaller_fix)_hook-_tkinter.py", "env-macos/lib/python3.7/site-packages/PyInstaller/hooks/hook-_tkinter.py")
shutil.copyfile("src/build/fix/macos/(pyinstaller_build_fix)_osx.py", "env-macos/lib/python3.7/site-packages/PyInstaller/building/osx.py")
shutil.copyfile("src/build/fix/(pydub_fix)_audio_segment.py", "env-macos/lib/python3.7/site-packages/pydub/audio_segment.py")