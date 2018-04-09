# -*- coding: utf-8 -*-

import os
import subprocess
import time
from Blynk import Blynk


ip = "192.168.1.51"
token = "37705464687a564e366a46486f675367"
auth = "2261c143d6f84d42a2bce2fa0aad2cb9"
os.environ["MIROBO_IP"] = ip
os.environ["MIROBO_TOKEN"] = token

start_button = Blynk(auth, pin="V5")
stop_button = Blynk(auth, pin="V6")
repeat = Blynk(auth, pin="V9")
terminal = Blynk(auth, pin="V7")

areas = {"V0": [21281, 24865, 24831, 26365, 1],
         "V1": [24850, 24765, 27350, 26165, 1],
         "V2": [24907, 22483, 25707, 25033, 1],
         "V3": [24851, 20140, 26901, 22540, 1],
         "V4": [21860, 20162, 24860, 24012, 1]}
areas_to_clean = []


def do_robo_cmd(cmd):
    result = subprocess.check_output(cmd, shell=True)
    return result.replace("\\", r"\\").replace("\n", r"\n")


while 1:
    if start_button.get_val()[0] == "1":
        if "Charging" in do_robo_cmd("mirobo status"):
            terminal.set_val(r'\n\nStart cleaning\n')
            for t in areas.keys():
                button = Blynk(auth, pin=t)
                areas[t][-1] = int(repeat.get_val()[0])
                if button.get_val()[0] == "1":
                    areas_to_clean.append(areas[t])
            result = do_robo_cmd("mirobo raw_command app_zoned_clean '%s'" % str(areas_to_clean))
            terminal.set_val(result)
            start_button.off()
            time.sleep(5)
        else:
            start_button.off()
            terminal.set_val(r"\n\nCleaning denied\n")
            time.sleep(5)
        terminal.set_val(do_robo_cmd("mirobo status"))
        areas_to_clean = []
    if stop_button.get_val()[0] == "1":
        terminal.set_val(r'\n\nGo Home\n')
        result = do_robo_cmd("mirobo home")
        terminal.set_val(result)
        stop_button.off()
        time.sleep(5)
        terminal.set_val(do_robo_cmd("mirobo status"))
    if "Zone" in do_robo_cmd("mirobo status"):
        current_status = do_robo_cmd("mirobo status")
        print(current_status)
    time.sleep(5)

