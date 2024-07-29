import os
import datetime

class Logger:
    def __init__(self):
        # 動的にログファイルのパスを生成
        self.path = os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir)),
            f"assets/config/log/log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        )
        print(self.path)
        self.create_file(self.path)

    def create_file(self, path: str):
        # ファイルを作成し、初期メッセージを書き込みます。
        with open(path, 'w') as file:
            file.write("Log file created\n")


    def write(self, *msg: str) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.path, 'a', encoding="UTF-8") as f:
            f.write(f"{timestamp} {' '.join(msg)}\n")
