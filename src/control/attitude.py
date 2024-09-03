class Attitude: 
    def __init__(self, roll_deg = 0.0, pitch_deg = 0.0, yaw_deg = 0.0, qw = 1.0, qx = 0.0, qy = 0.0, qz = 0.0):
        self.roll: float = roll_deg
        self.pitch: float = pitch_deg
        self.yaw: float = yaw_deg
        self.qw: float = qw
        self.qx: float = qx
        self.qy: float = qy
        self.qz: float = qz

    def get_roll(self) -> float:
        return self.roll

    def get_pitch(self) -> float:
        return self.pitch

    def get_yaw(self) -> float:
        return self.yaw

    def get_quaternion(self) -> dict[str,float]:
        return {"qw": self.qw, "qx": self.qx, "qy": self.qy, "qz": self.qz}


    def get_attitude(self) -> dict[str,float,dict]:
        return {"roll": self.roll, "pitch": self.pitch, "yaw": self.yaw, "quaternion": self.get_quaternion()}

    def set_roll(self, roll: float):
        self.roll = roll
        return

    def set_pitch(self, pitch: float):
        self.pitch = pitch
        return

    def set_yaw(self, yaw: float):
        self.yaw = yaw
        return

    def set_quaternion(self, qw: float, qx: float, qy: float, qz: float):
        self.qw = qw
        self.qx = qx
        self.qy = qy
        self.qz = qz
