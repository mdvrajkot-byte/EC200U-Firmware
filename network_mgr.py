# network_mgr.py
# -*- coding: UTF-8 -*-

import sim
import net
import utime
from config import Config

class NetworkManager:
    def __init__(self):
        print("[INFO] Network Manager Initializing...")
        
    def check_sim_status(self):
        try:
            status = sim.getStatus()
            print("[DIAGNOSTIC] Raw SIM Status Code: {}".format(status))
            
            if status == 1:
                print("[SUCCESS] SIM Card is READY and active.")
                return True
            elif status == 0:
                print("[ERROR] SIM Card is missing or Not Inserted!")
                return False
            elif status == 2:
                print("[ERROR] SIM Card is PIN locked!")
                return False
            elif status == 3:
                print("[ERROR] SIM Card is PUK locked!")
                return False
            else:
                print("[ERROR] Unknown SIM status detected: {}".format(status))
                return False
        except Exception as e:
            print("[CRITICAL ERROR] Failed to access SIM module: {}".format(e))
            return False

    def get_signal_strength(self):
        try:
            csq = net.csqQueryPoll()
            print("[DIAGNOSTIC] Raw CSQ Signal Query: {}".format(csq))
            
            if isinstance(csq, int):
                if csq == 99:
                    print("[WARNING] CSQ is 99: No Signal or Antenna is disconnected completely!")
                    return 0
                elif csq < 10:
                    print("[WARNING] Very Poor Signal Strength: {}/31. Consider moving the antenna.".format(csq))
                    return csq
                else:
                    print("[INFO] Good Signal Strength (CSQ): {}/31".format(csq))
                    return csq
            else:
                print("[ERROR] CSQ returned an invalid data type: {}".format(type(csq)))
                return 0
        except Exception as e:
            print("[ERROR] Failed to query Signal Strength: {}".format(e))
            return 0

    def wait_for_network(self, timeout_sec=45):
        print("[INFO] Starting Network Registration scan (Timeout: {}s)...".format(timeout_sec))
        start_time = utime.time()
        
        while (utime.time() - start_time) < timeout_sec:
            try:
                net_state = net.getState()
                print("[DIAGNOSTIC] Raw Network Tuple Received: {}".format(net_state))
                
                # કૌંસ (Tuple) માંથી ડેટા એક્સટ્રેક્ટ કરવાનું એનાલિસિસ
                if isinstance(net_state, (tuple, list)) and len(net_state) >= 2:
                    voice_list = net_state[0]
                    if isinstance(voice_list, (tuple, list)) and len(voice_list) > 0:
                        voice_status = voice_list[0]
                    else:
                        voice_status = voice_list
                else:
                    voice_status = net_state
                
                print("[DIAGNOSTIC] Parsed Voice Status Code: {}".format(voice_status))
                
                # સ્ટેટસ કોડ એનાલિસિસ (QuecPython Standard)
                if voice_status == 1:
                    print("[SUCCESS] Registered on Home Network!")
                    self.get_signal_strength()
                    return True
                elif voice_status == 5:
                    print("[SUCCESS] Registered on Roaming Network!")
                    self.get_signal_strength()
                    return True
                elif voice_status == 0:
                    print("[DEBUG] Not registered, searching for operator...")
                elif voice_status == 2:
                    print("[DEBUG] Not registered, searching network internally...")
                elif voice_status == 3:
                    print("[WARNING] Registration Denied by Tower! Check SIM validity.")
                elif voice_status == 4:
                    print("[WARNING] Unknown Network State.")
                
            except Exception as e:
                print("[ERROR] Exception inside network scanning loop: {}".format(e))
                
            utime.sleep(3)
            
        print("[ERROR] Network Registration Timeout! Failed to connect in time.")
        return False

    def initialize_cellular(self):
        print("\n--- Starting Cellular Setup for {} ---".format(Config.PROJECT_NAME))
        
        if not self.check_sim_status():
            print("[ANALYSIS] Setup halted: SIM card verification failed.")
            return False
            
        if not self.wait_for_network():
            print("[ANALYSIS] Setup halted: Network registration failed.")
            return False
            
        print("[SUCCESS] Cellular Network is fully operational.\n")
        return True