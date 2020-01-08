from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd


def common_topic(content, limit):
    tokenized_word = word_tokenize(content)
    stop_words = set(stopwords.words("english"))
    filtered_sent = []
    for w in tokenized_word:
        if len(w) > 1 and w not in stop_words:
            filtered_sent.append(w.lower())
    fdist = FreqDist(filtered_sent)
    fd = pd.DataFrame(fdist.most_common(limit),
                      columns=["Word", "Frequency"]).reindex()
    return fd.items()


if __name__ == '__main__':
    import nltk
    import ssl

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    nltk.download()
    print(common_topic(
        "Then tokenize the entire text from all tweets, use Stop Words to remove commonly used words tweets, and extract 10 most common words in the Frequency Distribution of all words.",
        10))
