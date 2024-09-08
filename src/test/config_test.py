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

lora_sync = config.read_int(section, "LoraSync")
lora_freq = config.read_int(section, "LoraFreq")
lora_sf = config.read_int(section, "LoraSf")
lora_bw = config.read_int(section, "LoraBw")
lora_pwr = config.read_int(section, "LoraPwr")

print(speed, type(speed))
print(hov_alt, type(hov_alt))
print(target_lon, type(target_lon))
print(target_lat, type(target_lat))
print(goal_radius, type(goal_radius))

print(lora_sync, type(lora_sync))
print(lora_freq, type(lora_freq))
print(lora_sf, type(lora_sf))
print(lora_bw, type(lora_bw))
print(lora_pwr, type(lora_pwr))
