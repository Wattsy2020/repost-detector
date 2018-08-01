from datetime import datetime

import post_recorder
import config


def record_all_posts(posts_per_month):
    start_month = int(datetime(config.subreddit_creation_year, config.subreddit_creation_month, 1).timestamp())
    end_month = start_month + 2592000

    while end_month < datetime.today().timestamp():
        post_recorder.record_old_posts(start_month, end_month, posts_per_month)
        print('Downloaded all posts before {}'.format(datetime.fromtimestamp(end_month)))

        # adds 30 days instead of 1 month but we only need evenly spaced intervals anyway
        start_month = end_month
        end_month += 2592000

    # record the most recent posts using praw
    post_recorder.record_new_posts('month', posts_per_month)


def print_settings():
    print('\nYour current settings are:')
    print('-'*50)
    print('{:30}{:>20}'.format('subreddit', config.subreddit))
    print('{:30}{:>20}'.format('subreddit creation month', config.subreddit_creation_month))
    print('{:30}{:>20}'.format('subreddit creation year', config.subreddit_creation_year))
    print('{:30}{:>20}\n'.format('min post score', config.min_post_score))


print_settings()
confirm = input('Are you sure you want to download posts [Y/N] ').lower()
if confirm == 'y':
    max_posts_per_month = int(input('Enter the maximum number of posts to record per month: '))

    print('\n\n\n')
    print('-'*50)
    print('Recording posts...')
    record_all_posts(max_posts_per_month)

    print("Successfully downloaded posts")
