from pathlib import Path
import datetime

class Logger:
    default_path: str = Path(__file__).parent.parent.joinpath(f"assets/log/log_{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.txt")

    def __init__(self):
        self.path: str = Logger.default_path
        print(self.path)
        self.create_file(self.path)


    def write(self, *msg: str) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.path, 'a', encoding="UTF-8") as f:
            f.write(f"{timestamp} {' '.join(msg)}\n")

    def create_file(self, path: str) -> None:
        self.write("")
        return