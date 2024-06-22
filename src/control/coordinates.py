class Coordinates:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
    
    def x() -> float:
        return self.x
    
    def y() -> float:
        return self.y
    
    def z() -> float:
        return self.z
    
    def get() -> dict[str, float]:
        return { "x": self.x, "y": self.y, "z": self.z }
    
    def set_x(x: float):
        self.x = x
        return
    
    def set_y(y: float):
        self.y = y
        return
    
    def set_z(z: float):
        self.z = z
        return
    
    def set(x, y, z):
        self.x = x
        self.y = y
        self.z = z
        return