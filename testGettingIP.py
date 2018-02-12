import os,socket

result=os.popen('ipconfig')
for line in result.readlines():
	pass#print(line)
result.close()

prt = socket.gethostbyname_ex(socket.gethostname())[2][2]
print (prt)

#import fcntl
import struct

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])
	
#print (get_ip_address("Подключение по локальной сети:"))
import subprocess
#proc = subprocess.check_output("ipconfig").decode('utf-8')
#proc = subprocess.check_output("ipconfig").decode('cp1251')
proc = subprocess.check_output("ipconfig").decode('cp866')
#print (proc)
mass= proc.split(':')
print(mass[0],mass[1])

	