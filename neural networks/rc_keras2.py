import cv2
import numpy as np
import socket
from model import NeuralNetwork
import threading

class RCDriverNNOnly(object):

    def __init__(self, host, port, model_path):

        self.server_socket = socket.socket()
        self.server_socket.bind((host, port))
        self.server_socket.listen(0)

        # accept a single connection
        self.connection = self.server_socket.accept()[0].makefile('rb')
        
        """self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('192.168.0.105', 1234))
        self.connection2 = client_socket.makefile('wb')"""

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('192.168.0.105', 1234))
        #self.connection2 = self.client_socket.makefile('wb')

        #self.prediction = -1
        
        # load trained neural network
        self.nn = NeuralNetwork()
        self.nn.load_modelKeras("model_test.h5")

    def drive(self):
        print("drive called")
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
                    print("Image loaded")
                    
                    #frame= cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
                    
                    cv2.imshow('image', image)
                    cv2.waitKey(1)

                    # reshape image
                    image_array = roi.reshape(1, int(height/2) * width).astype(np.float32)
                    
                    # neural network makes prediction                   

                    self.prediction = self.nn.predictKeras(image_array)
                    print("Keras prediction: ",self.prediction)
                    
                    #convPred = self.prediction.astype(str)
                    #print(type(convPred))
                    #xyz = convPred[0]

                    xyz = self.prediction[0]
                    xyz = str(xyz)
                    print(xyz)

                    t2 = threading.Thread(target=self.sendPrediction, args=(xyz,))
                    
                    #t2 = threading.Thread(target=self.sendPrediction, args=(self.prediction,))
                    t2.start()
                   
                    #print(prediction)
                    #prediction = self.nn.predict(image_array)

                    #pred = self.connection.write(prediction)
                    #self.sendPrediction(self.prediction)
                
                    #Thread(target=self.sendPrediction(prediction)).start()
                    #t2.start()
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("car stopped")
                        self.rc_car.stop()
                        break
        finally:
            cv2.destroyAllWindows()
            self.connection.close()
            self.server_socket.close()

    def sendPrediction(self, pred):
        print('inside sendPrediction')
        """client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('192.168.0.105', 1234))
        
        connection2 = client_socket.makefile('wb')
        
        while True:        
            #print(pred)
            p=connection2.write(bytes(str(pred), 'utf-8'))"""
    
        p=pred+ ' '
        #print(type(p))
        p = p.encode('utf-8')
        self.client_socket.send(p)
        #self.connection2.write(bytes(p), encoding='utf-8')
        print('prediction sent')

        #p=pred + ' '
        #self.connection2.write(bytes(p))
        #print('prediction sent')

        #connection2.close
        #client_socket.close()


if __name__ == '__main__':
    # host, port
    h, p = "192.168.0.100", 1234

    # model path
    path = "model_test.h5"
  
    rc = RCDriverNNOnly(h, p, path)
    
    #Thread(target=rc.drive).start()
    #Thread(target=rc.sendPrediction.start()

    #t1 = threading.Thread(target=rc.drive)
    #t2 = threading.Thread(target=rc.sendPrediction, args=(,))
    #t2.start()
    rc.drive()

    #t1.start()

    #t1.join()
    #t2.join()
    #rc.drive()




#not updating in pi
#prediction in [x] format