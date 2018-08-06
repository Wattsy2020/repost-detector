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
    # this won't record 200 new posts per day, it will record all the posts that are above the minimum upvotes
    post_recorder.record_new_posts('day', 200)

    # refresh image_searcher to load in the updated index.csv file
    global image_searcher
    image_searcher = image_search.ImageSearcher(post_recorder.index_file)

    # this is performed during a low traffic time so performance is not an issue, can reuse load_all_posts
    return load_all_posts()


def reply(repost: NewPost, original):
    if repost.link in replied: return

    with open(bot_activity, 'a') as file:
        file.write('{} is a repost of {}\n'.format(repost.link, original.link))
    message = config.message.format(original.title, original.link)
    # repost.submission.reply(message)
    replied.append(repost.link)


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
    results = [posts[result[0]] for result in image_searcher.search(new_post.features)]
    for similar_post in results:
        if new_post.compare_image(similar_post) >= config.min_similarity:
            reply(new_post, similar_post)
            return


def main():
    process_start_time = datetime.today()

    # this is wrapped in a try except to prevent internet dropouts crashing the bot
    while True:
        try:
            for submission in subreddit.stream.submissions():
                post_age = datetime.today().timestamp() - submission.created_utc
                if post_age > config.max_post_age: continue  # so the bot can be restarted without analysing old posts
                print(post_age)

                post = NewPost(submission, new_folder)
                check_if_repost(post)
                shutil.rmtree(new_folder)

                # update posts when there is low traffic
                if process_start_time.day < datetime.today().day and datetime.today().hour == config.update_hour:
                    print('\n refreshing posts at {0:02d}'.format(datetime.today().hour)
                          + ':{0:02d}'.format(datetime.today().minute))

                    global posts
                    posts = update_posts()
                    process_start_time = datetime.today()
        except prawcore.exceptions.ServerError:
            print("Error occured while connecting to reddit, restarting stream")
            time.sleep(300)
        except Exception as e:
            print("\n\n\nError occured: {}".format(e))
            print("If this isn't an internet connection error please report it "
                  "at https://github.com/Wattsy2020/repost-detector/issues\n\n\n")
            time.sleep(300)


new_folder = os.path.join(post_recorder.base_folder, 'new')
temp_folder = os.path.join(post_recorder.base_folder, 'temp')

if os.path.exists(new_folder): shutil.rmtree(new_folder)
if os.path.exists(temp_folder): shutil.rmtree(temp_folder)

bot_activity = os.path.join(post_recorder.base_folder, 'reposts.txt')
replied = []  # track replied too posts, if an error occurs and the bot has to restart it won't reply to a post twice

posts = load_all_posts()
image_searcher = image_search.ImageSearcher(post_recorder.index_file)

if __name__ == '__main__':
    main()
