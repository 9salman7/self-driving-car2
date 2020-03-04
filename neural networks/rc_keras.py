
import cv2
import numpy as np
import socket
from model import NeuralNetwork
from threading import Thread
#from rc_driver_helper import RCControl

class RCDriverNNOnly(object):

    def __init__(self, host, port, model_path):

        self.server_socket = socket.socket()
        self.server_socket.bind((host, port))
        self.server_socket.listen(0)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('192.168.0.105', 1234))
        self.connection2 = client_socket.makefile('wb')

        # accept a single connection
        self.connection = self.server_socket.accept()[0].makefile('rb')
        #self.connection2= self.server_socket.makefile('wb')

        # load trained neural network
        self.nn = NeuralNetwork()
        #self.nn.model = load_modelKeras('model_test.h5')
        self.nn.load_modelKeras("model_test.h5")
        #self.nn.load_model("tf_model.pb")
        #self.rc_car = RCControl()

    def drive(self):
        stream_bytes = b' '
        try:
            # stream video frames one by one
            while True:
                stream_bytes += self.connection.read(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')

                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    gray = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                    # lower half of the image
                    height, width = gray.shape
                    roi = gray[int(height/2):height, :]

                    cv2.imshow('image', image)
                    # cv2.imshow('mlp_image', roi)

                    # reshape image
                    image_array = roi.reshape(1, int(height/2) * width).astype(np.float32)
                    
                    # neural network makes prediction
                    prediction = self.nn.predictKeras(image_array)
                    #prediction = self.nn.predict(image_array)

                    #pred = self.connection.write(prediction)
                    self.sendPrediction(prediction)
                    #elf.rc_car.steer(prediction)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("car stopped")
                        self.rc_car.stop()
                        break
        finally:
            cv2.destroyAllWindows()
            self.connection.close()
            self.server_socket.close()

    def sendPrediction(pred):
        while True:
            pred = self.connection2.write(bytes(str(prediction), 'utf8'))



if __name__ == '__main__':
    # host, port
    h, p = "192.168.0.112", 1234

    # serial port
    #sp = "/dev/tty.usbmodem1421"

    # model path
    path = "model_test.h5"
  

    rc = RCDriverNNOnly(h, p, path)
    Thread(target=rc.sendPrediction()).start()
    rc.drive()
