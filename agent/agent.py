from winotify import Notification
from cryptography.fernet import Fernet
from hashlib import sha256

import sys
import json
import os
import time
import base64
import re
import keyring
import uuid
import psutil
import threading
import pymem
import traceback
import tkinter
import requests
import win32process
import tkinter.messagebox as messagebox

import _unprotected

FERNET = Fernet(bytes(keyring.get_password("GuardianStealerBlocker", os.getlogin()), encoding="utf-8"))
foundPid = []
blackList = ["python"]
allowList = [f"{os.getenv('APPDATA')}/Gardian"]
pathProcess = {}

def update_current(_data):
    data = json.loads(open(DATA_FILE, "r").read())
    data.update(_data)
    open(DATA_FILE, "w").write(json.dumps(data, indent=4))

def search():
    global foundPid
    data = json.loads(open(DATA_FILE, "r").read())
    if not data["settings"]["process-scan-active"]:
        return
    while True:
        for proc in list(set(win32process.EnumProcesses()) - set(foundPid)):
            foundPid.append(proc)
            try:
                proc = psutil.Process(proc)
                threading.Thread(target=pre_protect, args=(proc, data, )).start()
            except: pass
        time.sleep(1)
     
def pre_protect(proc, data):
    global pathProcess
    try:              
        processExe = proc.exe()
        
        python = None
        if proc.name() == "python.exe":
            if len(proc.cmdline()) > 1:
                python = proc.cmdline()[1].replace("\\", "/")
                if ":" not in python:
                    python = os.path.join(proc.cwd(), python)
            else:
                return
                
        if python == None:
            path = processExe
        else:
            path = python
            
        if any(allow.lower().replace("\\", "/") in path.lower().replace("\\", "/") for allow in allowList):
            return
        if any(folder.lower().replace("\\", "/") in path.lower().replace("\\", "/") for folder in data["settings"]["process-scan-filter-folders"]) and (not data["settings"]["process-scan-only-folder-filter"]):
            return
        if (not any(folder.lower().replace("\\", "/") in path.lower().replace("\\", "/") for folder in data["settings"]["process-scan-filter-folders"])) and data["settings"]["process-scan-only-folder-filter"]:
            return
        
        if (processExe not in data["trusted_exe"] or any(blocked in processExe.lower() for blocked in blackList)) and ":" in processExe and proc.pid != os.getpid():
            proc.suspend()
            print("PID==PID: ", proc.pid, os.getppid())
            print(f"{proc.pid} {proc.name()} {processExe}")
            if path not in pathProcess:
                pathProcess[path] = [proc]
                if data["settings"]["process-ask-before"]:
                    root = tkinter.Tk()
                    root.withdraw()
                    root.wm_attributes('-topmost', 1)
                    result = messagebox.askyesno("Guardian - Unknown process", f"""💬 This process is unknown, do you want to scan it? ?
                                                
    📂 {path}""", icon = 'warning', parent=root)
                    root.destroy()
                    if result:
                        for process in pathProcess[path]:
                            threading.Thread(target=protect, args=(process,)).start()
                            
                        stats = json.loads(open(DATA_FILE, "r").read()).get("stats")
                        update_current({
                            "stats": {
                                "securized_data": stats.get("securized_data"),
                                "token_grabber_detection": stats.get("token_grabber_detection"),
                                "ip_grabber_detection": stats.get("ip_grabber_detection"),
                                "stealer_detection": stats.get("stealer_detection"),
                                "process_scanned": stats.get("process_scanned") + len(pathProcess[path])
                            }
                        })
                        del pathProcess[path]

                    else:
                        for process in pathProcess[path]:
                            process.resume()
                        del pathProcess[path]
                        with open(DATA_FILE, "w", encoding="utf-8") as f:
                            data["trusted_exe"].append(proc.exe())
                            f.write(json.dumps(data, indent=4))
                else:
                    for process in pathProcess[path]:
                        print(process)
                        threading.Thread(target=protect, args=(process,)).start()
                    del pathProcess[path]
            else:
                pathProcess[path].append(proc)
            
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
        
def delete_variable(pm, regex):
    for i in range(10):
        threading.Thread(target=_delete_variable, args=(pm, regex,)).start()

def _delete_variable(pm, regex):
    try:
        addr = pm.pattern_scan_all(bytes(regex, encoding="utf8"))
        if addr != None:
            print(f"{pm.process_id} - Token Address Found:", hex(addr))
            var = pm.read_string(addr, 59)
            print(f"{pm.process_id} - Before Memory Edit:", var)
            pm.write_string(addr, "." * len(var))
            print(f"{pm.process_id} - After Memory Edit:", pm.read_string(addr))
    except Exception as e:
        print(f"{pm.process_id} - ERROR ({e})")

