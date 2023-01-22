import os
import re
import base64
from Crypto.Cipher import AES
from ctypes import windll, wintypes, byref, cdll, Structure, POINTER, c_char, c_buffer
import json
import sys
import keyring
from cryptography.fernet import Fernet

def DecryptValue(buff, master_key=None):
    starts = buff.decode(encoding='utf8', errors='ignore')[:3]
    if starts == 'v10' or starts == 'v11':
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass

class DATA_BLOB(Structure):
    _fields_ = [
        ('cbData', wintypes.DWORD),
        ('pbData', POINTER(c_char))
    ]

def GetData(blob_out):
    cbData = int(blob_out.cbData)
    pbData = blob_out.pbData
    buffer = c_buffer(cbData)
    cdll.msvcrt.memcpy(buffer, pbData, cbData)
    windll.kernel32.LocalFree(pbData)
    return buffer.raw

def CryptUnprotectData(encrypted_bytes, entropy=b''):
    buffer_in = c_buffer(encrypted_bytes, len(encrypted_bytes))
    buffer_entropy = c_buffer(entropy, len(entropy))
    blob_in = DATA_BLOB(len(encrypted_bytes), buffer_in)
    blob_entropy = DATA_BLOB(len(entropy), buffer_entropy)
    blob_out = DATA_BLOB()

    if windll.crypt32.CryptUnprotectData(byref(blob_in), None, byref(blob_entropy), None, None, 0x01, byref(blob_out)):
        return GetData(blob_out)

def decrypt():
    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")
    PATHS = {
        "Discord": ROAMING + "\\Discord"
    }
    
    def decrypt_path(path):
        if not os.path.exists(f"{path}/Local State"): return []
        pathC = path + "\\Local Storage\\leveldb"
        pathKey = path + "/Local State"
        with open(pathKey, 'r', encoding='utf-8') as f: local_state = json.loads(f.read())
        master_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
        master_key = CryptUnprotectData(master_key[5:])

        for file in os.listdir(pathC):
            if file.endswith(".log") or file.endswith(".ldb")   :
                updates = {}
                for line in [x.strip() for x in open(f"{pathC}\\{file}", errors="ignore").readlines() if x.strip()]:
                    for secure_info in re.findall(r"\{Guardian\.[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}", line):
                        encoded_info = json.loads(open(DATA_FILE, "r", encoding="utf-8").read())["secure_info"]
                        if secure_info.split(".")[1].replace("}", "") in encoded_info:
                            encoded_info = encoded_info[secure_info.split(".")[1].replace("}", "")]
                        else:
                            continue
                        info = FERNET.decrypt(encoded_info.encode()).decode()
                        updates[secure_info] = info
                
                data = open(f"{pathC}\\{file}", "rb").read()
                with open(f"{pathC}\\{file}", "wb") as f:
                    for secure_info in updates:
                        data = data.replace(bytes(secure_info, encoding="utf-8"), bytes(updates[secure_info], encoding="utf-8"))
                    f.write(data)
                        

    for path in PATHS:
        decrypt_path(PATHS[path])

DATA_FILE = keyring.get_password("GuardianStealerBlocker", "guardian_current_path")
FERNET = Fernet(bytes(keyring.get_password("GuardianStealerBlocker", os.getlogin()), encoding="utf-8"))

decrypt()
os.system(fr"start app.exe {' '.join(sys.argv[1:])}")