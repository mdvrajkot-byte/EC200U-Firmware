# main.py
# -*- coding: UTF-8 -*-

import sys
sys.path.append('usr')
sys.path.append('/usr')

import uos
import utime
from network_mgr import NetworkManager
from voice_call_mgr import VoiceCallManager


# main.py ની અંદર (ઉપરના ભાગમાં)
from ota_mgr import OTAManager

# ... (તમારું નેટવર્ક કનેક્ટ થવાનું લોજિક) ...
net_mgr = NetworkManager()
if not net_mgr.initialize_cellular():
    while True: utime.sleep(1)

# 🌟 નેટવર્ક આવ્યા પછી તરત જ OTA અપડેટ ચેક કરો
ota = OTAManager()
# ota.check_and_update() # અત્યારે આને કોમેન્ટ (બૂઝી) રાખેલું છે. જ્યારે અપડેટ કરવું હોય ત્યારે જ આને કોલ કરાવાય.

print("\n=== ⚙️ MOBILE AUTO SWITCH BOOT SEQUENCE ===")
print("\n=== OTA ===")

# --- 🔍 ડાયગ્નોસ્ટિક: ડાયરેક્ટરી સ્કેનિંગ ---
print("[DIAGNOSTIC] Current Working Directory:", uos.getcwd())
try: print("[DIAGNOSTIC] Contents of '/':", uos.listdir('/'))
except: pass
try: print("[DIAGNOSTIC] Contents of '/usr':", uos.listdir('/usr'))
except: pass
print("-------------------------------------------\n")

# ૧. નેટવર્ક કનેક્શન સેટઅપ
net_mgr = NetworkManager()
if not net_mgr.initialize_cellular():
    print("[MAIN CRITICAL] Network registration failed. Halting.")
    while True: utime.sleep(1)

# ૨. વોઈસ કૉલ મેનેજર સેટઅપ
call_mgr = VoiceCallManager()

# ૩. 🌟 માસ્ટર ફાઇલ લોકેટર: સાચો પાથ ઓટોમેટિક શોધો
FILE_PATH = None
possible_paths = ["/usr/alert.amr", "usr/alert.amr", "alert.amr", "U:/alert.amr", "/alert.amr"]

print("[MAIN] Executing robust file path discovery for 'alert.amr'...")
for path in possible_paths:
    try:
        # uos.stat ના બદલે ડાયરેક્ટ open() થી જ ચેક કરો
        with open(path, "rb") as test_file:
            pass 
        FILE_PATH = path
        print("[MAIN FILE OK] Successfully verified readable path: '{}'".format(path))
        break # સાચો પાથ મળતા જ લૂપ અટકાવી દો
    except:
        continue

if FILE_PATH is None:
    print("[MAIN CRITICAL ERROR] 'alert.amr' is MISSING or unreadable in all known paths!")
    print("[ACTION REQUIRED] Please re-upload 'alert.amr' to the 'usr' folder in QPYcom.")
else:
    print("[MAIN] System is IDLE and Standing By. Main thread monitoring armed...\n")

CHUNK_SIZE = 10 * 1024
STREAM_FORMAT = 4 

# --- મુખ્ય લૂપ ---
while True:
    try:
        if call_mgr.is_call_active and call_mgr.aud_player is not None:
            if FILE_PATH is None:
                print("[MAIN STREAM CRITICAL] Cannot play: File is missing!")
                utime.sleep(2)
                continue
                
            print("[MAIN STREAM] Active call detected. Initiating stable audio pipeline...")
            utime.sleep(1.5) 
            
            while call_mgr.is_call_active:
                try:
                    with open(FILE_PATH, "rb") as f:
                        f.read(6) # હેડર બાયપાસ
                        print("[MAIN STREAM] Playing alert track loop...")
                        
                        while call_mgr.is_call_active:
                            b = f.read(CHUNK_SIZE)
                            if not b:
                                print("[MAIN STREAM] Track EOF reached. Reloading...")
                                break 
                            
                            call_mgr.aud_player.playStream(STREAM_FORMAT, b)
                            utime.sleep_ms(20) 
                            
                    if call_mgr.is_call_active:
                        utime.sleep(4)
                        
                except Exception as file_err:
                    print("[MAIN STREAM CRITICAL] File Access Crash: {}".format(file_err))
                    utime.sleep(2)
                    break
        else:
            utime.sleep_ms(250)
            
    except KeyboardInterrupt:
        print("[MAIN] Interrupted manually.")
        break
    except Exception as global_err:
        print("[MAIN GLOBAL EXCEPTION] {}".format(global_err))
        utime.sleep(1)