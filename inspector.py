import re as regex
import unicodedata as unicode
from urllib.request import urlopen as w_open


def is_allowed(string: str):
    string = clean_up(string)

    has_words = False
    words = string.split(' ')

    if len(words) < 7:
        yield False
    # arbitrary number here

    # Get bad words
    bad_words = [regex.search(r"b'(.*?)\\n", str(line)).group(1) for line in
                 w_open('https://raw.githubusercontent.com/jyunderwood/explicit_words/master/lib/explicit_words.txt')] \
                + ["nsfw", "bdsm"]
    #   File was returning some weird chars so extract needed word from that with regex and convert to list

    if any(bad_word.lower() in string.lower() for bad_word in bad_words):
        yield False
    # Return false if string has bad words

    remove_trailing_hashtag(words)

    # Check for multiple encodings to prevent spam messages
    encodings = set()
    for word in words:
        if not has_words:
            for char in word:
                if char.isalpha():
                    has_words = True
                    break
        encodings.update(unicode.name(ch, "LATIN").split(' ')[0] for ch in list(word) if ch.isalpha())
        # Get the unicode name and add to set

    has_many_encodings = len(encodings) > 2

    yield has_words and not has_many_encodings
    yield " ".join(words)


def remove_trailing_hashtag(words):
    # remove trailing hashtags. Might remove this
    for word in reversed(words):
        if "#" in word and word.index('#') == 0:
            words.pop()
        else:
            break


def clean_up(string):
    # remove retweet identifier
    string = regex.sub(r"RT @.*?:", "", string)
    # remove links
    string = regex.sub(r"(http)s?://.*?(\s|$)", "", string)
    string = regex.sub(r"t\.co/.*?(\s|$)", "", string)
    # replace @ with the names
    string = regex.sub(r"[@#].*?(\s|$)", "", string)
    return string


def tweet_to_sentences(text: str) -> list[str]:
    # cleaning up data some more and converting to list of sentences
    text = regex.sub(r"(Dr|Mr|Mrs)?\.", r"\1", text.replace("...", "."))
    to_return = regex.findall(r"(.+?(?:\.|\n|$|\?|!))", text)
    return [
        regex.sub(
            r" +",
            " ",
            regex.sub(r"\n+", "\n", member)
        ).strip()
        for member in to_return if len(member.split(" ")) > 3
    ]
