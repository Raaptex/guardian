import os
import shutil
import sys
import winshell
import win32com.client
import psutil
import json
import winreg

APPDATA = os.getenv('APPDATA').replace("\\", "/")
GUARDIAN_PATH = os.path.join(APPDATA, "Guardian").replace("\\", "/")
AGENT_PATH = os.path.join(GUARDIAN_PATH, "agent").replace("\\", "/")

def _path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def update():
    try:
        try:
            os.system(f'kill {json.loads(open(os.path.join(GUARDIAN_PATH, "current.json"), "r").read())["agent_pid"]}')
            try:
                psutil.Process(json.loads(open(os.path.join(GUARDIAN_PATH, "current.json"), "r").read())["agent_pid"])
                raise Exception("guardian_still_here")
            except Exception as e: 
                if e == "guardian_still_here":
                    raise Exception(e)
        except: 
            input("Unable to kill guardian agent, try running in administrator mode")
            return

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
        
        if os.path.exists(_path("guardian-uninstall.exe").replace("\\", "/")):
            os.remove(_path("guardian-uninstall.exe").replace("\\", "/"))
            
        try:shutil.move(_path("guardian-uninstall.exe").replace("\\", "/"), APPDATA.replace("\\", "/")) # Done
        except: pass
        
        try:os.remove(os.path.join(GUARDIAN_PATH, "Guardian.exe").replace("\\", "/")) # Done
        except: pass
        try:shutil.rmtree(AGENT_PATH) # Done
        except: pass
        
        shutil.move(_path("Guardian.exe").replace("\\", "/"), GUARDIAN_PATH.replace("\\", "/")) # Done
        if os.path.exists(os.path.join(GUARDIAN_PATH, "current.json").replace("\\", "/")):
            with open(os.path.join(GUARDIAN_PATH, "current.json").replace("\\", "/"), "r") as current:
                old_jzed = json.loads(current.read())
                jzed = json.loads(open(_path("current.json").replace("\\", "/"), "r").read())
                for key in jzed:
                    old_jzed.setdefault(key, jzed[key])
                with open(os.path.join(GUARDIAN_PATH, "current.json").replace("\\", "/"), "w") as f:
                    f.write(json.dumps(old_jzed))
        else:
            shutil.move(_path("current.json").replace("\\", "/"), GUARDIAN_PATH.replace("\\", "/")) # Done
        os.mkdir(AGENT_PATH.replace("\\", "/"))
        shutil.move(_path("agent.exe").replace("\\", "/"), AGENT_PATH.replace("\\", "/")) # Done
        os.rename(os.path.join(AGENT_PATH, "agent.exe").replace("\\", "/"), os.path.join(AGENT_PATH, "GuardianAgent.exe").replace("\\", "/")) # Done

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
        if not os.path.exists(f'{DISCORD_PATH}/app.exe'):
            os.rename(f'{DISCORD_PATH}/Discord.exe', f'{DISCORD_PATH}/app.exe')
        else:
            os.remove(os.path.join(DISCORD_PATH, "Discord.exe")) 
        shutil.move(_path("discord-agent.exe").replace("\\", "/"), DISCORD_PATH.replace("\\", "/")) # Done
        os.rename(os.path.join(DISCORD_PATH, "discord-agent.exe").replace("\\", "/"), os.path.join(DISCORD_PATH, "Discord.exe").replace("\\", "/"))

        input("Guardian is updated !")
    except Exception as e: 
        print(f"Error: {e}")

def main():
    if os.path.exists(GUARDIAN_PATH) and os.path.isdir(os.path.exists(GUARDIAN_PATH)):
        print("Guardian is already installed")
        if input("Update it ? (Y/n)").lower() == "n":
            return
        else:
            update()
            return
    elif os.path.exists(GUARDIAN_PATH) and (not os.path.isdir(os.path.exists(GUARDIAN_PATH))):
        try:
            os.remove(GUARDIAN_PATH)
        except:
            shutil.rmtree(GUARDIAN_PATH)
        
    os.mkdir(GUARDIAN_PATH)

    if os.path.exists(_path("guardian-uninstall.exe").replace("\\", "/")):
        os.remove(_path("guardian-uninstall.exe").replace("\\", "/"))
    try:
        shutil.move(_path("guardian-uninstall.exe").replace("\\", "/"), APPDATA.replace("\\", "/")) # Done
    except: pass
    shutil.move(_path("Guardian.exe").replace("\\", "/"), GUARDIAN_PATH.replace("\\", "/")) # Done
    shutil.move(_path("current.json").replace("\\", "/"), GUARDIAN_PATH.replace("\\", "/")) # Done
    os.mkdir(AGENT_PATH.replace("\\", "/"))
    shutil.move(_path("agent.exe").replace("\\", "/"), AGENT_PATH.replace("\\", "/")) # Done
    os.rename(os.path.join(AGENT_PATH, "agent.exe").replace("\\", "/"), os.path.join(AGENT_PATH, "GuardianAgent.exe").replace("\\", "/")) # Done

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
    if not os.path.exists(f'{DISCORD_PATH}/app.exe'):
        os.rename(f'{DISCORD_PATH}/Discord.exe', f'{DISCORD_PATH}/app.exe')
    else:
        os.remove(os.path.join(DISCORD_PATH, "Discord.exe")) 
    shutil.move(_path("discord-agent.exe").replace("\\", "/"), DISCORD_PATH.replace("\\", "/")) # Done
    os.rename(os.path.join(DISCORD_PATH, "discord-agent.exe").replace("\\", "/"), os.path.join(DISCORD_PATH, "Discord.exe").replace("\\", "/"))

    desktop = winshell.desktop()
    path = os.path.join(desktop, 'Guardian.lnk')
    target = os.path.join(GUARDIAN_PATH, "Guardian.exe")
    icon = os.path.join(GUARDIAN_PATH, "Guardian.exe")
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.IconLocation = icon
    shortcut.save()

    input("Guardian is installed !")
    
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        input(f"ERROR: {e}")