# -*- coding: utf-8 -*-
import serial
import subprocess
import os
import time
import re
import BeautifulSoup
import requests
from blynkapi import Blynk


auth = "2261c143d6f84d42a2bce2fa0aad2cb9"
start_button = Blynk(auth, pin="V3")

areas = {"V2":["blabla"]}
areas_to_clean = []

while 1:
    if start_button.get_val()[0] == "1":
        print('Start cleaning')
        for t in areas.keys():
            button = Blynk(auth, pin=t)
            if button.get_val()[0] == "1":
                areas_to_clean.append(areas[t])
        print areas_to_clean
        start_button.off()
        #os.system("sudo /home/pi/Downloads/ttyecho -n /dev/tty1 kodi")
        time.sleep(5)

