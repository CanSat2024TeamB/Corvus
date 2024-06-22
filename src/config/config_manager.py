import configparser
import os

class ConfigManager:
    def __init__(self, path: str):
        self.config_ini = configparser.ConfigParser()
        self.load(path)
        return

    def load(self, path: str) -> None:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"{path} does not exist!")
        self.config_ini.read(path, encoding = "utf-8")
        return

    def read(self, section: str, item: str) -> str:
        return self.config_ini.get(section, item)
    
    def read_default(self, item: str) -> str:
        return self.config_ini.get("DEFAULT", item)
    
    def get_sections(self) -> list[str]:
        return self.config_ini.sections()

    def get_items(self, section: str) -> dict[str, str]:
        items = self.config_ini.items(section)
        return dict(items)