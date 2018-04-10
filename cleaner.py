# -*- coding: utf-8 -*-

import os
import subprocess
import time
from Blynk import Blynk
import re


ip = "192.168.1.51"
token = "37705464687a564e366a46486f675367"
auth = "2261c143d6f84d42a2bce2fa0aad2cb9"
os.environ["MIROBO_IP"] = ip
os.environ["MIROBO_TOKEN"] = token

start_button = Blynk(auth, pin="V5")
stop_button = Blynk(auth, pin="V6")

repeat_kor = Blynk(auth, pin="V9")
power_kor = Blynk(auth, pin="V11")

repeat_room1 = Blynk(auth, pin="V12")
power_room1 = Blynk(auth, pin="V13")

repeat_room2 = Blynk(auth, pin="V14")
power_room2 = Blynk(auth, pin="V15")

repeat_kitchen = Blynk(auth, pin="V16")
power_kitchen = Blynk(auth, pin="V17")

terminal = Blynk(auth, pin="V7")

lcd1 = Blynk(auth, pin="V8")
lcd2 = Blynk(auth, pin="V10")

areas = {"V0": [21281, 24865, 24831, 26365, 1],
         "V1": [24850, 24765, 27350, 26165, 1],
         "V2": [24907, 22483, 25707, 25033, 1],
         "V3": [24851, 20140, 26901, 22540, 1],
         "V4": [21860, 20162, 24860, 24012, 1]}
areas_to_clean = []


def do_robo_cmd(cmd):
    result = subprocess.check_output(cmd, shell=True)
    return result.replace("\\", r"\\").replace("\n", r"\n")


def update_app(status):
    if "Error" in status:
        return r"ERROR!!!\n" + status
    state = re.findall("State: ([\w\s]+)", status)[0]
    battery = re.findall("Battery: (\d+ %)", status)[0]
    cleaning_duration = re.findall("Cleaning since: (\d:\d\d:\d\d)", status)[0]
    lcd1.set_val(state)
    lcd2.set_val(battery)
    if state == "Zoned cleaning":
        lcd2.set_val(cleaning_duration)
    return state


while 1:
    if start_button.get_val()[0] == "1":
        if "Charging" in do_robo_cmd("mirobo status"):
            terminal.set_val(r'\n\nStart cleaning\n')
            for t in areas.keys():
                button = Blynk(auth, pin=t)
                if t == "V0" or t == "V1":
                    areas[t][-1] = int(repeat_kor.get_val()[0])
                elif t == "V2":
                    areas[t][-1] = int(repeat_room1.get_val()[0])
                elif t == "V3":
                    areas[t][-1] = int(repeat_room2.get_val()[0])
                elif t == "V4":
                    areas[t][-1] = int(repeat_kitchen.get_val()[0])
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
    try:
        current_status = do_robo_cmd("mirobo status")
        update_app(current_status)
    except Exception, e:
        terminal.set_val(r"OMG!!!\n{}\n".format(str(e)))
    time.sleep(5)

