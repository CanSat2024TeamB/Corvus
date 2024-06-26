class Vector3d:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
    
    #def __init__(self):
     #   self.x = 0.0
      #  self.y = 0.0
       # self.z = 0.0
    
    def x(self) -> float:
        return self.x
    
    def y(self) -> float:
        return self.y
    
    def z(self) -> float:
        return self.z
    
    def get(self) -> dict[str, float]:
        return { "x": self.x, "y": self.y, "z": self.z }
    
    def set_x(self, x: float):
        self.x = x
        return
    
    def set_y(self, y: float):
        self.y = y
        return
    
    def set_z(self, z: float):
        self.z = z
        return
    
    def set(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        return