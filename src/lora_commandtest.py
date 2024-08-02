import serial
import time

def send_and_receive(ser, data, wait_time=2):
    try:
        ser.write(data)
        ser.flush()
        time.sleep(wait_time)  # 受信するための待機時間を長く設定
        response = ser.readline().decode('utf-8').strip()
        return response
    except Exception as e:
        print(f"通信エラー: {e}")
        return ""

def main():
    try:
        # シリアルポートの設定
        ser = serial.Serial(port='/dev/ttyAMA0', baudrate=9600, timeout=5)  # タイムアウトを長めに設定
        if ser.is_open:
            print(f"シリアルポート {ser.port} を開きました")
        else:
            print("シリアルポートを開けませんでした")
            return
    except Exception as e:
        print(f"シリアルポートのオープンエラー: {e}")
        return

    # データの送受信
    for i in range(10):
        data_to_send = b'Hello, World!\r\n'
        print(f"送信したデータ: {data_to_send}")
        response = send_and_receive(ser, data_to_send)
        print(f"受信したデータ: {response}")
        time.sleep(2)

    # シリアルポートを閉じる
    try:
        ser.close()
        print("シリアルポートを閉じました")
    except Exception as e:
        print(f"シリアルポートのクローズエラー: {e}")

if __name__ == "__main__":
    main()






