# coding: UTF-8

import lora_setting
import datetime
import time
import base64
import threading

# LoRa送信用クラス
class LoraRecvClass:
    def __init__(self, lora_device, channel, test_mode, sf, num_bytes, band, file_type):
        self.recvDevice = lora_setting.LoraSettingClass(lora_device)

        # 利用チャンネル
        self.channel = channel

        # 待ち状態保持
        self.waiting_flag = True

        # テストモード
        self.test_mode = test_mode

        # 読み込むバイト数
        self.num_bytes = num_bytes 

        # sf値
        self.sf = str(sf)

        # 帯域幅
        self.band = str(band)

        # 拡張子
        self.file_type = file_type

    # RM-92Cデータ受信メソッド
    def lora_recv(self):
        # b64データ受け取り用
        b64_data = ""
        # 受信データ格納用
        recv_data = ""
        # 書き込みデータ格納用
        write_data = ""
        # シーケンス番号格納用
        seq = None
        # LoRa初期化
        self.recvDevice.reset_lora()

        # LoRa設定コマンド
        set_mode = [
            "\n",
            "1",
            "a ",
            self.channel,
            # PANアドレス
            "b ",
            "0",
            # 自局アドレス
            "c ",
            "2",
            # 宛先アドレス
            "d ",
            "1",
            # ユニットモード
            "e ",
            "0",
            # 帯域幅
            "g ",
            "1",
            "13",
            # 帯域幅
            "g ",
            "2",
            self.band,
            # sf値
            "g ",
            "3",
            self.sf,
            # CR/LF非出力設定
            "l ",
            "3",
            "0",
            "m ",
            "1",
            "0",
            "5",
            # 総和時間管理機能を無効化
            "p ",
            "1",
            "0",
            # ステータスコード機能を使用しない
            "t ",
            "0",
            "s ",
        ]

        # LoRa設定
        self.recvDevice.setup_lora(set_mode)

        # LoRa(RM-92C)受信待機
        while True:
            try:
                if self.recvDevice.device.inWaiting() > 0:
                    try:
                        line = self.recvDevice.device.readline()
                        line = line.decode("utf-8")
                    except Exception as e:
                        print(e)
                        continue

                    print(line)
                    
                    #リスト宣言
                    recv_data = []
                    recv_data = line.split(",")

                    # 書き込みデータ格納
                    write_data = recv_data[3]

                    #確認応答番号計算
                    recv_data[2] = str(int(recv_data[2]) + self.num_bytes)

                    # データを出力
                    print("RECV["+ str(line) +"]")

                    if len(recv_data) == 0:
                        print("no data")
                        continue
                    # ack送信
                    self.recvDevice.cmd_lora("#"+recv_data[2])
                    print("ACK_NUMBER =" +str(recv_data[2]))

                    # データ終端文字確認
                    if write_data == "end":
                        print("complete")
                        break

                    if seq != recv_data[1]:
                        b64_data += write_data
                        seq = recv_data[1]
                    else:
                        print("discard")

            except KeyboardInterrupt:
                self.recvDevice.close()

        # b64データをデコード
        with open("./imgs/b64.txt", "w") as f:
            f.write(b64_data)

        # base64 → binary
        bin_data = base64.b64decode(b64_data.encode())

        # ファイルに書き込み
        with open(
            "./imgs/recv_sf_{}_bandwidth_{}.{}".format(
                self.sf, self.band, self.file_type
            ),
            "bw",
        ) as mp4:
            mp4.write(bin_data)

