#! /usr/bin/env python3

# import genral libraries
import os
import time
from datetime import datetime, timedelta
import sys



# import qcm libraries
from pygas import alicat_flow, alicat_pressure
from pyinfuse import Chain, Pump
from pymov import valves
from pyhot import heater
import usb


print("Loaded All Libraries")

__version__ = "0.0.1"

## find serail ports
devices = usb.list_devices()
omega_ports = []
for device in devices:
	#print('USB Serial Device {}:{}{} found @{}'.format(*device))
	print(device)
	if len(devices) == 0:
        	print('No USB Serial devices detected.')
	if "Harvard_Apparatus" in device[2]:
		pump_port = device[-1]
	if "AU0641TC" in device[2]:
		pressure_port = device[-1]
	if "AU0585NK" in device[2]:
		flow_port = device[-1]
	if "Arduino" in device[2]:
		arduino_port = device[-1]
	if "OMEGA_ENGINEERING" in device[2]:
		omega_ports.append(device[-1])
print(pump_port)
print(pressure_port)
print(flow_port)
print(arduino_port)
print(omega_ports)

# inialize instruments
# pressure and flow meter
alicat_pressure = alicat_pressure(port=pressure_port)
alicat_flow = alicat_flow(port=flow_port)

# pump
pump = Pump(Chain(pump_port),address=1)
pump.setdiameter(15.96)  # mm
pump.setflowrate(9,"ul/min")
pump.settargettime(2*60*60)


# valves
sys_valves = valves(port=arduino_port)

# Omega PID Tempreture Controller
try:
    	print("was dis one")
    	c1 = heater(port=omega_ports[0], addr=2)
    	c2 = heater(port=omega_ports[1], addr=1)
    	c1.set_thermocouple()
    	c2.set_thermocouple()
    	c1.set_action()
    	c2.set_action()
    	c1.filter_hold()
    	c2.filter_hold()
    	c1.set_PID(max_rate=1, dev_gain=1, pro_gain=8, int_gain=0, PID_setpoint=70)
    	c2.set_PID(max_rate=1, dev_gain=1, pro_gain=8, int_gain=0, PID_setpoint=70)
except:
    	print("bugga was da oda one")
    	c1 = heater(port=omega_ports[1], addr=2)
    	c2 = heater(port=omega_ports[0], addr=1)
    	c1.set_thermocouple()
    	c2.set_thermocouple()
    	c1.set_action()
    	c2.set_action()
    	c1.filter_hold()
    	c2.filter_hold()
    	c1.set_PID(max_rate=1, dev_gain=1, pro_gain=8, int_gain=0, PID_setpoint=70)
    	c2.set_PID(max_rate=1, dev_gain=1, pro_gain=8, int_gain=0, PID_setpoint=70)


date = datetime.now().isoformat()
output_data = "out/{}--testing.txt".format(date)

print("Initialized all Devices")


# Turn on Heaters
c1.run()
c2.run()
print("Heaters Activated")

# control flow
print("Opening valves 1 and 3")
sys_valves.open_valve("13")
end_time = datetime.now()+timedelta(hours=2)
while(datetime.now() < end_time):
	f = open( output_data, "a")
	data1 = "{},{},{}\n".format(datetime.now().strftime("%H:%M:%S"), c1.get_temp(), c2.get_temp())
	print(data1)
	f.write(data1)
	f.close()
	time.sleep(5)

print("Closing valve 3")
sys_valves.close_valve("3")
print("Opening valves 2 and 4")
sys_valves.open_valve("24")
pump.infuse()

end_time = datetime.now()+timedelta(hours=2)
while(datetime.now() < end_time):
	f = open(output_data, "a")
	pressure = alicat_pressure.poll_data("B")
	data1 = "{},{},{}\n".format(datetime.now().strftime("%H:%M:%S"), c1.get_temp(), c2.get_temp())
	print(data1)
	f.write(data1)
	print("\n")
	print(pressure)
	f.write(str(pressure)+'\n')
	print("\n")
	flow = alicat_flow.poll_data("A")
	f.write(str(flow)+'\n')
	f.close()
	print(flow)
	print("----------\n")
	time.sleep(5)

print("ended")
pump.stop()

c1.stop()
c2.stop()

print("Closing all")
sys_valves.close_valve("1234")




