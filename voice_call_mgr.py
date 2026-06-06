# voice_call_mgr.py
# -*- coding: UTF-8 -*-

import voiceCall
import audio
import utime
from config import Config

class VoiceCallManager:
    def __init__(self):
        self.is_call_active = False 
        self.aud_player = None
        
        print("\n========== AUDIO HARDWARE INIT ==========")
        try:
            self.aud_player = audio.Audio(2)
            # અહીં આપણે config.py માંથી વોલ્યુમ લઈએ છીએ
            self.aud_player.setVolume(Config.MASTER_VOLUME)
            print("[SUCCESS] Audio Engine Bound to Device 2. Volume: {}".format(Config.MASTER_VOLUME))
        except Exception as e:
            print("[ERROR] Audio Init Failed: {}".format(e))
            
        voiceCall.setCallback(self.call_status_callback)
        print("[SUCCESS] Voice Call Callback Armed.")
        print("=========================================\n")

    def call_status_callback(self, args):
        try:
            call_state = args[3] if isinstance(args, (tuple, list)) and len(args) >= 4 else args
            
            if call_state == 4: # Ringing
                print("\n[CALLBACK] Incoming Call! Auto-answering...")
                utime.sleep(1.5)
                voiceCall.callAnswer()
                    
            elif call_state == 0: # Connected
                print("[CALLBACK] Call Connected! Triggering Stream Pipeline.")
                self.is_call_active = True
                    
            elif call_state == 6: # Disconnected
                print("\n[CALLBACK] Call Disconnected. Halting Stream.")
                self.is_call_active = False
                if self.aud_player is not None:
                    try:
                        self.aud_player.stopPlayStream()
                    except:
                        pass
                    
        except Exception as e:
            print("[CALLBACK EXCEPTION] {}".format(e))