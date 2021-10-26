# coding: UTF-8

import sys
import os
import pandas as pd
import csv

import lora_send
import lora_recv


def main(argc, argv):
    lora_device = "/dev/ttyS0" # RM92C デバイス名
    if argc < 2:
        print("Usage: python %s [send | recv]" % (argv[0]))
        print("     [send | recv] ... mode select")
        sys.exit()
    if argv[1] != "send" and argv[1] != "recv":
        print("Usage: python %s [send | recv]" % (argv[0]))
        print("     [send | recv] ... mode select")
        sys.exit()
    
    # チャンネル番号を入力
    channel = input("channel:")

    # testモード
    test_mode = False

    # ファイル名取得
    file_name = os.listdir("./imgs")[0]

    # 一度の送信で読み込むバイト数を指定
    num_bytes = 22

    # 送信側の場合
    if argv[1] == "send":
        # 一度の送信で読み込むバイト数を指定
        # num_bytes = int(input("byte:"))
        
        
        df = pd.read_csv("./test_data/data_frame.csv", index_col=[0, 1])
            
        for sf in [int(input("select sf(1~6):"))]:
            for band in [int(input("select bandwidth(0~2):"))]:
                lr_send = lora_send.LoraSendClass(lora_device,\
                                                  channel,    \
                                                  num_bytes,  \
                                                  test_mode,  \
                                                  sf,         \
                                                  band)

                send_time, resend_count = lr_send.lora_send(file_name)
                df.iat[sf*2,band] = send_time
                df.iat[sf*2+1,band] = int(resend_count)
                print(df)
                
        df.to_csv("./test_data/{}.csv".format(file_name))
        print(df)
        # for i in file_name:
        #     lr_send = lora_send.LoraSendClass(lora_device, channel, num_bytes, test_mode)
        #     lr_send.lora_send(i)
    # 受信側の場合
    elif argv[1] == "recv":
        
        with open("./test_data/{}.csv".format(file_name),"w") as f:
            for sf in [int(input("select sf(1~6):"))]:
                for band in [int(input("select bandwidth(0~2):"))]:
                    file_type = input("input file type(mp4 or jpg etc...)")
                    lr_recv = lora_recv.LoraRecvClass(lora_device,\
                                                      channel,    \
                                                      test_mode,  \
                                                      sf,         \
                                                      num_bytes,  \
                                                      band,       \
                                                      file_type)

                    resend_count = lr_recv.lora_recv()
                    writer = csv.writer(f)
                    writer.writerow([sf,band,resend_count])


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)
    sys.exit()
