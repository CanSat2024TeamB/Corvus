from pathlib import Path
import datetime
import os

class Logger:
    default_dir = "~/corvus/assets/log"
    def __init__(self, dir: str = default_dir):
        # 動的にログファイルのパスを生成
        self.dir = dir
        self.path = str(Path(self.dir).joinpath(f"log_{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.txt"))
        print(f"Logs will be written to the file, {self.path}")
        self.create_file(self.path)

    def create_file(self, path: str):
        # ディレクトリが存在しない場合は作成する
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # ファイルを作成し、初期メッセージを書き込みます。
        with open(path, 'w') as file:
            file.write("Log file created\n")

    def write(self, *msg: str) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.path, 'a', encoding="UTF-8") as f:
            f.write(f"{timestamp} {' '.join(msg)}\n")

