import os
import shutil
import time
import prawcore
from datetime import datetime

import post_recorder
import image_search
import config
from post_recorder import subreddit
from post_comparison import Post, NewPost


def load_all_posts():
    posts_folder = os.path.join(post_recorder.base_folder, 'top_posts')
    posts = [Post(os.path.join(posts_folder, i.title()+'\\data.txt')) for i in os.listdir(posts_folder)]

    # sort by id so that posts[post id] gives you the post with that id
    return sorted(posts, key=lambda post: post.id)


def update_posts():
    # this won't record 100 new posts per day, it will record all the posts that are above the minimum upvotes
    post_recorder.record_new_posts('day', 100)

    # refresh image_searcher to load in the updated index.csv file
    global image_searcher
    image_searcher = image_search.ImageSearcher(post_recorder.index_file)

    # this is performed during a low traffic time so performance is not an issue, can reuse load_all_posts
    return load_all_posts()


def reply(repost: NewPost, original):
    with open(bot_activity, 'a') as file:
        file.write('{} is a repost of {}\n'.format(repost.link, original.link))
    message = config.message.format(original.title, original.link)
    print(message)
    # repost.submission.reply(message)


def check_if_repost(new_post):
    if not new_post.image_path: return  # ignore non image posts

    # compare posts with the same title
    for submission in subreddit.search("title:{}".format(new_post.title), sort='top'):
        # ignore the exact same post
        if new_post.link == ('reddit.com'+submission.permalink): continue
        if submission.score <= 25: break

        search_post = NewPost(submission, temp_folder)
        if not search_post.image_path:
            shutil.rmtree(temp_folder)
            continue

        similarity = new_post.compare_image(search_post)
        shutil.rmtree(temp_folder)

        if similarity >= config.min_similarity:
            reply(new_post, search_post)
            return

    # search through stored posts with similar colour histograms and confirm they are structurally similar
    results = image_searcher.search(new_post.features)
    for result in results:
        similar_post = posts[result[0]]
        if new_post.compare_image(similar_post) >= config.min_similarity:
            reply(new_post, similar_post)
            return


def main():
    if os.path.exists(new_folder):
        shutil.rmtree(new_folder)
    process_start_time = datetime.today()

    for submission in subreddit.stream.submissions():
        post_age = datetime.today().timestamp() - submission.created_utc
        if post_age > config.max_post_age: continue  # so the bot can be restarted without analysing a backlog of posts
        print(post_age)

        post = NewPost(submission, new_folder)

        # handle internet dropouts
        try:
            check_if_repost(post)
        except prawcore.exceptions.ServerError:
            time.sleep(180)

        shutil.rmtree(new_folder)

        # update posts when there is low traffic
        if process_start_time.day < datetime.today().day and datetime.today().hour == config.update_hour:
            print('\n refreshing posts at {0:02d}'.format(datetime.today().hour)
                  + ':{0:02d}'.format(datetime.today().minute))

            global posts
            posts = update_posts()
            process_start_time = datetime.today()


new_folder = os.path.join(post_recorder.base_folder, 'new')
temp_folder = os.path.join(post_recorder.base_folder, 'temp')
bot_activity = os.path.join(post_recorder.base_folder, 'reposts.txt')

posts = load_all_posts()
image_searcher = image_search.ImageSearcher(post_recorder.index_file)

if __name__ == '__main__':
    main()
