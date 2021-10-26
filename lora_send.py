# coding: UTF-8

import lora_setting
import img_read

import time
import csv
from threading import Timer


# LoRa送信用クラス
class LoraSendClass:

    def __init__(self, lora_device, channel, num_bytes, test_mode, sf, band):
        self.sendDevice = lora_setting.LoraSettingClass(lora_device)
        self.file_reader = img_read.ImgReadClass()

        # 利用チャンネル
        self.channel = channel

        # 読み込むバイト数
        self.num_bytes = num_bytes 

        # テストモード
        self.test_mode = test_mode

        # 再送回数
        self.resend_count = 0

        # 待ち状態保持
        self.waiting_flag = True

        # sf値
        self.sf = str(sf)

        # 帯域幅
        self.band = str(band)


    # RM-92Cデータ送信メソッド
    def lora_send(self, file_name):


        # 再送制御用
        def timer():
            self.resend_count += 1
            self.waiting_flag = False
            print("resend")

        # 送信するファイルを開く
        self.file_reader.bin2b64(file_name)
         
        # LoRa初期化
        self.sendDevice.reset_lora()

        # 送信完了フラグ
        send_comp = False

        # LoRa設定コマンド
        # set_mode = ["\n", "1\n",
        #             "a \n", self.channel+"\n",
        #             # PANアドレス
        #             "b \n", "0\n",
        #             # 自局アドレス
        #             "c \n", "1\n",
        #             # 宛先アドレス
        #             "d \n", "2\n",
        #             # ユニットモード
        #             "e \n", "0\n",
        #             # 帯域幅
        #             "g \n", "1\n", "13\n",
        #             # 帯域幅
        #             "g \n", "2\n", self.band+"\n",
        #             # sf値
        #             "g \n", "3\n", self.sf+"\n",
        #             # 総和時間管理機能を無効化
        #             "p \n", "1\n", "0\n",
        #             # ステータスコード機能を使用しない
        #             "t \n", "0\n",
        #             "s \n"]
        set_mode = ["\n", "1",
                    "a ", self.channel,
                    # PANアドレス
                    "b ", "0",
                    # 自局アドレス
                    "c ", "1",
                    # 宛先アドレス
                    "d ", "2",
                    # ユニットモード
                    "e ", "0",
                    # 帯域幅
                    "g ", "1", "13",
                    # 帯域幅
                    "g ", "2", self.band,
                    # sf値
                    "g ", "3", self.sf,
                    "m ", "1", "0", "5",
                    # 総和時間管理機能を無効化
                    "p ", "1", "0",
                    # ステータスコード機能を使用しない
                    "t ", "0",
                    "s "]
        
        # LoRa設定
        self.sendDevice.setup_lora(set_mode)

        # 送信開始時間取得(unix秒)
        dt_start = time.time()
        dt_end = 0

        # 送信データ
        send_data = self.file_reader.read_byte(self.num_bytes)

        # シーケンス番号
        seq = "0"
        
        #確認応答番号
        ack_num = 1

        # LoRa(RM-92C)データ送信
        while True:
            try:
                # 終端文字送信処理
                if len(send_data) == 0:
                    print("end")
                    send_data = "end"
                    send_comp = True
                    # 終端文字を送信する
                    # self.sendDevice.cmd_lora(send_data)
                    # # 送信終了時間取得
                    # dt_end = time.time()
                    # time.sleep(10)
                    # break

                send_data = send_data
                print("ACK_NUMBER[" + str(ack_num) + "]")
                print("SEND[" + seq + "," + str(ack_num) + "," + send_data + "]")

                # b64データを送信する
                self.sendDevice.cmd_lora(seq + "," + str(ack_num) + "," + send_data)

                # 10秒間のタイマーを作成
                waiting_timer = Timer(10,timer)
                # タイマーをスタート
                waiting_timer.start()

                
                self.waiting_flag = True
                # ACKの受け取り
                while self.waiting_flag:
                    try:
                        if self.sendDevice.device.inWaiting() > 0:
                            line = self.sendDevice.device.readline()
                            
                            # ack確認(確認文字:#)
                            if line.find(b"#") > -1:
                                #print(line)
                                
                                #確認計算
                                ack = str(line).replace('\\n','').replace("\'","").split("#")
                                ack_num = int(ack[1]) + 1
                                

                                #print("checked ack")
                                
                                if not(send_comp):
                                    send_data = self.file_reader.read_byte(self.num_bytes)
                                if seq == "0":
                                    seq = "1"
                                else:
                                    seq = "0"
                                # 待ち状態を解除
                                self.waiting_flag = False
                                # タイマーを中断
                                waiting_timer.cancel()
                                break
                    except Exception as e:
                        print(e)
                        continue
                
                if send_comp:
                    dt_end = time.time()
                    break

            except KeyboardInterrupt:
                self.sendDevice.close()

            # 50ms待機
            time.sleep(0.05)
        # 送信にかかった時間を表示
        self.sf = int(self.sf)
        self.band = int(self.band)
        print(dt_end - dt_start)
        
        # データフレームを更新
        return dt_end - dt_start, self.resend_count


