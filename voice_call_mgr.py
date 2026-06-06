# voice_call_mgr.py
# -*- coding: UTF-8 -*-

import voiceCall
import audio
import utime
import modem  # 🌟 ચિપના હાર્ડવેર રજીસ્ટર હેક કરવા માટેનું પાવરફુલ મોડ્યુલ

class VoiceCallManager:
    def __init__(self):
        self.is_call_active = False 
        self.aud_player = None
        
        print("\n========== AUDIO HARDWARE INIT ==========")
        try:
            self.aud_player = audio.Audio(2)
            self.aud_player.setVolume(4)
            print("[SUCCESS] Audio Core Engine initialized on Device 2.")
        except Exception as e:
            print("[ERROR] Audio Core Initialization Failed: {}".format(e))
            
        voiceCall.setCallback(self.call_status_callback)
        print("[SUCCESS] Voice Call Interrupt Armed.")
        print("=========================================\n")

    def trigger_internal_software_loopback(self):
        # આ કમાન્ડ્સ ચિપની અંદરથી જ સ્પીકર અને માઇકને શોર્ટ કરવાનો પ્રયત્ન કરશે
        print("\n--- 🛠️ INJECTING INTERNAL AT COMMANDS ---")
        
        # ૧. Software Loopback કમાન્ડ
        res1 = modem.atACmd('AT+QAUDLOOP=1')
        print("[AT BRIDGE] AT+QAUDLOOP=1 Response: {}".format(res1.strip()))
        
        utime.sleep_ms(300)
        
        # ૨. Direct AT Playback (જો પાયથોન સ્ટ્રીમ કામ ન કરે તો સીધું C-Core થી વગાડવાનો કમાન્ડ)
        # 1 = AMR-NB, 0 = Normal path
        res2 = modem.atACmd('AT+QAUDPLAY="/usr/alert.amr",0')
        print("[AT BRIDGE] AT+QAUDPLAY Response: {}".format(res2.strip()))
        
        print("--- 🛠️ INJECTION COMPLETE ---\n")

    def call_status_callback(self, args):
        try:
            if isinstance(args, (tuple, list)) and len(args) >= 4:
                call_state = args[3] 
            else:
                call_state = args
                
            if call_state == 4: # Ringing
                print("[CALLBACK] Incoming Call! Answering in 1.5 seconds...")
                utime.sleep(1.5)
                voiceCall.callAnswer()
                    
            elif call_state == 0: # Connected
                print("[CALLBACK] Call Connected! Flipping safety flag to True.")
                self.is_call_active = True
                
                # 🌟 જેવો કૉલ કનેક્ટ થાય, તરત જ ઇન્ટરનલ રૂટીંગ ઓપન કરો
                self.trigger_internal_software_loopback()
                    
            elif call_state == 6: # Disconnected
                print("[CALLBACK] Call Disconnected. Stopping all pipelines.")
                self.is_call_active = False
                
                # કૉલ પૂરો થાય એટલે લૂપબેક અને AT પ્લેયર બંધ કરી દો
                modem.atACmd('AT+QAUDLOOP=0')
                modem.atACmd('AT+QAUDSTOP')
                
                if self.aud_player is not None:
                    try:
                        self.aud_player.stopPlayStream()
                    except:
                        pass
                    
        except Exception as e:
            print("[CALLBACK EXCEPTION] {}".format(e))