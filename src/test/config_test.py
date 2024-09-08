import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from config.config_manager import ConfigManager

config = ConfigManager()
section = "ARLISS"
speed = config.read_float(section, "Speed")
hov_alt = config.read_float(section, "HovAlt")
target_lon = config.read_float(section, "TargetLon")
target_lat = config.read_float(section, "TargetLat")
goal_radius = config.read_float(section, "GoalRadius")

print(speed, type(speed))
print(hov_alt, type(hov_alt))
print(target_lon, type(target_lon))
print(target_lat, type(target_lat))
print(goal_radius, type(goal_radius))