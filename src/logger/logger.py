import datetime

class Logger:
    default_path: str = f"../assets/log/log_{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.txt"
    
    def __init__(self, path: str):
        self.path: str = path
        self.create_file(self.path)
    
    def __init__(self):
        self.path: str = Logger.default_path
        self.create_file(self.path)

    def write(self, *msg: str) -> None:
        f = open(self.path, 'a', encoding = "UTF-8")
        f.writelines(map(lambda s: s + "\n", msg))
        f.close()
        return

    def create_file(self, path: str) -> None:
        self.write("")
        return