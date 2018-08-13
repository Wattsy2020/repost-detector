import numpy as np
import cv2
import csv


class ColorDescriptor:
    def __init__(self, bins):
        self.bins = bins

    # extracts a color histogram from a section of an image
    def histogram(self, image, mask):
        hist = cv2.calcHist([image], [0, 1, 2], mask, self.bins, [0, 180, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist).flatten()

        return hist

    # extracts a color histogram from the image, analysing sections of the image separately for greater accuracy
    def describe(self, image_path):
        image = cv2.imread(image_path)

        # convert the image to the HSV color space and initialize the features used to quantify the image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        features = []

        # grab the dimensions and compute the center of the image
        h, w = image.shape[:2]
        cx, cy = int(w * 0.5), int(h * 0.5)

        # divide the image into four rectangular segments
        segments = [(0, cx, 0, cy), (cx, w, 0, cy), (cx, w, cy, h), (0, cx, cy, h)]

        # construct an elliptical mask representing the center of the image
        x_radius, y_radius = int(w * 0.75) // 2, int(h * 0.75) // 2
        ellipse_mask = np.zeros(image.shape[:2], dtype="uint8")
        cv2.ellipse(ellipse_mask, (cx, cy), (x_radius, y_radius), 0, 0, 360, 255, -1)

        # loop over the segments and create a color histogram for each
        for (startX, endX, startY, endY) in segments:
            # construct a mask for each corner of the image, subtracting the elliptical center from it
            corner_mask = np.zeros(image.shape[:2], dtype="uint8")
            cv2.rectangle(corner_mask, (startX, startY), (endX, endY), 255, -1)
            corner_mask = cv2.subtract(corner_mask, ellipse_mask)

            # extract a color histogram from the image and update the feature vector
            hist = self.histogram(image, corner_mask)
            features.extend(hist)

        # extract a color histogram from the elliptical region and update the feature vector
        hist = self.histogram(image, ellipse_mask)
        features.extend(hist)

        # convert features to form needed for cv2.compareHist()
        features = np.array(features)
        return features.ravel().astype('float32')


# Searches for images with similar features to the stored posts
class ImageSearcher:
    def __init__(self, index_file):
        with open(index_file) as file:
            reader = csv.reader(file)
            # form a list where each item is a tuple in the form (post_id, histogram of image)
            self.index = [(int(line[0]), np.array(list(map(float, line[1:]))).ravel().astype('float32'))
                          for line in reader]

    def search(self, query_features, limit=20):
        results = []

        for post_id, features in self.index:
            distance = cv2.compareHist(features, query_features, cv2.HISTCMP_CORREL)
            results.append([post_id, distance])

        results = sorted(results, key=lambda result: result[1], reverse=True)
        return results[:limit]