def protect(process):
    global foundPid
    try:
        pm = pymem.Pymem(process.pid)

        token = r"[\w-]{24}\.[\w-]{6}\.[\w-]{27,38}|mfa\.[\w-]{84}|%s" % IP
        kill_or_delete = None
        
        scans = {
            "freeze": 10
        }
        
        python = None
        if process.name() == "python.exe":
            python = process.cmdline()[1].replace("\\", "/")
            if "/" not in python:
                python = os.path.join(process.cwd(), python)
                
        if python == None:
            path = process.exe()
        else:
            path = python

        print(f"Checking process {process.name()} ({process.pid}) - {process.exe()}")
        
        token_grabber_addr = pm.pattern_scan_all(bytes("W(4|A)SP( Stealer)?|Plague|Mercurial Grabber", encoding="utf8"))
        if token_grabber_addr != None:
            stats = json.loads(open(DATA_FILE, "r").read()).get("stats")
            update_current({
                "stats": {
                    "securized_data": stats.get("securized_data"),
                    "token_grabber_detection": stats.get("token_grabber_detection"),
                    "ip_grabber_detection": stats.get("ip_grabber_detection"),
                    "stealer_detection": stats.get("stealer_detection") + 1,
                    "process_scanned": stats.get("process_scanned")
                }
            })
            root = tkinter.Tk()
            root.withdraw()
            root.wm_attributes('-topmost', 1)
            if "Plague" in pm.read_string(token_grabber_addr):
                messagebox.showerror("Guardian -  Plague detected", f"""⛔ Plague was injected into this process!
                                                    
    📂 {path}""")
                
            elif "Mercurial Grabber" in pm.read_string(token_grabber_addr):
                messagebox.showerror("Guardian -  Mercurial Grabber detected", f"""⛔ Mercurial Grabber was injected into this process!
                                                    
    📂 {path}""")
                
            else:
                messagebox.showerror("Guardian -  WASP Stealer detected", f"""⛔ WASP Stealer was injected into this process!
                                                    
    📂 {path}""")
            root.destroy()
            process.kill()
            return

        while True:
            try:
                start = time.time()
                addr = pm.pattern_scan_all(bytes(token, encoding="utf8"))
                print(f"{process.pid} - {round((time.time() - start) * 1000)}ms to search in memory")
                    
                messages = {
                    "token": "This process is possibly a token grab, do you want to close the program (yes), or remove the token from the process (no)",
                    "ip": "This process is possibly an IP grabber, do you want to close the program (yes), or remove your IP address from the process (no)",
                }
                    
                if addr != None:
                    
                    data_found = pm.read_string(addr)
                    print(data_found)
                    data_type = "token"
                    if IP in data_found:
                        data_type = "ip"
                        
                        stats = json.loads(open(DATA_FILE, "r").read()).get("stats")
                        update_current({
                            "stats": {
                                "securized_data": stats.get("securized_data"),
                                "token_grabber_detection": stats.get("token_grabber_detection"),
                                "ip_grabber_detection": stats.get("ip_grabber_detection") + 1,
                                "stealer_detection": stats.get("stealer_detection"),
                                "process_scanned": stats.get("process_scanned")
                            }
                        })
                    else:
                        stats = json.loads(open(DATA_FILE, "r").read()).get("stats")
                        update_current({
                            "stats": {
                                "securized_data": stats.get("securized_data"),
                                "token_grabber_detection": stats.get("token_grabber_detection") + 1,
                                "ip_grabber_detection": stats.get("ip_grabber_detection"),
                                "stealer_detection": stats.get("stealer_detection"),
                                "process_scanned": stats.get("process_scanned")
                            }
                        })
                    
                    if kill_or_delete == None:
                        root = tkinter.Tk()
                        root.withdraw()
                        root.wm_attributes('-topmost', 1)
                        kill_or_delete = messagebox.askyesno("Guardian -  Stealer Suspicion", f"""⚠️ {messages[data_type]}
                                                             
    📂 {path}""",icon = 'warning')
                        root.destroy()
                    if kill_or_delete:
                        process.kill()
                        return
                    else:
                        delete_variable(pm, token)
                else:
                    if scans["freeze"] > 0:
                        process.resume()
                        time.sleep(0.5)
                        process.suspend()
                        scans["freeze"] -= 1
            except Exception as e:
                print(f"{process.pid} - ERROR ({e})")
                print(traceback.format_exc())
                break

        foundPid.remove(process.pid)

    except Exception as e:
        print(f"{process.pid} - ERROR ({e})")
        print(traceback.format_exc())

