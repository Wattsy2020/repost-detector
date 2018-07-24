import re
import os
import shutil
import cv2
import urllib
import psaw
import praw

import image_description
import config


def get_praw_api():
    reddit = praw.Reddit(username=config.username,
                         password=config.password,
                         client_id=config.client_id,
                         client_secret=config.client_secret,
                         user_agent=config.user_agent)

    return reddit


def get_psaw_api():
    return psaw.PushshiftAPI()


def store_post(data, folder):
    file_path = os.path.join(folder, "data.txt")

    with open(file_path, 'w', encoding="utf-8") as file:
        for field in data:
            file.write(str(field)+'\n')


def download_image(url, folder):
    file_name = os.path.join(folder, 'image.jpg')
    imgur = False

    # handle different image urls and ignore gifs
    if '.gif' in url:
        return ''
    if 'imgur' in url:
        url = url + '.jpg'
        imgur = True
    elif 'i.redd' not in url:
        return ''

    # download the image, take into account deleted images and other downloading errors
    try:
        urllib.request.urlretrieve(url, file_name)
    except urllib.error.HTTPError:
        return ''
    except Exception as error:
        print('\n Error occurred while downloading image: {}'.format(error))
        return ''

    # Check that images downloaded from imgur are not gifs
    if imgur:
        image = cv2.imread(file_name)
        if image is None:  # gifs will be opened as none
            os.remove(file_name)
            file_name = ''

    return file_name


def get_post_data(post, folder):
    title = post.title
    title = re.sub('[^a-zA-Z0-9\s]+', '', title)  # subreddit.search(title) throws errors with weird characters
    date = int(post.created_utc)
    link = "reddit.com{}".format(post.permalink)

    image_path = download_image(post.url, folder)
    if image_path:  # only record image posts
        features = image_processor.describe(image_path)
        return title, link, date, image_path, features
    return None


def record_posts_from_generator(generator):
    num_existing_posts = len(os.listdir(base_post_folder))

    with open(index_file, 'a') as index:
        for post in generator:
            if post.score < 500: return

            post_folder = os.path.join(base_post_folder, str(num_existing_posts))
            os.mkdir(post_folder)

            data = get_post_data(post, post_folder)
            if data:
                features = list(map(str, data[4]))
                index.write('{}\n'.format(','.join(features)))

                store_post(data[:4], post_folder)
                num_existing_posts += 1
            else:
                shutil.rmtree(post_folder)


def record_old_posts(start_date, end_date, amount):
    post_generator = psaw_api.search_submissions(after=start_date,
                                                 before=end_date,
                                                 subreddit='prequelmemes',
                                                 sort_type="score",
                                                 sort="desc",
                                                 limit=amount)
    record_posts_from_generator(post_generator)


def record_new_posts(time_filter, amount):
    record_posts_from_generator(subreddit.top(time_filter, limit=amount))


psaw_api = get_psaw_api()
subreddit = get_praw_api().subreddit('prequelmemes')
image_processor = image_description.ColorDescriptor((8, 12, 3))

base_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)))
index_file = os.path.join(base_folder, 'index.csv')
base_post_folder = os.path.join(base_folder, 'top_posts')
if not os.path.exists(base_post_folder):
    os.mkdir(base_post_folder)
