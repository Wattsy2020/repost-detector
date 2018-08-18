from skimage.measure import compare_ssim as ssim
import cv2
from os import mkdir

from post_recorder import get_post_data
from image_search import resize
import config


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
        self.image_path = data[3]
        if self.image_path:
            self.image = cv2.imread(self.image_path)
        self.features = data[4]
        self.submission = submission

    def compare_image(self, post):
        # create images from the path
        image1 = self.image
        image2 = cv2.imread(post.image_path)

        # resize image2 to image1's dimensions
        if image1.shape[:2] > config.max_image_size:  # resize image if too large
            image1 = resize(image1)
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
