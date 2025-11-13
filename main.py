from recurso_base import RecursoBase
import cv2
import sys
import numpy as np
import zmq
import time
import os

FPS = int( os.environ.get("FPS") )
JPEG_QUALITY = int( os.environ.get("JPEG_QUALITY") )

class PrimeiroPlugin(RecursoBase):
    def __init__(self, id, recurso_alvo):
        super().__init__(id, recurso_alvo)
        self.init_sub_img()
        self.init_pub_img()
        self.init_pub_log()

    def load_image(self):
        loaded = False
        while self.active:
            try:
                topic, image = self.sub_img_socket.recv_multipart(flags=zmq.NOBLOCK)
                if topic == self.sub_img_topic and image:
                    self.image = image
                    loaded = True
            except zmq.Again:
                break

        return loaded

    def processa(self):
        try:
            frame_array = np.frombuffer(self.image, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            loaded, buffer = cv2.imencode(".jpg", gray_image, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            if loaded:
                self.image = buffer.tobytes()
                
                self.send_image()
        except Exception as e:
            print(e)
            raise e

    def close(self):
        self.send_log(f"Parando plugin {self.id}")
        self.active = False
        self.sub_img_socket.close()
        self.pub_img_socket.close()
        self.pub_log_socket.close()

def main(id, target):
    reader = PrimeiroPlugin(id, target)
    reader.send_log(f'Rodando primeiro plugin na camera {target}')
    while reader.active:
        try:
            if reader.load_image():
                reader.processa()
        except Exception:
            reader.close()
            break
        time.sleep(1/FPS)

if __name__ == "__main__":
    id = sys.argv[1]
    target = sys.argv[2]
    main(id, target)