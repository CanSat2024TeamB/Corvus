from control import Vector3d

class Coordinates(Vector3d):
    def __init__(self, longitude: float, latitude: float, height: float):
        super(longitude, latitude, height)
    
    def __init__(self, longitude: float, latitude: float):
        super(longitude, latitude, None)
    
    def __init__(self):
        super()

    def longitude(self) -> float:
        return self.x()
    
    def latitude(self) -> float:
        return self.y()
    
    def set_longitude(self, x: float) -> None:
        self.set_x(x)
        return
    
    def set_latitude(self, y: float) -> None:
        self.set_y(y)
        return