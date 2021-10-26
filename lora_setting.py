# -*- coding: utf-8 -*-
import serial
import time
import RPi.GPIO as GPIO


# LoRa設定用クラス
class LoraSettingClass:

    def __init__(self, serial_device=''):
        try:  # インスタンス変数 serialDevice を生成
            self.device = serial.Serial(serial_device, 115200)
        except Exception as e:
            error_mes = '{0}'.format(e)
            print(error_mes)
        self.cmd = None
        self.reset_pin = 11
        self.set_mode = None

    # LoRaモジュールに対して命令コマンドを入力する
    def cmd_lora(self, cmd=''):
        if not cmd:  # cmdが未入力の場合は終了
            print('cmdが入力されていません')
            return
        self.cmd = '{0}\n'.format(cmd)
        self.device.write(self.cmd.encode())

    # LoRaモジュール初期化
    def reset_lora(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.reset_pin, GPIO.OUT)
        GPIO.output(self.reset_pin, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(self.reset_pin, GPIO.LOW)
        time.sleep(0.5)
        GPIO.cleanup()
        time.sleep(1)

    # LoRaモジュール設定
    def setup_lora(self, set_mode=''):
        # LoRa(RM92C)設定コマンドリスト
        self.set_mode = set_mode
        # LoRa(RM92C)起動待機
        while self.device.inWaiting() > 0:
            try:
                line = self.device.readline()
                if line.find(b'Setting') > -1:
                    print("LoRa Start Up")
            except Exception as e:
                print(e)
                continue
        # LoRa(RM92C)コマンド入力
        for cmd in self.set_mode:
            self.cmd_lora(cmd)
            time.sleep(0.5)
        while self.device.inWaiting() > 0:
            try:
                line = self.device.readline()
                line = line.decode("utf-8")
                print(line)
            except Exception as e:
                print(e)
                continue

    def close(self):
        self.device.close()
