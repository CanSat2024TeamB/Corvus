class FlightController:
    def __init__(self, drone_controller):
        self.drone_controller = drone_controller
        
    async def set_altitude(self, altitude: float):
        return