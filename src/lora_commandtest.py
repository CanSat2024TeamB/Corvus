import serial
import time

def send_command(ser, command, wait_time=1):
    ser.write(command.encode('utf-8'))
    ser.flush()
    time.sleep(wait_time)
    response = ser.read_all().decode('utf-8')
    return response

def main():
    ser = serial.Serial(port='/dev/ttyS0', baudrate=9600, timeout=1)
    if ser.is_open:
        print(f"シリアルポート {ser.port} を開きました")
    else:
        print("シリアルポートを開けませんでした")
        return
    
    # コマンドを送信し、応答を表示
    command = 'YOUR_LORA_COMMAND_HERE'
    response = send_command(ser, command)
    print(f"送信したコマンド: {command}")
    print(f"受信した応答: {response}")

    # 終了前にシリアルポートを閉じる
    ser.close()
    print("シリアルポートを閉じました")

if __name__ == "__main__":
    main()
