# coding: UTF-8

import base64

class ImgReadClass:

    def __init__(self):
        self.path = "./imgs/"
        self.reader = None

    def bin2b64(self, file_name):
        # 任意のファイルを開く
        # バイナリをbase64に変換
        print(self.path + file_name)
        with open(self.path + file_name, "br") as f:
            base64_data = base64.b64encode(f.read())
        
        with open("./b64.txt","w") as f:
            f.write(base64_data.decode())

        self.reader = open("./b64.txt", "r")

    def read_byte(self, num_bytes):
        send_data = self.reader.read(num_bytes)
        if len(send_data) == 0:
            self.reader.close()
        return send_data

        
