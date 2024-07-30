import serial
import time

def send_and_receive(ser, data, wait_time=1):
    try:
        ser.write(data)
        ser.flush()
        time.sleep(wait_time)
        response = ser.read_all()
        return response
    except Exception as e:
        print(f"通信エラー: {e}")
        return b""

def main():
    try:
        # シリアルポートの設定
        ser = serial.Serial(port='/dev/ttyS0', baudrate=115200, timeout=1)
        if ser.is_open:
            print(f"シリアルポート {ser.port} を開きました")
        else:
            print("シリアルポートを開けませんでした")
            return
    except Exception as e:
        print(f"シリアルポートのオープンエラー: {e}")
        return

    # データの送受信
    data_to_send = b'Hello, World!'
    print(f"送信したデータ: {data_to_send}")
    response = send_and_receive(ser, data_to_send)
    print(f"受信したデータ: {response}")

    # シリアルポートを閉じる
    try:
        ser.close()
        print("シリアルポートを閉じました")
    except Exception as e:
        print(f"シリアルポートのクローズエラー: {e}")

if __name__ == "__main__":
    main()




