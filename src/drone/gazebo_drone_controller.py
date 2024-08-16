from drone.drone_controller import DroneController

class GazeboDroneController(DroneController):
    pixhawk_address: str = "udp://:14540"

    default_log_dir = "/Users/adminair/Documents/Sources/VSCode/Corvus/assets/log"

    def __init__(self, log_dir = default_log_dir):
        super().__init__(log_dir)