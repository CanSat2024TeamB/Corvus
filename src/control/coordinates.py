from control.vector3d import Vector3d

class Coordinates(Vector3d):
    def __init__(self, longitude: float, latitude: float, altitude: float):
        super().__init__(longitude, latitude, altitude)
    
    def __init__(self, longitude: float, latitude: float):
        super().__init__(longitude, latitude, None)
    
    def __init__(self):
        super().__init__()

    def longitude(self) -> float:
        return self.x()
    
    def latitude(self) -> float:
        return self.y()
    
    def altitude(self) -> float:
        return self.z()
    
    def set_longitude(self, longitude: float) -> None:
        self.set_x(longitude)
        return
    
    def set_latitude(self, latitude: float) -> None:
        self.set_y(latitude)
        return
    
    def set_altitude(self, altitude: float) -> None:
        self.set_z(altitude)
        return