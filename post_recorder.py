import re
import psaw
import os
import urllib
import cv2
import praw

import config
import text_recognition


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


def get_post_data(post, folder, get_text=True):
    title = post.title
    title = re.sub('[^a-zA-Z0-9\s]+', '', title)  # subreddit.search(title) throws errors with weird characters

    date = int(post.created_utc)
    link = "reddit.com{}".format(post.permalink)
    image_path = download_image(post.url, folder)

    title_words = text_recognition.get_words(title)
    title_keywords = text_recognition.remove_common_words(title_words)

    if get_text:
        meme_text = text_recognition.get_image_text(image_path)
        meme_words = text_recognition.get_words(meme_text)
        meme_keywords = text_recognition.parse_ocr_text(meme_words)
    else:
        meme_keywords = ['']

    # 0 is there because system used to record upvotes
    # if creating a new system remove this and modify the __init__ function of NewPost and Post in post_comparison
    return title, title_keywords, link, 0, date, image_path, meme_keywords


def record_posts_from_generator(generator, num_existing_posts):
    for i, post in enumerate(generator):
        if post.score < 500: return

        post_folder = os.path.join(base_post_folder, str(i+num_existing_posts))
        os.mkdir(post_folder)

        data = get_post_data(post, post_folder)
        store_post(data, post_folder)


def record_old_posts(start_date, end_date, amount):
    num_existing_posts = len(os.listdir(base_post_folder))
    post_generator = psaw_api.search_submissions(after=start_date,
                                                 before=end_date,
                                                 subreddit='prequelmemes',
                                                 sort_type="score",
                                                 sort="desc",
                                                 limit=amount)

    record_posts_from_generator(post_generator, num_existing_posts)


def record_new_posts(time_filter, amount):
    num_existing_posts = len(os.listdir(base_post_folder))
    post_generator = subreddit.top(time_filter, limit=amount)

    record_posts_from_generator(post_generator, num_existing_posts)


psaw_api = get_psaw_api()
subreddit = get_praw_api().subreddit('prequelmemes')

base_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)))
base_post_folder = os.path.join(base_folder, 'top_posts')
