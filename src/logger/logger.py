import datetime

class Logger:
    default_path: str = f"../assets/config/log/log_{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.txt"
    
    def __init__(self, path: str):
        self.path: str = path
        self.create_file(self.path)
    
    def __init__(self):
        self.path: str = Logger.default_path
        self.create_file(self.path)


    def write(self, *msg: str) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.path, 'a', encoding="UTF-8") as f:
            f.write(f"{timestamp} {msg[0]}\n")  # 送信時刻と最初のメッセージをスペースで区切って書き込む
            f.writelines(map(lambda s: s + "\n", msg[1:]))


    def create_file(self, path: str) -> None:
        self.write("")
        return