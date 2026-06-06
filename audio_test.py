# audio_test.py
# -*- coding: UTF-8 -*-

import audio
import uos
import utime
from machine import Pin

print("\n=== 🔍 QUECPYTHON AUDIO DIAGNOSTIC TOOL ===")

AUDIO_FILE = "U:/alert.amr"

# ૧. ફાઈલ સિસ્ટમ વેરિફિકેશન
try:
    f_stat = uos.stat("/usr/alert.amr")
    print("[FILE INFO] File found in flash memory. Size: {} bytes".format(f_stat[6]))
except Exception as e:
    print("[CRITICAL] File check failed on /usr/alert.amr: {}".format(e))

def diagnostic_cb(event):
    print("[EVENT CALLBACK] Hardware Triggered Event ID: {}".format(event))
    if event == 0:   print(" -> Meaning: Playback Started.")
    elif event == 5: print(" -> Meaning: Buffer Empty / Silent Mode.")
    elif event == 7: print(" -> Meaning: Playback Finished / Closed.")

# ૨. હાર્ડવેર ઇનિશિયલાઇઝેશન
try:
    # કૉલ વગર ચેનલ 2 (Speaker) વેરિફાય કરો
    aud = audio.Audio(2)
    aud.setCallback(diagnostic_cb)
    aud.setVolume(11)
    print("[HARDWARE] Audio Engine successfully initialized on Channel 2.")
except Exception as e:
    print("[CRITICAL] Audio Hardware Object Creation Failed: {}".format(e))

# ૩. પ્લેબેક અને લાઈવ સ્ટેટ મોનિટરિંગ ટેસ્ટ
def run_diagnostic_play():
    try:
        print("\n[TEST] Triggering Audio.play()...")
        # priority=2, breakin=1
        result = aud.play(2, 1, AUDIO_FILE)
        print("[TEST] Function Return Value (Should be 0 for Success): {}".format(result))
        
        # આગામી ૬ સેકન્ડ સુધી દર ૫૦૦ms એ ઓડિયો હાર્ડવેરનું સ્ટેટસ ચેક કરો
        print("[TEST] Polling hardware state for the next 6 seconds...")
        for i in range(12):
            # getState() -> 0: IDLE, 1: PLAYING, 2: PAUSED
            hw_state = aud.getState()
            print(" -> Time: {}s | Internal Hardware State: {}".format(i*0.5, hw_state))
            utime.sleep_ms(500)
            
        aud.stop()
        print("[TEST] Diagnostic Play Sequence Completed.")
    except Exception as e:
        print("[ERROR] Exception during diagnostic play: {}".format(e))

# ટેસ્ટ રન કરો
run_diagnostic_play()