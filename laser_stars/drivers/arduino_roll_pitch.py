
import serial

class ArduinoRollPitchDriver():
    def __init__(self, roll_0, roll_1, pitch_0, pitch_1, com_port=None):
        self.roll_0 = roll_0
        self.roll_1 = roll_1
        self.pitch_0 = pitch_0
        self.pitch_1 = pitch_1
        if com_port:
            self.serial = serial.Serial(com_port)
        else:
            self.serial = None

    def move_to(self, x, y):
        pass

    def set_power(self):
        pass
