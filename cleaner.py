# -*- coding: utf-8 -*-
import os
import subprocess
import time
from Blynk import Blynk
import re


ip = "192.168.1.51"
token = "37705464687a564e366a46486f675367"
auth = "7784a8e7e1084ae08ad587702494a124"
server = "192.168.1.35"
os.environ["MIROBO_IP"] = ip
os.environ["MIROBO_TOKEN"] = token

start_button = Blynk(auth, server=server, pin="V5")
stop_button = Blynk(auth, server=server, pin="V6")

repeat_kor = Blynk(auth, server=server, pin="V9")
power_kor = Blynk(auth, server=server, pin="V11")

repeat_room1 = Blynk(auth, server=server, pin="V12")
power_room1 = Blynk(auth, server=server, pin="V13")

repeat_room2 = Blynk(auth, server=server, pin="V14")
power_room2 = Blynk(auth, server=server, pin="V15")

repeat_kitchen = Blynk(auth, server=server, pin="V16")
power_kitchen = Blynk(auth, server=server, pin="V17")

terminal = Blynk(auth, server=server, pin="V7")

lcd1 = Blynk(auth, server=server, pin="V8")
lcd2 = Blynk(auth, server=server, pin="V10")

areas = {"V2": [21281, 24865, 24831, 26365, 1],
         "V0": [24850, 24765, 27350, 26165, 1],
         "V1": [24907, 22483, 25707, 25033, 1],
         "V4": [24851, 20140, 26901, 22540, 1],
         "V3": [21860, 20162, 24860, 24012, 1]}

areas_named = {"V0": "Hall",
               "V1": "Corridor",
               "V2": "Room1",
               "V3": "Room2",
               "V4": "Kitchen"}

areas_powers = {"Hall": "V11",
                "Corridor": "V11",
                "Room1": "V13",
                "Room2": "V15",
                "Kitchen": "V17"}

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
    fanspeed = re.findall("Fanspeed: (\d+ %)", status)[0]
    if state == "Zoned cleaning":
        check = check_zone()
        if check:
            lcd1.set_val(check)
            power = Blynk(auth, server=server, pin=areas_powers[check])
            if fanspeed != "{} %".format(str(int(float(power.get_val()[0])))):
                terminal.set_val(do_robo_cmd("mirobo fanspeed %s" % str(int(float(power.get_val()[0])))))
        else:
            lcd1.set_val(state)
        lcd2.set_val("%s W:%s" % (cleaning_duration, fanspeed))
    else:
        lcd1.set_val(state)
        lcd2.set_val(battery)
    return state


def check_zone():
    do_robo_cmd("rsync -avz -e ssh root@192.168.1.51:/var/run/shm/SLAM_fprintf.log .")
    file = open("SLAM_fprintf.log", "r")
    lines = file.readlines()
    if "estimate" in lines[-1]:
        d = lines[-1].split('estimate')[1].strip()
        x, y, z = map(float, d.split(' '))
        for t in areas:
            if (areas[t][0] <= 25500 + int(x*996) <= areas[t][2]) and (areas[t][1] <= 25500 + int(y*996) <= areas[t][3]):
                return areas_named[t]


while 1:
    if start_button.get_val()[0] == "1":
        if "Charging" in do_robo_cmd("mirobo status"):
            terminal.set_val(r'\n\nStart cleaning\n')
            for t in areas.keys():
                button = Blynk(auth, server=server, pin=t)
                if t == "V0" or t == "V1":
                    areas[t][-1] = int(float(repeat_kor.get_val()[0]))
                elif t == "V2":
                    areas[t][-1] = int(float(repeat_room1.get_val()[0]))
                elif t == "V3":
                    areas[t][-1] = int(float(repeat_room2.get_val()[0]))
                elif t == "V4":
                    areas[t][-1] = int(float(repeat_kitchen.get_val()[0]))
                if button.get_val()[0] == "1":
                    areas_to_clean.append(areas[t])
            start_clean = do_robo_cmd("mirobo raw_command app_zoned_clean '%s'" % str(areas_to_clean))
            set_fan = do_robo_cmd("mirobo fanspeed %s" % str(int(float(power_kor.get_val()[0]))))
            terminal.set_val(start_clean)
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
        print current_status
        update_app(current_status)
        #consumables = do_robo_cmd("/usr/bin/python3.5 /home/art/Документы/Cleaner/raw_mirobo.py").split(r"\n")
        #print consumables
    except Exception, e:
        terminal.set_val(r"OMG!!!\n{}\n".format(str(e)))
    time.sleep(1)

