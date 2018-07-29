from datetime import datetime
import os
import cv2
import time

import main
import post_recorder
import image_search


def test_post_archive_coverage():
    posts = sorted(main.posts, key=lambda item: item.date)

    posts_in_month = []
    cutoff_date = datetime(2017, 1, 1).timestamp()
    i = 0

    while cutoff_date < datetime.today().timestamp():
        posts_in_month.append(0)

        while i < len(posts) and posts[i].date < cutoff_date:
            posts_in_month[-1] += 1
            i += 1

        print(datetime.fromtimestamp(cutoff_date), ': {}'.format(posts_in_month[-1]))
        cutoff_date += 2592000

    print(posts_in_month)


def check_folder_numbers():
    for i in range(len(os.listdir(post_recorder.base_post_folder))):
        if not os.path.exists(os.path.join(post_recorder.base_post_folder, str(i))):
            print(i)
    print('Done')


# used to test the effectiveness of different numbers of bins
class ImageSearchTester:
    def __init__(self, bins, indexed=False):
        self.image_processor = image_search.ColorDescriptor(bins)
        if not indexed:
            self.re_index()
        self.image_searcher = image_search.ImageSearcher(post_recorder.index_file)

    def re_index(self):
        with open(post_recorder.index_file, 'w') as index:
            for post in main.posts:
                features = self.image_processor.describe(post.image_path)
                features = list(map(str, features))
                index.write('{}, {}\n'.format(post.id, ','.join(features)))

    def search_image(self, image_path):
        query_features = self.image_processor.describe(image_path)
        start = time.time()
        results = self.image_searcher.search(query_features)
        print('Search took {} seconds'.format(time.time() - start))

        image_paths = [main.posts[result[0]].image_path for result in results]
        for path in image_paths:
            image = cv2.imread(path)
            cv2.imshow('Result', image)
            cv2.waitKey(0)
        cv2.destroyAllWindows()

    def test(self):
        folder = input('Image Directory: ')
        for image in os.listdir(folder):
            image_path = os.path.join(folder, image)

            image = cv2.imread(image_path)
            cv2.imshow('Query', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            self.search_image(image_path)
