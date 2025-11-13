import os
import zmq
import atexit
import time

class RecursoBase():
    def __init__(self, id, recurso_alvo):
        self.id = id
        self.recurso_alvo = recurso_alvo
        if os.name == 'nt':  # Windows
            self.zmq_url_in = "tcp://localhost:5555"
            self.zmq_url_out = "tcp://localhost:5556"
        else:
            self.zmq_url_in = "ipc:///tmp/exivium_in.sock"
            self.zmq_url_out = "ipc:///tmp/exivium_out.sock"
        self.context = zmq.Context()
        self.image = None
        self.active = True
        atexit.register(self.close)

    def init_pub_img(self):
        self.pub_img_topic = f"recurso.img.{self.id}".encode()

        self.pub_img_socket = self.context.socket(zmq.PUB)
        self.pub_img_socket.setsockopt(zmq.LINGER, 0)
        self.pub_img_socket.setsockopt(zmq.SNDHWM, 2)
        
        self.pub_img_socket.connect(self.zmq_url_out)

    def init_pub_log(self):
        self.pub_log_topic = f"recurso.log.{self.id}".encode()

        self.pub_log_socket = self.context.socket(zmq.PUB)
        self.pub_log_socket.setsockopt(zmq.LINGER, 1000)
        self.pub_log_socket.setsockopt(zmq.SNDHWM, 100)

        self.pub_log_socket.connect(self.zmq_url_out)
        time.sleep(1) # sincronizar leitura do log

    def init_sub_img(self):
        self.sub_img_topic = f"recurso.img.{self.recurso_alvo}".encode()

        self.sub_img_socket = self.context.socket(zmq.SUB)

        self.sub_img_socket.setsockopt(zmq.SUBSCRIBE, self.sub_img_topic)
        self.sub_img_socket.setsockopt(zmq.LINGER, 0)
        self.sub_img_socket.setsockopt(zmq.RCVHWM, 2)

        self.sub_img_socket.connect(self.zmq_url_in)

    def init_sub_log(self):
        self.sub_log_topic = f"recurso.log.{self.recurso_alvo}".encode()

        self.sub_log_socket = self.context.socket(zmq.SUB)

        self.sub_log_socket.setsockopt(zmq.LINGER, 1000)
        self.sub_log_socket.setsockopt(zmq.RCVHWM, 100)
        self.sub_log_socket.setsockopt(zmq.SUBSCRIBE, self.sub_log_topic)

        self.sub_log_socket.connect(self.zmq_url_in)

    def load_image(self):
        pass

    def get_image(self):
        return self.image

    def send_image(self):
        if self.image:
            self.pub_img_socket.send_multipart([self.pub_img_topic, self.image])

    def send_log(self, text: str):
        if text != "":
            self.pub_log_socket.send_multipart([self.pub_log_topic, text.encode("utf-8") ])

    def close(self):
        self.active = False
