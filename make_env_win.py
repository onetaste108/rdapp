import os
import shutil
os.system("python -m venv env-win")
os.system("env-win\Scripts\pip.exe install -r ./requirements.txt")
shutil.copyfile("src/build/fix/win/(pyinstaller_depend)_bindepend.py", "env-win/Lib/site-packages/PyInstaller/depend/bindepend.py")
shutil.copyfile("src/build/fix/(pydub_fix)_audio_segment.py", "env-win/Lib/site-packages/pydub/audio_segment.py")