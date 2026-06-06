# ota_mgr.py
# -*- coding: UTF-8 -*-

import request
import uos
import machine
import utime
from config import Config

class OTAManager:
    def __init__(self):
        self.update_url = Config.OTA_UPDATE_URL

    def check_and_update(self):
        print("\n--- 🔄 OTA UPDATE ENGINE STARTED ---")
        print("[OTA] Connecting to Server:", self.update_url)
        
        try:
            # ૧. ઇન્ટરનેટ પરથી નવી ફાઇલ ડાઉનલોડ કરો
            response = request.get(self.update_url)
            
            if response.status_code == 200:
                print("[OTA] Code Downloaded! Size: {} bytes".format(len(response.text)))
                
                # ૨. સેફ્ટી: નવી ફાઇલને 'main_new.py' તરીકે સેવ કરો (ઓવરરાઇટ ન કરો)
                with open('/usr/main_new.py', 'w') as f:
                    f.write(response.text)
                print("[OTA] Saved temporarily as 'main_new.py'.")
                
                # ૩. સ્વેપિંગ લોજિક (જૂની કાઢો, નવી લગાવો)
                print("[OTA] Swapping files safely...")
                try:
                    uos.remove('/usr/main.py') # જૂની ફાઇલ ડિલીટ
                except Exception as e:
                    print("[OTA] Remove old file info:", e)
                    
                uos.rename('/usr/main_new.py', '/usr/main.py') # નવી ફાઇલને મેઈન બનાવી દો
                
                print("[OTA SUCCESS] Firmware updated successfully!")
                print("[OTA] System will REBOOT in 3 seconds to apply changes...\n")
                utime.sleep(3)
                
                # ૪. મોડ્યુલ હાર્ડ-રીસેટ (રીબૂટ)
                machine.reset()
                
            else:
                print("[OTA ERROR] Server returned HTTP Code:", response.status_code)
                
        except Exception as e:
            print("[OTA CRITICAL] Update process failed: {}".format(e))