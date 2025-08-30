Python 3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> # First install the emoji library with:
... # pip install emoji
... 
... import emoji
... 
... # Dictionary of emojis with their human-readable names
... emoji_dict = {
...     "😀": "grinning face",
...     "😃": "smiling face with big eyes",
...     "😄": "smiling face with smiling eyes",
...     "😁": "beaming face",
...     "😆": "grinning squinting face",
...     "😅": "grinning face with sweat",
...     "😂": "face with tears of joy",
...     "🤣": "rolling on the floor laughing",
...     "😊": "smiling face with blushing cheeks",
...     "😍": "smiling face with heart-eyes",
...     "😘": "face blowing a kiss",
...     "😎": "smiling face with sunglasses",
...     "🤩": "star-struck",
...     "😋": "face savoring food",
...     "😜": "winking face with tongue",
...     "🤔": "thinking face",
...     "😴": "sleeping face",
...     "😷": "face with medical mask",
...     "🤖": "robot",
...     "👋": "waving hand",
...     "👍": "thumbs up",
...     "👎": "thumbs down",
...     "🙏": "folded hands",
...     "❤": "red heart",
...     "🔥": "fire",
...     "⭐": "star",
...     "🌙": "moon",
...     "☀": "sun",
...     "🌍": "earth globe",
...     "🚀": "rocket",
...     "⚽": "soccer ball",
...     "🎵": "musical note",
...     "🎉": "party popper",
...     "💡": "light bulb",
...     "📚": "books",
...     "💻": "laptop",
...     "📱": "mobile phone",
...     "🍎": "red apple",
...     "🍕": "pizza",
    "🍔": "burger",
    "⚡": "high voltage"
}

# Print each emoji with its name
for symbol, name in emoji_dict.items():
