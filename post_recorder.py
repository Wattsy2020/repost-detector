import re
import psaw
import os
import urllib
import cv2

import text_recognition


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

    score = post.score
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

    return title, title_keywords, link, score, date, image_path, meme_keywords


def record_top_posts(start_date, end_date, amount):
    base_post_folder = os.path.join(base_folder, 'top_posts')

    if os.path.exists(base_post_folder):
        num_existing_posts = len(os.listdir(base_post_folder))
    else:
        os.mkdir(base_post_folder)
        num_existing_posts = 0

    post_generator = psaw_api.search_submissions(after=start_date,
                                                 before=end_date,
                                                 subreddit='prequelmemes',
                                                 sort_type="score",
                                                 sort="desc",
                                                 limit=amount)

    for i, post in enumerate(post_generator):
        post_folder = os.path.join(base_post_folder, str(i+num_existing_posts))
        os.mkdir(post_folder)

        data = get_post_data(post, post_folder)
        store_post(data, post_folder)

        print("{}% complete".format(int((i+1)/amount*100)))


psaw_api = get_psaw_api()
base_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)))
