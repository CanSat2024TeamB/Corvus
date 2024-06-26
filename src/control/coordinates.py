from control.vector3d import Vector3d

class Coordinates(Vector3d):
    def __init__(self, longitude: float = None, latitude: float = None, altitude: float = None):
        if longitude is not None and latitude is not None and altitude is not None:
            super().__init__(longitude, latitude, altitude)
        elif longitude is not None and latitude is not None:
            super().__init__(longitude, latitude, 0.0)  # デフォルトで高度を0.0に設定
        else:
            super().__init__(0.0, 0.0, 0.0)  # デフォルトで全ての値を0.0に設定

    def longitude(self) -> float:
        return self.get_x()
    
    def latitude(self) -> float:
        return self.get_y()
    
    def altitude(self) -> float:
        return self.get_z()
    
    def set_longitude(self, longitude: float) -> None:
        self.set_x(longitude)
    
    def set_latitude(self, latitude: float) -> None:
        self.set_y(latitude)
    
    def set_altitude(self, altitude: float) -> None:
        self.set_z(altitude)

# 使用例
coord1 = Coordinates(139.760557, 35.714995, 0)
print(coord1.get())  # {'x': 139.760557, 'y': 35.714995, 'z': 0.0}

coord2 = Coordinates(139.760557, 35.714995)
print(coord2.get())  # {'x': 139.760557, 'y': 35.714995, 'z': 0.0}

coord3 = Coordinates()
print(coord3.get())  # {'x': 0.0, 'y': 0.0, 'z': 0.0}
