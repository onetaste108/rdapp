import os
import shutil
os.system("fbs clean")
os.system("fbs freeze")
with open("target/rdapp.app/Contents/Info.plist", "r") as f:
    plist = f.read().split("/n")
with open()
plist.insert()
os.system("fbs installer")
