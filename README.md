---


---

<h2 id="infernus">Infernus</h2>
<h3 id="self-driving-car-built-using-opencv-tensorflow-and-arduino">Self Driving Car built using OpenCV, Tensorflow and Arduino</h3>
<h3 id="about-the-files">About the files</h3>
<p><strong>arduino/</strong><br>
     <code>carController.ino</code>: Arduino code for controlling the car</p>
<p><strong>test files/</strong><br>
     <code>rc_control_test.py</code>: RC car control with keyboard<br>
     <code>stream_server_test.py</code>: video streaming from Pi to computer<br>
     <code>ultrasonic_server_test.py</code>: sensor data streaming from Pi to computer<br>
   <br>
<strong>client data streaming files/</strong><br>
     <code>stream_client.py</code>: stream video frames in jpeg format to the host computer<br>
     <code>ultrasonic_client.py</code>: send distance data measured by sensor to the host computer</p>
<p><strong>neural networks/</strong><br>
     <strong>old codes/</strong><br>
        codes for testing<br>
     <strong>saved_models/</strong><br>
        OpenCV neural network models<br>
    <strong>training data/</strong><br>
        training data saved in .npz format<br>
   <br>
     <code>collect_training_data.py</code>: collect images in grayscale, data saved as  <code>*.npz</code><br>
     <code>model.py</code>: neural network model<br>
     <code>model_test.h5</code>: keras neural network model<br>
     <code>rc_driver_keras2.py</code>: code to be run on Pi<br>
     <code>rc_keras5.py</code>: receive data from Raspberry Pi and drive the car based on model prediction<br>
     <code>rc_driver_nn_only.py</code>: simplified  <code>rc_driver.py</code>  without object detection</p>
<p><code>kerasInfernus.ipynb</code>: Jupyter notebook for training Tensorflow model</p>

