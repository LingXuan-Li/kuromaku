import re

def message_parse(text: str) -> str:
    # RED
    text = re.sub(r'\*(.*?)\*', r'<span style="color: red;">\1</span>', text)

    # GREEN
    text = re.sub(r'#(.*?)#', r'<span style="color: green;">\1</span>', text)

    # ORANGE
    text = re.sub(r'\$(.*?)\$', r'<span style="color: orange;">\1</span>', text)
    
    return text


md = """
これは*赤*と#緑#と$オレンジ$です
"""

print(message_parse(md))