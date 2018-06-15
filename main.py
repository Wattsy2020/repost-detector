import os
import shutil
import time
import praw
import prawcore
from datetime import datetime

import post_recorder
import message
from post_recorder import subreddit
from post_comparison import Post, NewPost, compare_keywords


def record_all_posts(posts_per_month):
    start_month = int(datetime(2017, 1, 1).timestamp())
    end_month = int(datetime(2017, 2, 1).timestamp())

    while end_month < datetime.today().timestamp():
        post_recorder.record_old_posts(start_month, end_month, posts_per_month)

        # this actually adds 30 days instead of 1 month but that doesn't matter much
        start_month = end_month
        end_month += 2592000

    # record the most recent posts using praw
    post_recorder.record_new_posts('month', posts_per_month)


def load_all_posts():
    posts_folder = os.path.join(post_recorder.base_folder, 'top_posts')

    posts = [Post(os.path.join(posts_folder, i.title()+'\\data.txt')) for i in os.listdir(posts_folder)]
    return sorted(posts, key=lambda item: -item.date)  # need negative sign to sort by most recent date


def update_posts():
    post_recorder.record_new_posts('day', 35)

    # this is performed during a low traffic time so performance is not an issue
    return load_all_posts()


def reply(repost: NewPost, original):
    with open(output_storage_file, 'a+') as storage:
        storage.write('{} is a repost of {}\n'.format(repost.link, original.link))

    '''
    reply_message = message.get_message(original.title, original.link)

    # handle deleted posts
    try:
        repost.submission.reply(reply_message)
    except praw.exceptions.APIException:
        return
    '''


def check_if_repost(new_post, text_similarity_limit):
    # print('\nChecking: {}       Meme text: {}'.format(new_post.title, new_post.meme_words))
    meme_text_similarity_limit = text_similarity_limit
    title_similarity_limit = .7
    image_similarity_limit = .9

    # compare posts with the same title
    temp_folder = os.path.join(post_recorder.base_folder, 'temp')
    for submission in subreddit.search("title:{}".format(new_post.title), sort='top'):
        # ignore the exact same post
        if new_post.link == ('reddit.com'+submission.permalink): continue
        if submission.score <= 25: break

        search_post = NewPost(submission, temp_folder, get_text=False)

        # ignore gifs
        if new_post.image_path == '' or search_post.image_path == '':
            shutil.rmtree(temp_folder)
            continue

        similarity = new_post.compare_image(search_post)
        shutil.rmtree(temp_folder)

        if similarity >= image_similarity_limit:
            reply(new_post, search_post)
            return

    # search for posts with similar meme_words and use image comparison on the matches
    for post in posts:
        # ignore gifs
        if new_post.image_path == '' or post.image_path == '':
            continue

        # compare blank images
        if not new_post.meme_words:
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
    process_start_time = datetime.today()

    for submission in subreddit.stream.submissions():
        post_age = datetime.today().timestamp() - submission.created_utc
        if post_age > 3600: continue  # so the bot can be restarted without analysing a backlog of posts
        print(post_age)

        post = NewPost(submission, new_folder)
        # can afford to spend more time analysing a post if we've analysed the rest of the submission stream
        text_similarity_limit = .15 if post_age < 360 else .25

        # handle internet dropouts
        try:
            check_if_repost(post, text_similarity_limit)
        except prawcore.exceptions.ServerError:
            time.sleep(180)

        shutil.rmtree(new_folder)

        # update posts when there is low traffic (adjust hour depending on your timezone)
        if process_start_time.hour < datetime.today().hour == 12:
            print('\n refreshing posts at {0:02d}'.format(datetime.today().hour)
                  + ':{0:02d}'.format(datetime.today().minute))

            global posts
            posts = update_posts()
            process_start_time = datetime.today()


posts = load_all_posts()
print('done')
new_folder = os.path.join(post_recorder.base_folder, 'new')
output_storage_file = os.path.join(post_recorder.base_folder, 'reposts.txt')

if __name__ == '__main__':
    main()
