from datetime import datetime
import main


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
