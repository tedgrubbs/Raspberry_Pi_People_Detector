# Raspberry Pi security camera
# Object detection code originally written by Evan Juras https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi/blob/master/README.md
# Modified into a security camera app by Taylor Grubbs
# Date: 12-31-2020
# Please follow Evan's tutorial for installation of the object detection API and opencv on the Raspberry PI
# It is incredibly simple

# Import packages
try:
    import os
    import cv2
    import numpy as np
    import tensorflow as tf
    import argparse
    import sys
    from time import sleep
    import timeit

    # Set up camera constants
    IM_WIDTH = 640    #Use smaller resolution for
    IM_HEIGHT = 480   #slightly faster framerate

    # Import utilites
    from object_detection.utils import label_map_util
    from object_detection.utils import visualization_utils as vis_util

    # Name of the directory containing the object detection module we're using
    MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'

    # Grab path to current working directory
    CWD_PATH = os.getcwd()

    # Path to frozen detection graph .pb file, which contains the model that is used
    # for object detection.
    PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

    # Path to label map file
    PATH_TO_LABELS = os.path.join(CWD_PATH,'mscoco_label_map.pbtxt')

    # Number of classes the object detector can identify
    NUM_CLASSES = 90

    ## Load the label map.
    # Label maps map indices to category names, so that when the convolution
    # network predicts `5`, we know that this corresponds to `airplane`.
    # Here we use internal utility functions, but anything that returns a
    # dictionary mapping integers to appropriate string labels would be fine
    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    # Load the Tensorflow model into memory.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.compat.v1.GraphDef()
        with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.graph_util.import_graph_def(od_graph_def, name='')

        sess = tf.compat.v1.Session(graph=detection_graph)


    # Define input and output tensors (i.e. data) for the object detection classifier

    # Input tensor is the image
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # Output tensors are the detection boxes, scores, and classes
    # Each box represents a part of the image where a particular object was detected
    detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

    # Each score represents level of confidence for each of the objects.
    # The score is shown on the result image, together with the class label.
    detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
    detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

    # Number of objects detected
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    threshold = 0.5
    from Mailer import Mailer
    mail_man = Mailer()
    pic_list = []
    person_seen = False

    # Initialize USB webcam feed
    camera = cv2.VideoCapture(0)
    ret = camera.set(3,IM_WIDTH)
    ret = camera.set(4,IM_HEIGHT)
    wait_time = 10. # seconds to wait after a detection is made. Keeps it from taking multiple images of same event.
    timer = timeit.default_timer() - wait_time
    num_pics = 3


    while(True):

        # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
        # i.e. a single-column array, where each item in the column has the pixel RGB value
        ret, frame = camera.read()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_expanded = np.expand_dims(frame_rgb, axis=0)

        # Perform the actual detection by running the model with the image as input
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: frame_expanded})

        # Have to do things this way for a couple reasons
        # cannot just wait x seconds with time.sleep() because camera has a backlog of frames that
        # somehow persist. The person_seen boolean is used because the next 2 frames after a detection may not
        # detect the person even though they are most likely still in frame
        # This ensures you catch at least 3 or more pics of the same event
        print(timeit.default_timer() - timer)

        if scores[0][0] > threshold and classes[0][0] == 1. and (timeit.default_timer() - timer) > wait_time:
            print('Person!', scores[0][0], '\n')
            person_seen = True
        else:
            print('No person here!\n')
            mail_man.check_errors()
            mail_man.send_backlog()

        if person_seen:
            # Draw boxes around people and other things
            vis_util.visualize_boxes_and_labels_on_image_array(
                frame,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                category_index,
                use_normalized_coordinates=True,
                line_thickness=8,
                min_score_thresh=threshold)

            img_name = 'Someone_here_' + str(len(pic_list)) + '.png'
            cv2.imwrite(img_name, frame)
            pic_list.append(img_name)

            if len(pic_list) == num_pics:
                mail_man.send_alert(pic_list)
                person_seen = False
                timer = timeit.default_timer()
                pic_list = []
except Exception as e:
    with open('runtime_errors.txt', 'w') as fp:
        fp.write(str(e)+ '\n')
