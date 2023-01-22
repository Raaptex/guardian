import os
import shutil
import sys
import winshell
import winreg
import psutil
import json

APPDATA = os.getenv('APPDATA').replace("\\", "/")
GUARDIAN_PATH = os.path.join(APPDATA, "Guardian").replace("\\", "/")
AGENT_PATH = os.path.join(GUARDIAN_PATH, "agent").replace("\\", "/")

def path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    if input("Uninstalling Guardian will reset your token the next time you launch Discord\nContinue ? (Y/n)").lower() == "n":
        return

    try:
        try:
            p = psutil.Process(json.loads(open(os.path.join(GUARDIAN_PATH, "current.json"), "r").read())["agent_pid"])
            p.kill()
        except: pass

        shutil.rmtree(GUARDIAN_PATH)

        DISCORD_PATH = None
        APPDATA = os.path.dirname(os.getenv('APPDATA'))
        for dir in os.listdir(fr"{APPDATA}\Local\discord"):
            if "app-" in dir and os.path.isdir(fr"{APPDATA}\Local\discord\{dir}"):
                DISCORD_PATH = fr"{APPDATA}\Local\discord\{dir}"
                break
        if DISCORD_PATH == None:
            print("Error: discord app not found")
            input()
            return
        os.remove(f'{DISCORD_PATH}/Discord.exe')
        os.rename(f'{DISCORD_PATH}/app.exe', f'{DISCORD_PATH}/Discord.exe')

        try:
            desktop = winshell.desktop()
            os.remove(f'{desktop}/Guardian.lnk'.replace("\\", "/"))
        except: pass

        try:
            with winreg.OpenKey(
                        key=winreg.HKEY_CURRENT_USER,
                        sub_key=r'Software\Microsoft\Windows\CurrentVersion\Run',
                        reserved=0,
                        access=winreg.KEY_ALL_ACCESS,
                ) as key:
                    winreg.DeleteValue(key, "Guardian")
        except: pass

        input("Guardian is uninstalled !")
    except Exception as e: 
        print(f"Error: {e}")
    
if __name__ == "__main__":
    main()