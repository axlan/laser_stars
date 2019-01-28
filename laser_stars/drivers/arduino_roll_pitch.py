
import serial
import math
import time

class ArduinoRollPitchDriver():

    _CMD_ROLL = 100
    _CMD_PITCH = 101
    _CMD_POWER = 102

    def __init__(self, roll_offset, pitch_offset, roll_max, pitch_max, com_port=None):
        """ roll_offset (int) - servo angle (deg) to align laser straight up
            pitch_offset (int) - servo angle (deg) to align laser straight up
            roll_max (int) - max roll angle (deg). Sets scale of image
            pitch_max (int) - max pitch angle (deg). Sets scale of image
            com_port - com port for arduino serial
        """
        assert roll_max < roll_offset
        assert pitch_max < pitch_offset
        self.running = True
        self.roll_offset = int(roll_offset)
        self.pitch_offset = int(pitch_offset)
        self.h_width = math.tan(math.radians(pitch_max))
        self.h_height = math.tan(math.radians(roll_max))
        if com_port:
            self.ser = serial.Serial(com_port, baudrate=115200, timeout=3)
            header = self.ser.read()
            assert len(header) == 1
            assert header[0] == 255
        else:
            self.ser = None

    @staticmethod
    def _calc_angle_offset(val, max_val):
        is_neg = val < .5
        distance = abs(val - .5) * max_val * 2
        angle = round(math.degrees(math.atan2(distance, 1)))
        if is_neg:
            angle *= -1
        return angle


    def move_to(self, x, y):
        pitch = self._calc_angle_offset(x, self.h_width) + self.pitch_offset
        roll = self._calc_angle_offset(y, self.h_height) + self.roll_offset
        self._send_cmd(self._CMD_ROLL, roll)
        self._send_cmd(self._CMD_PITCH, pitch)

    def set_power(self, is_on):
        self._send_cmd(self._CMD_POWER, int(is_on))

    def _send_cmd(self, cmd, val):
        data = bytearray([cmd, val])
        if self.ser:
            self.ser.write(data)
        else:
            print(int(data[0]), int(data[1]))

    def __enter__(self):
        return self    

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.ser:
            self.ser.close()
        self.running = False
