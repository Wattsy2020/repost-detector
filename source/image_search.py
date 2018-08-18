import cv2
import numpy as np
import math
import scipy
import pickle
import os

import config


def resize(image):
    """Returns a resized version of image with dimensions < config.max_image_size"""
    resize_ratio = config.max_image_size[0]/max(image.shape[:2])
    new_width = math.floor(image.shape[0]*resize_ratio)
    new_height = math.floor(image.shape[1]*resize_ratio)

    return cv2.resize(image, (new_height, new_width), interpolation=cv2.INTER_AREA)


class ImageDescriptor:
    def __init__(self):
        self.extractor = cv2.KAZE_create()

    def describe(self, image_path, vector_size=32):
        """extract features from an image using KAZE"""
        image = cv2.imread(image_path)
        if image.shape[:2] > config.max_image_size:
            image = resize(image)

        keypoints = self.extractor.detect(image)
        if not keypoints: return  # sometimes there are no keypoints

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


class ImageSearcher:
    def __init__(self, index_file):
        with open(index_file) as file:
            data = pickle.load(file)

        self.ids, self.matrix = zip(*data)
        self.ids = np.array(self.ids)
        self.matrix = np.array(self.matrix)

    def cos_cdist(self, vector):
        """get cosine distance between search image and stored images"""
        v = vector.reshape(1, -1)
        return scipy.spatial.distance.cdist(self.matrix, v, 'cosine').reshape(-1)

    def search(self, query_features, limit=30):
        """returns the post ids of posts with similar features to query features"""
        image_distances = self.cos_cdist(query_features)

        # return the post_ids of the top results
        nearest_images_indices = np.argsort(image_distances)[:limit].toList()
        return self.ids[nearest_images_indices].toList()


path1 = "C:\\Users\\liamw\\Desktop\\Memes\\Mathmeme.png"
path2 = os.path.join(os.path.dirname(os.path.dirname(__file__)), "top_posts\\3052\\image.jpg")
dsc = ImageDescriptor()
dsc.describe(path2)
