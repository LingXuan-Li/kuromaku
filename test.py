import re

MESSAGE_INDEX = 0

def message_parse(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'<span style="color: red;">\1</span>', text)
    text = re.sub(r'\$\$(.*?)\$\$', r'<span style="color: springgreen;">\1</span>', text)
    text = re.sub(r'\@\@(.*?)\@\@', r'<span style="color: orange;">\1</span>', text)
    return text


def get_info():
    global MESSAGE_INDEX

    messages = [
        "**【衛環からのお知らせ】** $$水分補給$$・@@塩分補給@@しっかりしようね",
        "めっちゃ**スポイベ**いいよね",
        "**スポイベ**を@@淘汰@@するなー",
        "@@ルールは破るためにある@@ ―by 壊滅開拓者"
    ]

    message = messages[MESSAGE_INDEX]
    message = message_parse(message)

    MESSAGE_INDEX = (MESSAGE_INDEX + 1) % len(messages)

    return [message]


while True:
    print(get_info())