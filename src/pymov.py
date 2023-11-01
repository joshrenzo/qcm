import serial
from time import sleep


class valves:
    def __init__(
        self,
        port="/dev/tty.usbmodem12201",
        baudrate=9600,
        valves_available=["1", "2", "3", "4"],
        valve_status=["0", "0", "0", "0", "0"],
    ):
        self.valves_available = valves_available
        self.valve_status = valve_status
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(
            self.port,
            self.baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0,
            xonxoff=False,
        )
        sleep(5)

    def open_valve(self, mod_valve):
        sleep(5)
        mod_valve = [i for i in mod_valve]
        for valve in mod_valve:
            if valve not in self.valves_available:
                print("Valve not Available")
            else:
                self.valve_status[int(valve) - 1] = "1"
        valve_str = ""
        for i in self.valve_status:
            valve_str += i
        self.ser.write(valve_str.encode(encoding="ascii", errors="strict"))
        # return valve_str

    def close_valve(self, mod_valve):
        sleep(5)
        mod_valve = [i for i in mod_valve]
        for valve in mod_valve:
            if valve not in self.valves_available:
                print("Valve not Available")
            else:
                self.valve_status[int(valve) - 1] = "0"
        valve_str = ""
        for i in self.valve_status:
            valve_str += i
        self.ser.write(valve_str.encode(encoding="ascii", errors="strict"))
        # return valve_str

    def stop(self):
        self.close_valve("1234")


if __name__ == "__main__":
    # valve_modify = input("Valve/s to modify: ")
    # valve_modify = [i for i in valve_modify]
    # valve_modify = ["1"]
    valve = valves()
    valve.open_valve("1234")
    valve.close_valve("23")
    valve.open_valve("3")
    valve.stop()
    """
    valves = valves()
    operation = input("Open('o') / Close('c'): \n")
    while operation != "end":
        valve_modify = input("Valve/s to modify: ")
        valve_modify = [i for i in valve_modify]
        if operation == "o":
            val_op = valves.open_valve(valve_modify)
            print(val_op)
        elif operation == "c":
            val_cl = valves.close_valve(valve_modify)
            print(val_cl)
        else:
            print("Operation not avaialble ")
        operation = input("open('o')/close('c'): \n")
    """
