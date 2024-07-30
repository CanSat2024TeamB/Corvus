import serial
import time

def send_command(ser, command, wait_time=1):
    try:
        ser.write((command + '\r').encode('ascii'))  # コマンドの末尾にCRを追加
        ser.flush()
        time.sleep(wait_time)
        response = ser.read_all().decode('ascii')
        return response
    except Exception as e:
        print(f"コマンド送信エラー: {e}")
        return ""

def main():
    try:
        ser = serial.Serial(port='/dev/ttyS0', baudrate=115200, timeout=1)
        if ser.is_open:
            print(f"シリアルポート {ser.port} を開きました")
        else:
            print("シリアルポートを開けませんでした")
            return
    except Exception as e:
        print(f"シリアルポートのオープンエラー: {e}")
        return
    
    # コマンドを送信し、応答を表示
    command = 'mod get_ver'  # 実際のコマンドに置き換えてください
    print(f"送信したコマンド: > {command}")
    response = send_command(ser, f"> {command}")
    print(f"受信した応答: {response}")


    # 通信確立
    ser = serial.Serial('/dev/ttyS0', '9600', timeout=0.1)
    print('new rate')
    # データ送受信
    ser.write('Hello, World!')
    print(repr(ser.readline()))
    ser.close()


    # 終了前にシリアルポートを閉じる
    try:
        ser.close()
        print("シリアルポートを閉じました")
    except Exception as e:
        print(f"シリアルポートのクローズエラー: {e}")

if __name__ == "__main__":
    main()


