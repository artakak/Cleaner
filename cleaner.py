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


def check_vacuum_status():
    mirobo_cmd = "mirobo status"
    result = subprocess.check_output(mirobo_cmd, shell=True)
    return result

while 1:
    if start_button.get_val()[0] == "1":
        if "Charging" in check_vacuum_status():
            terminal.set_val(r'\n\nStart cleaning\n')
            for t in areas.keys():
                button = Blynk(auth, pin=t)
                areas[t][-1] = int(repeat.get_val()[0])
                if button.get_val()[0] == "1":
                    areas_to_clean.append(areas[t])
            mirobo_cmd = "mirobo raw_command app_zoned_clean '%s'" % str(areas_to_clean)
            result = subprocess.check_output(mirobo_cmd, shell=True)
            terminal.set_val(result.replace("\\", r"\\").replace("\n", r"\n"))
            start_button.off()
            time.sleep(5)
        else:
            start_button.off()
            terminal.set_val(r"\n\nCleaning denied\n")
            time.sleep(5)
        terminal.set_val(check_vacuum_status().replace("\\", r"\\").replace("\n", r"\n"))
        areas_to_clean = []
    if stop_button.get_val()[0] == "1":
        terminal.set_val(r'\n\nGo Home\n')
        mirobo_cmd = "mirobo home"
        result = subprocess.check_output(mirobo_cmd, shell=True)
        terminal.set_val(result.replace("\\", r"\\").replace("\n", r"\n"))
        stop_button.off()
        time.sleep(5)
        terminal.set_val(check_vacuum_status().replace("\\", r"\\").replace("\n", r"\n"))
    time.sleep(5)

