import argparse
import os

# OTHER
import logging, time
from signal import signal, SIGINT
import sys
import math
import serial
from queue import Queue, Empty


class alicat_flow:
    def __init__(self, port="/dev/tty.usbserial-AU0585NK", baudrate=19200):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(
            self.port,
            self.baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0,
        )

    def start_stream(self, unit_id):
        self.ser.write(f"{unit_id}@ @\r".encode())

    def poll_data(self, unit_id):
        self.ser.write(f"{unit_id}\r".encode())
        msg = ""
        count = 0
        while msg == "":
            data_a = []
            data = self.ser.readline()
            count += 1
            data = data.decode(errors="ignore")
            data_a = data.split(" ")
            data_a = [val for val in data_a if (val != "")]
            if len(data_a) > 9:
                msg = msg + data
                return msg
            elif count == 5:
                count = 0
                self.ser.write(f"{unit_id}\r".encode())

    def stop_stream(self, unit_id):
        self.ser.write(f"@@ {unit_id}\r".encode())

    def tare(self, unit_id):
        self.ser.write(f"{unit_id}V\r".encode())

    def available_gases(self, unit_id):
        self.ser.write(f"{unit_id}??G*\r".encode())
        msg = ""
        count = 0
        while msg == "":
            data = self.ser.readline()
            count += 1
            data = data.decode(errors="ignore")
            if (f"{unit_id}" in data) and ("\r" in data):
                msg = msg + data
                return msg
            elif count == 5:
                count = 0
                self.ser.write(f"{unit_id}??G*\r".encode())

    def change_gas(self, unit_id, gas_num):
        self.ser.write(f"{unit_id}G {gas_num}\r".encode())
        msg = ""
        count = 0
        while msg == "":
            data = self.ser.readline()
            count += 1
            data = data.decode(errors="ignore")
            if len(data) > 3:
                msg = msg + data
                return msg
            elif count == 5:
                count = 0
                self.ser.write(f"{unit_id}G {gas_num}\r".encode())

    def lock_display(self, unit_id):
        self.ser.write(f"{unit_id}L\r".encode())

    def unlock_display(self, unit_id):
        self.ser.write(f"{unit_id}U\r".encode())

    def read_stream(self):
        msg = ""
        while 1:
            data = self.ser.readline()
            if len(data) > 0:
                msg = msg + data.decode()
                if "\r" in msg:
                    print(msg)

    def set_units(self, unit_id, static_value, unit_value, group="1", override="0"):
        """
        unit values :
        mg/s = 64, mg/m = 65, g/s = 66, g/m = 67, g/h = 68, kg/m = 69, kg/h = 70, oz/s = 71, oz/m =72, ib/m = 73, lb/h = 74
        mass flow units:
        SL/s: 6, NmL/s: 33
        static values:
        volumetric flow = 4, mass flow = 5,
        """
        #   statistic_value      group(0:static, 1:group)      unit_value    override
        self.ser.write(
            f"{unit_id}DCU {static_value} {group} {unit_value} {override}\r".encode()
        )
        msg = ""
        count = 0
        while msg == "":
            data = self.ser.readline()
            count += 1
            data = data.decode(errors="ignore")
            if len(data) > 3:
                msg = msg + data
                return msg
            elif count == 5:
                count = 0
                self.ser.write(
                    f"{unit_id}DCU {static_value} {group} {unit_value} {override}\r".encode()
                )

    def query_unit_val_static(self, unit_id):
        self.ser.write(f"{unit_id}DCU 69\r".encode())
        msg = ""
        count = 0
        while msg == "":
            data = self.ser.readline()
            count += 1
            data = data.decode(errors="ignore")
            print(data)
            if len(data) >= 10:
                msg = msg + data
                return msg
            elif count == 5:
                count = 0
                self.ser.write(f"{unit_id}DCU 5\r".encode())

    def baud_rate(self, unit_id):
        new_baud_rate = input("New baud rate: ")
        # Baud rates: 2400,9600,19200,38400,57600,115200
        self.ser.write(f"{unit_id}NCB {self.baudrate}\r".encode())

    def change_unit_id(self, unit_id, new_unit_id):
        self.ser.write(f"{curr_unit_id}@ {new_unit_id}\r".encode())


