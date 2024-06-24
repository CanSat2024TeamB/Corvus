class Attitude:
    def __init__(self, roll: float = 0.0, pitch: float = 0.0, yaw: float = 0.0, qw: float = 1.0, qx: float = 0.0, qy: float = 0.0, qz: float = 0.0):
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.qw = qw
        self.qx = qx
        self.qy = qy
        self.qz = qz

    def get_roll(self) -> float:
        return self.roll

    def get_pitch(self) -> float:
        return self.pitch

    def get_yaw(self) -> float:
        return self.yaw

    def get_quaternion(self) -> dict:
        return {"qw": self.qw, "qx": self.qx, "qy": self.qy, "qz": self.qz}

    def get_attitude(self) -> dict:
        return {"roll": self.roll, "pitch": self.pitch, "yaw": self.yaw, "quaternion": self.get_quaternion()}

    def set_roll(self, roll: float):
        self.roll = roll

    def set_pitch(self, pitch: float):
        self.pitch = pitch

    def set_yaw(self, yaw: float):
        self.yaw = yaw

    def set_quaternion(self, qw: float, qx: float, qy: float, qz: float):
        self.qw = qw
        self.qx = qx
        self.qy = qy
        self.qz = qz

# # 使用例
# att = Attitude()
# print(att.get_attitude())  # {'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0, 'quaternion': {'qw': 1.0, 'qx': 0.0, 'qy': 0.0, 'qz': 0.0}}

# att.set_roll(10.5)
# att.set_pitch(5.2)
# att.set_yaw(3.3)
# att.set_quaternion(0.707, 0.0, 0.707, 0.0)

# print(att.get_roll())  # 10.5
# print(att.get_pitch())  # 5.2
# print(att.get_yaw())  # 3.3
# print(att.get_quaternion())  # {'qw': 0.707, 'qx': 0.0, 'qy': 0.707, 'qz': 0.0}
# print(att.get_attitude())  # {'roll': 10.5, 'pitch': 5.2, 'yaw': 3.3, 'quaternion': {'qw': 0.707, 'qx': 0.0, 'qy': 0.707, 'qz': 0.0}}
