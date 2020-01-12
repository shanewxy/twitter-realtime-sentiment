from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
import re


def common_words(content, limit):
    tokenized_word = word_tokenize(content)
    stop_words = set(stopwords.words("english"))
    filtered_sent = []
    for w in tokenized_word:
        if len(w) > 2 and w not in stop_words:
            filtered_sent.append(w.lower())
    fdist = FreqDist(filtered_sent)
    fd = pd.DataFrame(fdist.most_common(limit),
                      columns=["Word", "Frequency"]).reindex()
    return fd.items()


def common_topics(content, limit):
    # tokenized_word = word_tokenize(content)
    # stop_words = set(stopwords.words("english"))
    filtered_sent = find_hashtags(content)
    # for w in filtered_sent:
    #     w = re[1:]
    fdist = FreqDist(filtered_sent)
    fd = pd.DataFrame(fdist.most_common(limit),
                      columns=["Word", "Frequency"]).reindex()
    print(fd)
    return fd.items()


def find_hashtags(tweet):
    '''This function will extract hashtags'''
    return re.findall('(#[A-Za-z]+[A-Za-z0-9-_]+)', tweet)


if __name__ == '__main__':
    # import nltk
    # import ssl
    #
    # try:
    #     _create_unverified_https_context = ssl._create_unverified_context
    # except AttributeError:
    #     pass
    # else:
    #     ssl._create_default_https_context = _create_unverified_https_context
    #
    # nltk.download()
    print(common_topics(
        "#Then tokenize the entire text from all tweets, use Stop Words to remove commonly used words tweets, and extract 10 most common words in the Frequency Distribution of all words.",10))
