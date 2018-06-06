from skimage.measure import compare_ssim as ssim
import cv2
from os import mkdir
import post_recorder


def compare_keywords(words1, words2):
    if len(words1) == 0: return 0  # only happens if title_keywords is blank

    matches = 0
    for word in words1:
        if word in words2:
            matches += 1

    return matches/len(words1)


# represents a post stored in memory
class Post:
    def __init__(self, text_file_path):
        with open(text_file_path, 'r', encoding='utf-8') as file:
            data = file.readlines()

            for i in range(len(data)):
                data[i] = data[i].rstrip()

            self.title = data[0]
            self.title_keywords = data[1][2:-3].split("', '")
            self.link = data[2]
            self.date = int(data[4])
            self.image_path = data[5]
            self.meme_words = [''] if len(data[6]) == 4 else data[6][2:-3].split("', '")


# represents a new post on the subreddit, contains methods for checking similarity of posts
class NewPost:
    def __init__(self, submission, folder, get_text=True):
        mkdir(folder)
        data = post_recorder.get_post_data(submission, folder, get_text)

        self.title = data[0]
        self.title_keywords = data[1]
        self.link = data[2]
        self.image_path = data[5]
        self.meme_words = data[6]
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
