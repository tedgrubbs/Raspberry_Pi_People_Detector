Little Brother - A Raspberry Pi Security camera

DISCLAIMER: This project is only for fun and should not be used as a real security device. USE AT YOUR OWN RISK.

To use please follow Evan Juras's tutorial on downloading the necessary packages for the Object Detection API and Open CV: https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi/blob/master/README.md

The tensorflow code is the same but it has been adapted using the compat module for use with TensorFlow 2.

Mailer.py looks for a sender and receiver email address in a local file called "config.json". The sender email's password should also be here (see example_config.json for the proper syntax). The sender email should be set to allow less secure apps like so:https://support.google.com/accounts/answer/6010255?hl=en

WARNING: Storing email credentials in a raw text file is highly unsafe and should only be done with extreme caution. For the sender email address I would recommend creating a brand new gmail account that has absolutely no connection to your other personal accounts.

The final step is to retrieve the MobileNet_v2 coco model from tensorflow:

On linux/mac:

wget http://download.tensorflow.org/models/object_detection/ssdlite_mobilenet_v2_coco_2018_05_09.tar.gz
tar -xzvf ssdlite_mobilenet_v2_coco_2018_05_09.tar.gz

On Windows: eh you figure it out

Simply run "python Little_Brother.py" and everything should work... hopefully...