class alicat_pressure:
    def __init__(self, port="/dev/tty.usbserial-AU0585NK", baudrate=19200):
        self.port = port
        self.baudrate = baudrate
        self.psia = ""
        self.temp = ""
        self.volum_flow = ""
        self.mass_flow = ""
        self.gas = ""
        self.ser = serial.Serial(
            self.port,
            self.baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0,
        )

    def start_stream(self, unit_id):
        self.ser.write(f"{unit_id}@=@\r".encode())

    def stop_stream(self, unit_id):
        self.ser.write(f"@@={unit_id}\r".encode())

    def tare(self, unit_id):
        self.ser.write(f"{unit_id}PC\r".encode())

    def read_stream(self):
        msg = ""
        while 1:
            data = self.ser.readline()
            if len(data) > 0:
                msg = msg + data.decode(errors="ignore")
                if "\r" in msg:
                    print(msg)

    def poll_data(self, unit_id):
        self.ser.write(f"{unit_id}\r".encode())
        msg = ""
        count = 0
        while msg == "":
            data = self.ser.readline()
            count += 1
            data = data.decode(errors="ignore")
            if (f"{unit_id}" in data) and ("\r" in data):
                msg = msg + data
                if "\r" in msg:
                    print(msg)
            elif count == 10:
                self.ser.write(f"{unit_id}\r".encode())

    def set_units(self, unit_id):
        """
        Pa = 2, hPa = 3, kPa = 4, MPa = 5, mbar = 6, bar = 7, g/cm^2 = 8, kg/cm = 9, PSI = 10, PSF = 11,
        mTorr = 12, torr = 13, mmHg = 14, inHg = 15, mmH2O = 16(4°C), mmH2O = 17(60°F), cmH2O = 18(4°C),
        mmH2O = 19(60°F), inH2O = 20(4°C), inH2O = 21(60°F), atm = 22, V = 61, count = 62, % = 63
        """
        #   statistic_value      group      unit_value    override
        self.ser.write(f"{unit_id}DCU 2 61 700 0\r".encode())
        msg = ""
        count = 0
        while msg == "":
            data = self.ser.readline()
            data = data.decode(errors="ignore")
            if (f"{unit_id}" in data) and ("\r" in data):
                msg = msg + data
                if "\r" in msg:
                    print(msg)
            elif count == 10:
                self.ser.write(f"{unit_id}DCU 2 61 700 0\r".encode())


if __name__ == "__main__":
    # alicat_pressure = alicat_pressure()
    # alicat_pressure.start_stream()
    # alicat_pressure.read_stream()
    # alicat_pressure.request_data()
    # alicat_pressure.set_units()
    # maybe_s_v = [8, 18, 4, 68, 167, 166, 100, 36, 165, 17, 81, 271, 270, 113, 49, 168]
    alicat_flow = alicat_flow()
    unit_id = input("Current unit_id: ")
    # alicat_flow.baud_rate(unit_id)
    alicat_flow.stop_stream(unit_id)
    # available_gas = alicat_flow.available_gases(unit_id)
    # print(available_gas)

    # static_value = input("Static value: ")
    # unit_value = input("Unit value: ")
    # units = alicat_flow.set_units(unit_id, i, unit_value)
    # print(units)
    gas_num = input("Gas num: ")
    alicat_flow.change_gas(unit_id, gas_num)
    data = alicat_flow.poll_data(unit_id)
    print(data)
    # new_unit_id = input("New Unit ID: ")
    # alicat_flow.change_unit_id(unit_id, new_unit_id)
    # alicat_flow.start_stream(unit_id)
    # alicat_flow.read_stream()
