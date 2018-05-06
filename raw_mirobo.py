import miio
import math
#import sys

#sys.path.append("pycharm-debug-py3k.egg")

#import pydevd

#pydevd.settrace('192.168.1.49', port=12345, stdoutToServer=True, stderrToServer=True)

vacuum = miio.Vacuum(ip="192.168.1.51", token="37705464687a564e366a46486f675367")
cmd = vacuum.status()
cmd2 = vacuum.consumable_status()
#cmd3 = vacuum.clean_details(id_=cmd2.ids[0])
print(math.ceil(cmd2.main_brush_left/cmd2.main_brush_total*100))
print(math.ceil(cmd2.side_brush_left/cmd2.side_brush_total*100))
print(math.ceil(cmd2.filter_left/cmd2.filter_total*100))
print(math.ceil(cmd2.sensor_dirty_left/cmd2.sensor_dirty_total*100))
#print(cmd2)
#print(cmd3)