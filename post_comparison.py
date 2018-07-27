from skimage.measure import compare_ssim as ssim
import cv2
import csv
import numpy as np
from os import mkdir
from post_recorder import get_post_data, index_file


# represents a post stored as a text file
class Post:
    def __init__(self, text_file_path):
        with open(text_file_path, 'r', encoding='utf-8') as file:
            data = file.read().split('\n')

            self.id = int(data[0])
            self.title = data[1]
            self.link = data[2]
            self.date = int(data[3])
            self.image_path = data[4]


# represents a new post on the subreddit, contains methods for checking similarity of posts
class NewPost:
    def __init__(self, submission, folder):
        mkdir(folder)
        data = get_post_data(submission, folder)
        if not data:  # if post isn't an image post data will be None
            data = ['']*5

        self.title = data[0]
        self.link = data[1]
        self.image_path = data[3]
        self.features = data[4]
        self.submission = submission

    def compare_image(self, post):
        # create images from the path
        image1 = cv2.imread(self.image_path)
        image2 = cv2.imread(post.image_path)

        # resize image2 to image1's dimensions
        width, height = image1.shape[:2]
        image2_resize = cv2.resize(image2, (height, width), interpolation=cv2.INTER_AREA)

        # split the image into 10ths and compare each section
        sum_similarities = 0
        for i in range(1, 11):
            # crop images with array splicing
            start_section = int(height*(i-1)/10)
            end_section = int(height*i/10)

            im1_section = image1[start_section:end_section, 0:width]
            im2_section = image2_resize[start_section:end_section, 0:width]

            # compare images using structural similarity index
            try:
                similarity = ssim(im1_section, im2_section, multichannel=True)
            except ValueError:  # image is too large (>2500*2500), not worth considering these outliers
                return 0

            # stop comparing if section is not similar
            if similarity < .70:
                return similarity
            sum_similarities += similarity

        # return average similarity of each section
        return sum_similarities/10


# Searches for images with similar features to the stored posts
class ImageSearcher:
    def __init__(self):
        # initialise image index from file
        with open(index_file) as file:
            reader = csv.reader(file)
            # form a list where each item is a tuple in the form (post_id, histogram of image)
            self.index = [(int(line[0]), list(map(float, line[1:]))) for line in reader]
        self.epsilon = 1e-10  # used to prevent division by 0 errors in the distance function

    def search(self, query_features, limit=10):
        results = {}

        for post_id, features in self.index:
            distance = self.distance(features, query_features)
            results[post_id] = distance  # update results with the post number and similarity between the features

        results = sorted(results.items(), key=lambda kv: kv[1])
        return results[:limit]

    # compute the chi-squared distance between two histograms
    def distance(self, histogram1, histogram2):
        return 0.5 * np.sum([((a - b) ** 2) / (a + b + self.epsilon) for (a, b) in zip(histogram1, histogram2)])
