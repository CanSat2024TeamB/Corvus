import serial
import time

def send_and_receive(ser, data, wait_time=2):
    try:
        ser.write(data.encode('ascii'))  # データをASCIIエンコードして送信
        ser.flush()
        time.sleep(wait_time)  # 受信するための待機時間を長く設定
        response = ser.read_until(b'\n\r').decode('utf-8', errors='ignore').strip()  # データをUTF-8デコードして受信
        return response
    except Exception as e:
        print(f"通信エラー: {e}")
        return ""

def main():
    try:
        # シリアルポートの設定
        ser = serial.Serial(port='/dev/ttyS0', baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=5)  # ボーレートとその他の設定を追加
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
        data_to_send = 'p2p tx 123\n\r'  # 送信データは文字列のまま
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


