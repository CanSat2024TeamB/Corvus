class FlightController:
    def __init__(self, drone):
        self.drone = drone
        
    async def set_altitude(self, altitude: float):
        return