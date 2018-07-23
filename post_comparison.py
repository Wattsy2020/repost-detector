from skimage.measure import compare_ssim as ssim
import cv2
from os import mkdir
from post_recorder import get_post_data


# represents a post stored as a text file
class Post:
    def __init__(self, text_file_path):
        with open(text_file_path, 'r', encoding='utf-8') as file:
            data = file.read().split('\n')

            self.title = data[0]
            self.link = data[1]
            self.date = int(data[2])
            self.image_path = data[3]


# represents a new post on the subreddit, contains methods for checking similarity of posts
class NewPost:
    def __init__(self, submission, folder):
        mkdir(folder)
        data = get_post_data(submission, folder)

        self.title = data[0]
        self.link = data[1]
        self.image_path = data[3]
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