def path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def add_secure_info(value, _bytes=False):
    encoded_info = FERNET.encrypt(value.encode()).decode()
    data = json.loads(open(DATA_FILE, "r").read())
    hashed_value = sha256(value.encode()).hexdigest()
    notify = json.loads(open(DATA_FILE, "r").read())["settings"]["notifications"]

    for _hash in data["hash_to_uuid"]:
        if hashed_value == _hash:
            return "{Guardian.uuid}".replace("uuid", data["hash_to_uuid"][_hash]) if not _bytes else bytes("{Guardian.uuid}".replace("uuid", data["hash_to_uuid"][_hash]), encoding="utf8")

    if notify:
        Notification(app_id="Guardian - Stealer Blocker",
                        title="Security",
                        msg="Securing new information",
                        icon=path("logo.ico")).show()

    info_uuid = str(uuid.uuid4())

    data["secure_info"][info_uuid] = encoded_info
    data["hash_to_uuid"][hashed_value] = info_uuid
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=4))
        
    stats = json.loads(open(DATA_FILE, "r").read()).get("stats")
    update_current({
        "stats": {
            "securized_data": stats.get("securized_data") + 1,
            "token_grabber_detection": stats.get("token_grabber_detection"),
            "ip_grabber_detection": stats.get("ip_grabber_detection"),
            "stealer_detection": stats.get("stealer_detection"),
            "process_scanned": stats.get("process_scanned")
        }
    })

    return "{Guardian.uuid}".replace("uuid", info_uuid) if not bytes else bytes("{Guardian.uuid}".replace("uuid", info_uuid), encoding="utf8")

def secure(tokens):
    ROAMING = os.getenv("APPDATA")
    PATHS = {
        "Discord": ROAMING + "\\Discord"
    }
    def _secure(path: str) -> list:
        path += "\\Local Storage\\leveldb"
        if os.path.isdir(path):
            for file_name in os.listdir(path):
                if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
                    continue
                data = open(f"{path}\\{file_name}", "rb").read()
                with open(f"{path}\\{file_name}", "wb") as f:
                    for token in tokens:
                        data = data.replace(bytes(token, encoding="utf8"), add_secure_info(token, True)) # Replace info with securised one
                    f.write(data)

    def _encrypt_secure(path: str):
        if not os.path.exists(f"{path}/Local State"): return []
        pathC = path + "\\Local Storage\\leveldb"
        found_tokens = []
        pathKey = path + "/Local State"
        with open(pathKey, 'r', encoding='utf-8') as f: local_state = json.loads(f.read())
        master_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
        master_key = _unprotected.CryptUnprotectData(master_key[5:])

        for file in os.listdir(pathC):
            if file.endswith(".log") or file.endswith(".ldb"):
                data = open(f"{pathC}\\{file}", "rb").read()
                for line in [x.strip() for x in open(f"{pathC}\\{file}", "rb").readlines() if x.strip()]:
                    for token in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", str(line)):
                        tokenDecoded = _unprotected.DecryptValue(base64.b64decode(token.split('dQw4w9WgXcQ:')[1]), master_key)
                        for _token in tokens:
                            if _token == tokenDecoded:
                                data = data.replace(bytes(token, encoding="utf8"), add_secure_info(token, True)) # Replace info with securised one
                with open(f"{pathC}\\{file}", "wb") as f:
                    f.write(data)
        return found_tokens

    for path in PATHS:
        _secure(PATHS[path])
        _encrypt_secure(PATHS[path])

def loaded():
    data = json.loads(open(DATA_FILE, "r").read())
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        data["agent_loaded"] = True
        f.write(json.dumps(data, indent=4))

def main():
    global DATA_FILE, IP
    DATA_FILE = keyring.get_password("GuardianStealerBlocker", "guardian_current_path")
    IP = requests.get("https://httpbin.org/ip").json()["origin"]
        
    data = json.loads(open(DATA_FILE, "r").read())
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        data["agent_pid"] = os.getpid()
        for proc in psutil.process_iter():
            try:
                if proc.exe() not in data["trusted_exe"] and ":" in proc.exe():
                    data["trusted_exe"].append(proc.exe())
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        f.write(json.dumps(data, indent=4))

    loaded()
    
    threading.Thread(target=search).start()

    while True:
        time.sleep(60)
        tokens = _unprotected.get_tokens()
        secure(tokens)

if __name__ == "__main__":
    main()