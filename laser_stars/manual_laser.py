

import serial
import math
import time

com_port = "COM6"

_CMD_ROLL = 100
_CMD_PITCH = 101
_CMD_POWER = 102

cmd_map = {
    'r': _CMD_ROLL,
    'i': _CMD_PITCH,
    'p': _CMD_POWER
}

ser = serial.Serial(com_port, baudrate=115200, timeout=3)
header = ser.read()
assert len(header) == 1
assert header[0] == 255


def _send_cmd(cmd, val):
    data = bytearray([cmd, val & 255, (val >> 8) & 255])
    print(data)
    ser.write(data)


while True:
    cmd = input("[r i p] x  or q: ")
    if cmd == 'q':
        ser.close()
        exit()
    pts = cmd.split()
    try:
        cmd = cmd_map[pts[0]]
        val = int(pts[1])
    except:
        continue
    _send_cmd(cmd, val)
    # resp = ser.read(4)
    # print(resp)

# r 1024 = 0deg
# r 600 = ~45
# r 1300 = ~-45

# i 950 = 0deg
# i  