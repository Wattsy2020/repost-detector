import numpy as np
import cv2
import math

import config


def resize(image):
    """Returns a resized version of image with dimensions < config.max_image_size"""
    resize_ratio = config.max_image_size[0]/max(image.shape[:2])
    new_width = math.floor(image.shape[0]*resize_ratio)
    new_height = math.floor(image.shape[1]*resize_ratio)

    return cv2.resize(image, (new_height, new_width), interpolation=cv2.INTER_AREA)


class ColorDescriptor:
    def __init__(self):
        self.extractor = cv2.KAZE_create()

    def describe(self, image_path, vector_size=32):
        image = cv2.imread(image_path)
        if image.shape[:2] > config.max_image_size:
            image = resize(image)

        keypoints = self.extractor.detect(image)

        # get most significant keypoints
        keypoints = sorted(keypoints, key=lambda x: -x.response)[:vector_size]

        # create descriptors vector
        _, descriptors = self.extractor.compute(image, keypoints)
        descriptors = descriptors.flatten()

        # make descriptors vector uniform size by adding extra zeros
        uniform_size = 64*vector_size
        if descriptors.size < uniform_size:
            descriptors = np.concatenate([descriptors, np.zeros(uniform_size - descriptors.size)])
        return descriptors


path = "C:\\Users\\liamw\\Desktop\\Memes\\Mathmeme.png"
image = cv2.imread(path)
cv2.imshow("Normal size", image)
cv2.waitKey(0)

image = resize(image)
cv2.imshow("Resized", image)
cv2.waitKey(0)
