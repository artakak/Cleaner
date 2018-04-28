import miio

vacuum = miio.Vacuum(ip="192.168.1.51", token="37705464687a564e366a46486f675367")
cmd = vacuum.status()
cmd2 = vacuum.clean_history()
cmd3 = vacuum.clean_details(id_=cmd2.ids[0])
print(cmd)
print(cmd2)
print(cmd3)