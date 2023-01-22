from cryptography.fernet import Fernet

import threading
import webview
import eel
import json
import os
import psutil
import keyring
import winreg
import sys
import tkinter
from tkinter import filedialog

import _unprotected

VERSION = "1.3"

@eel.expose
def get_unprotected():
    return _unprotected.get_all()

@eel.expose
def get_stats():
    return json.loads(open(exe_path("current.json"), "r").read()).get("stats")

@eel.expose
def get_info(name):
    return json.loads(open(exe_path("current.json"), "r").read())[name]

@eel.expose
def set_info(name, value):
    data = json.loads(open(exe_path("current.json"), "r").read())
    data[name] = value
    open(exe_path("current.json"), "w").write(json.dumps(data, indent=4))

@eel.expose
def get_agent_status():
    data = json.loads(open(exe_path("current.json"), "r").read())
    found = False
    for proc in psutil.process_iter():
        if data['agent_pid'] == proc.pid:
            found = True
    if not found:
        data["protection_status"] = False
        open(exe_path("current.json"), "w").write(json.dumps(data, indent=4))
        return False
    return data['agent_loaded']

@eel.expose
def toggle_protection(value):
    data = json.loads(open(exe_path("current.json"), "r").read())
    data["protection_status"] = value
    open(exe_path("current.json"), "w").write(json.dumps(data, indent=4))
    kill_agent()
    if value:
        start_agent()

@eel.expose
def get_main_content(id):
    return open(path(f"interface/main_contents/{id}.html"), "r").read()

@eel.expose
def get_version():
    return VERSION

@eel.expose
def update_filter_folders():
    root = tkinter.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    dir = filedialog.askdirectory(parent=root,initialdir="C:\\",title='Please select a directory')
    root.destroy()
    if dir != "":
        data = json.loads(open(exe_path("current.json"), "r").read())
        data["settings"]["process-scan-filter-folders"].append(dir)
        open(exe_path("current.json"), "w").write(json.dumps(data, indent=4))
    return dir
    
@eel.expose
def remove_filter_folders(dir):
    data = json.loads(open(exe_path("current.json"), "r").read())
    data["settings"]["process-scan-filter-folders"].remove(dir)
    open(exe_path("current.json"), "w").write(json.dumps(data, indent=4))

@eel.expose
def update_settings(name, value):
    data = json.loads(open(exe_path("current.json"), "r").read())
    data["settings"][name] = value
    open(exe_path("current.json"), "w").write(json.dumps(data, indent=4))
    if name == "on_startup":
        set_autostart_registry("Guardian", f'{exe_path("agent/GuardianAgent.exe")}'.replace("/", "\\"), value)

@eel.expose
def get_settings():
    return json.loads(open(exe_path("current.json"), "r").read())["settings"]

def exe_path(path):
    return os.path.join(os.getenv('APPDATA'), "Guardian", path)

def path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def set_autostart_registry(app_name, key_data=None, autostart: bool = True) -> bool:
    """
    Create/update/delete Windows autostart registry key

    ! Windows ONLY
    ! If the function fails, OSError is raised.

    :param app_name:    A string containing the name of the application name
    :param key_data:    A string that specifies the application path.
    :param autostart:   True - create/update autostart key / False - delete autostart key
    :return:            True - Success / False - Error, app name dont exist
    """

    with winreg.OpenKey(
            key=winreg.HKEY_CURRENT_USER,
            sub_key=r'Software\Microsoft\Windows\CurrentVersion\Run',
            reserved=0,
            access=winreg.KEY_ALL_ACCESS,
    ) as key:
        try:
            if autostart:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, key_data)
            else:
                winreg.DeleteValue(key, app_name)
        except OSError:
            return False
    return True

def start_agent():
    data = json.loads(open(exe_path("current.json"), "r").read())
    data["agent_loaded"] = False
    open(exe_path("current.json"), "w").write(json.dumps(data, indent=4))
    os.system(f'start {exe_path("agent/GuardianAgent.exe")}')

def kill_agent():
    try:
        p = psutil.Process(json.loads(open(exe_path("current.json"), "r").read())["agent_pid"])
        p.kill()
    except: pass

def start_app():
    eel_thread = threading.Thread(target=eel_start) # Eel app start.
    eel_thread.daemon = True
    eel_thread.start() # Run eel in a seperate thread.

    webview_start() # Start pywebview web browser.

def eel_start():
    # EEL app start.
    eel.init('interface')
    eel.start("index.html", port=8000, mode=None, shutdown_delay=0.0)

def webview_start():
    global window
    # pywebview start.
    window = webview.create_window("Guardian - Stealer Blocker", 
                                   "http://localhost:8000/index.html", 
                                   width=900, height=600,
                                   background_color="#414448", 
                                   resizable=False)
    webview.start()

def main():
    if keyring.get_password("GuardianStealerBlocker", os.getlogin()) == None:
        keyring.set_password("GuardianStealerBlocker", os.getlogin(), Fernet.generate_key().decode())
    keyring.set_password("GuardianStealerBlocker", "guardian_current_path", exe_path("current.json"))
    start_app()

if __name__ == "__main__":
    main()