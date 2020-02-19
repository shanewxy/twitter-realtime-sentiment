import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import json


# Get the polarity score using TextBlob
def get_textblob_sent(text):
    # This polarity score is between -1 to 1
    polarity = TextBlob(text).sentiment.polarity
    textblob_sent = 1 if polarity >= 0 else 0
    return textblob_sent


    # Get the compound score using VADER
def get_vader_sent(text):
    score = SentimentIntensityAnalyzer().polarity_scores(text)
    compound = score['compound']
    return 1 if compound >= -0.05 else 0


if __name__ == '__main__':

    textblob_corrret = 0
    vader_correct = 0

    with open("/Users/pengkedi/Documents/twitter-realtime-sentiment/data_collection/text_labelled.txt") as f:
        for cnt, line in enumerate(f):
            try:
                line = line.strip('\n')
                text = line[:-1].strip('\t')
                sent = int(line[-1])

                textblob_sent = get_textblob_sent(text)
                if textblob_sent == sent:
                    textblob_corrret += 1

                vader_sent = get_vader_sent(text)
                if vader_sent == sent:
                    vader_correct += 1

            except Exception as e:
                print(e)
                continue

    num_lines = 3000
    print("Accuracy of Textblob = {}% via {} samples".format(textblob_corrret / num_lines * 100.0, num_lines))
    print("Accuracy of VADER  = {}% via {} samples".format(vader_correct / num_lines * 100.0, num_lines))
