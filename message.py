message = '''
Accusation: General Reposti!
Observation: This post appears to be similar to [post_title](post_link)
Query: May I eliminate the meatbag master?

[Source code](https://github.com/Wattsy2020/repost-detector)
'''


def get_message(title, link):
    reply = message.replace('post_title', title)
    reply = reply.replace('post_link', link)

    return reply
