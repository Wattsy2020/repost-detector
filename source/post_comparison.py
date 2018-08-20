from skimage.measure import compare_ssim as ssim
import cv2
import math
from os import mkdir

from post_recorder import get_post_data
import config


def resize(image):
    """Returns a resized version of image with dimensions < config.max_image_size"""
    resize_ratio = config.max_image_size[0]/max(image.shape[:2])
    new_width = math.floor(image.shape[0]*resize_ratio)
    new_height = math.floor(image.shape[1]*resize_ratio)

    return cv2.resize(image, (new_height, new_width), interpolation=cv2.INTER_AREA)


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
            data = [None]*5

        self.title = data[0]
        self.link = data[1]
        self.features = data[4]
        self.submission = submission

        self.image_path = data[3]
        if self.image_path:
            self.image = cv2.imread(self.image_path)
            if self.image.shape[0] > config.max_image_size[0] or self.image.shape[1] > config.max_image_size[1]:
                self.image = resize(self.image)

    def compare_image(self, post):
        # create images from the path
        image1 = self.image
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
            similarity = ssim(im1_section, im2_section, multichannel=True)

            # stop comparing if section is not similar
            if similarity < .7:
                return similarity
            sum_similarities += similarity

        # return average similarity of each section
        return sum_similarities/10
