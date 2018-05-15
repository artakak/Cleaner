# -*- coding: utf-8 -*-
import os
import subprocess
import time
from Blynk import Blynk
import datetime
import requests
import json


ip = "192.168.1.51"
token = "37705464687a564e366a46486f675367"
auth = "7784a8e7e1084ae08ad587702494a124"
server = "192.168.1.35"
os.environ["MIROBO_IP"] = ip
os.environ["MIROBO_TOKEN"] = token

start_button = Blynk(auth, server=server, pin="V5")
stop_button = Blynk(auth, server=server, pin="V6")
get_cons = Blynk(auth, server=server, pin="V22")

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

main_brush = Blynk(auth, server=server, pin="V18")
side_brush = Blynk(auth, server=server, pin="V19")
filter = Blynk(auth, server=server, pin="V20")
sensor = Blynk(auth, server=server, pin="V21")

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

states = {0: "Unknown",
          1: "Initiating",
          2: "Sleeping",
          3: "Waiting",
          4: "?",
          5: "Cleaning",
          6: "Returning home",
          7: "?",
          8: "Charging",
          9: "Charging Error",
          10: "Pause",
          11: "Spot Cleaning",
          12: "In Error",
          13: "Shutting down",
          14: "Updating",
          15: "Docking",
          17: "Zone cleaning",
          100: "Full"}


def do_robo_cmd(cmd, params=None):
    if params:
        req = requests.get("http://192.168.1.51:9000/hooks/mirobo?method=%s&params=%s" % (cmd, params))
    else:
        req = requests.get("http://192.168.1.51:9000/hooks/mirobo?method=%s" % cmd)
    lines = req.text.splitlines()
    return json.loads(lines[-1].rstrip("\x00"))['result'][0]


def do_cmd(cmd):
    result = subprocess.check_output(cmd, shell=True)
    return result.replace("\\", r"\\").replace("\n", r"\n")


def update_app(status):
    if status['state'] in [9, 12]:
        return r"ERROR!!!\n" + str(status)
    state = states[status['state']]
    battery = status['battery']
    cleaning_duration = status['clean_time']
    fanspeed = status['fan_power']
    if state == "Zone cleaning":
        check = check_zone()
        if check:
            lcd1.set_val(check)
            power = Blynk(auth, server=server, pin=areas_powers[check])
            if fanspeed != int(float(power.get_val()[0])):
                terminal.set_val(do_robo_cmd("set_custom_mode", int(float(power.get_val()[0]))))
        else:
            lcd1.set_val(state)
        lcd2.set_val("{} W:{}%".format(str(datetime.timedelta(seconds=cleaning_duration)), fanspeed))
    else:
        lcd1.set_val(state)
        lcd2.set_val(str(battery) + " %")
    return state


def check_zone():
    #do_cmd("rsync -avz -e ssh root@192.168.1.51:/var/run/shm/SLAM_fprintf.log /srv/dev-disk-by-id-usb-PI-288_USB_2.0_Drive_100713000EC9-0-0-part1/")
    #file = open("/srv/dev-disk-by-id-usb-PI-288_USB_2.0_Drive_100713000EC9-0-0-part1/SLAM_fprintf.log", "r")
    do_cmd("rsync -avz -e ssh root@192.168.1.51:/var/run/shm/SLAM_fprintf.log .")
    file = open("SLAM_fprintf.log", "r")
    lines = file.readlines()
    if "estimate" in lines[-1]:
        d = lines[-1].split('estimate')[1].strip()
        x, y, z = map(float, d.split(' '))
        for t in areas:
            if (areas[t][0] <= 25500 + int(x*996) <= areas[t][2]) and (areas[t][1] <= 25500 + int(y*996) <= areas[t][3]):
                return areas_named[t]


while 1:
    try:
        current_status = do_robo_cmd("get_status")
        print current_status
        if "ERROR" in update_app(current_status):
            terminal.set_val(str(current_status))
        if get_cons.get_val()[0] == "1":
            consumables = do_robo_cmd("get_consumable")
            print consumables
            main_brush.set_val(str(100 - consumables['main_brush_work_time']*100/1080000))
            """side_brush.set_val(consumables[1])
            filter.set_val(consumables[2])
            sensor.set_val(consumables[3])
            terminal.set_val(r"\nConsumables get %s\n" % str(consumables))"""
            get_cons.off()
    except Exception, e:
        terminal.set_val(r"{} OMG!!!\n{}\n".format(str(datetime.datetime.now()), str(e)))
        continue
    if start_button.get_val()[0] == "1":
        if "Charging" or "Waiting" in states[current_status['state']]:
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
            try:
                start_clean = do_robo_cmd("app_zoned_clean", str(areas_to_clean).replace(" ", "").replace("[[", "[").replace("]]", "]"))
                set_fan = do_robo_cmd("set_custom_mode", int(float(power_kor.get_val()[0])))
            except Exception, e:
                terminal.set_val(r"{} OMG!!!\n{}\n".format(str(datetime.datetime.now()), str(e)))
                continue
            terminal.set_val(str(start_clean))
            start_button.off()
            time.sleep(5)
        else:
            start_button.off()
            terminal.set_val(r"\n\nCleaning denied\n")
            time.sleep(5)
        areas_to_clean = []
    if stop_button.get_val()[0] == "1":
        try:
            do_robo_cmd("app_stop")
            do_robo_cmd("app_charge")
            terminal.set_val(r'\n\nGo Home\n')
        except Exception, e:
            terminal.set_val(r"{} OMG!!!\n{}\n".format(str(datetime.datetime.now()), str(e)))
            continue
        stop_button.off()
        time.sleep(5)
    time.sleep(1)

