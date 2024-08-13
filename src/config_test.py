from pathlib import Path
from config.config_manager import ConfigManager

config = ConfigManager()

speed = config.read_float("NOSHIRO", "Speed")
print(speed)
print(type(speed))