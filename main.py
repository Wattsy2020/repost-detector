import os
import shutil
import time

import prawcore
from datetime import datetime
from post_recorder import subreddit

import post_recorder
from post_comparison import Post, NewPost, compare_keywords


def record_posts():
    post_recorder.record_top_posts('all', 1000)
    post_recorder.record_top_posts('month', 1000)


def load_posts_from_folder(folder):
    posts_folder = os.path.join(post_recorder.base_folder, folder)
    posts = []

    for folder in os.listdir(posts_folder):
        post_path = os.path.join(posts_folder, '{}\\data.txt'.format(folder.title()))

        if os.path.exists(post_path):  # if its a deleted post it will have a folder but no text file
            posts.append(Post(post_path))

    return posts


def load_all_posts():
    # return all stored posts sorted by date
    top_posts = load_posts_from_folder('all')
    month_posts = load_posts_from_folder('month')

    top_posts.extend(month_posts)
    top_posts = sorted(top_posts, key=lambda item: -item.date)  # need negative sign to sort by most recent date

    return top_posts


def update_posts():
    # record top posts of the day
    post_recorder.record_top_posts('day', 35)

    # move them to the month folder
    month_folder = os.path.join(post_recorder.base_folder, 'month')
    day_folder = os.path.join(post_recorder.base_folder, 'day')

    num_posts = len(os.listdir(month_folder))
    for i in range(35):
        source = os.path.join(day_folder, str(i))
        destination = os.path.join(month_folder, str(i + num_posts))

        shutil.move(source, destination)

    shutil.rmtree(day_folder)

    # reload posts
    return load_all_posts()


def reply(repost: NewPost, original):
    print('\n{} is a repost of {}'.format(repost.link, original.link))


def check_if_repost(new_post, posts):
    # print('\nChecking: {}       Meme text: {}'.format(new_post.title, new_post.meme_words))
    title_similarity_limit = .7
    meme_text_similarity_limit = .7
    image_similarity_limit = .9

    # compare posts with the same title
    temp_folder = os.path.join(post_recorder.base_folder, 'temp')
    for submission in subreddit.search("title:{}".format(new_post.title), sort='top'):
        # ignore the exact same post
        if new_post.link == ('reddit.com'+submission.permalink): continue
        if submission.score <= 25: break

        search_post = NewPost(submission, temp_folder, get_text=False)

        # handle gifs
        if new_post.image_path == '' or search_post.image_path == '':
            if new_post.image_path == search_post.image_path and new_post.title == search_post.title:
                reply(new_post, search_post)
                shutil.rmtree(temp_folder)
                return
            else:
                shutil.rmtree(temp_folder)
                continue

        similarity = new_post.compare_image(search_post)
        shutil.rmtree(temp_folder)

        if similarity >= image_similarity_limit:
            reply(new_post, search_post)
            return

    # search for posts with similar meme_words and use image comparison on the matches
    for post in posts:
        # compare gifs
        if new_post.image_path == '' or post.image_path == '':
            if new_post.image_path == post.image_path:  # if they are both gifs go by the similarity of the title
                if compare_keywords(new_post.title_keywords, post.title_keywords) >= title_similarity_limit:
                    reply(new_post, post)
                    return

        # compare blank images
        elif new_post.meme_words == ['a'] or new_post.meme_words == []:  # blank text is autocorrected to 'a'
            if compare_keywords(new_post.title_keywords, post.title_keywords) >= title_similarity_limit:
                if new_post.compare_image(post) >= image_similarity_limit:
                    reply(new_post, post)
                    return

        # compare normal image post
        elif compare_keywords(new_post.meme_words, post.meme_words) >= meme_text_similarity_limit:
            if new_post.compare_image(post) >= image_similarity_limit:
                reply(new_post, post)
                return


def main():
    posts = load_all_posts()
    new_folder = os.path.join(post_recorder.base_folder, 'new')

    while True:
        process_start_time = datetime.today()

        for i, submission in enumerate(subreddit.top('hour')):
            post_folder = os.path.join(new_folder, str(i))
            post = NewPost(submission, post_folder)

            # handle internet dropouts
            try:
                check_if_repost(post, posts)
            except prawcore.exceptions.ServerError:
                time.sleep(180)

            if process_start_time.hour < datetime.today().hour:
                break

        print('Refreshing posts at {0:02d}'.format(datetime.today().hour)+':{0:02d}'.format(datetime.today().minute))

        # clear the new posts directory
        shutil.rmtree(new_folder)
        os.mkdir(new_folder)

        if process_start_time.day < datetime.today().day:
            posts = update_posts()


main()
