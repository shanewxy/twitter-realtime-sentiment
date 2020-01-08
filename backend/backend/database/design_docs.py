DESIGN_DOCS_TWEETS = {
    "_id": "_design/sentiment",
    "views": {
        "all_tweets": {
            "map": "function (doc){emit(doc)}"
        },
        "zones_sentiment": {
            "map": "function(doc){if(doc.sa2_name){emit([doc.sa2_name,doc.sa2_code], doc.sentiment)}}",
            "reduce": "_stats"
        },
        "realtime_zone": {
            "map": "function(doc){if(doc.timestamp,doc.sa2_name,doc.sentiment,doc.user_id)emit(doc.timestamp,[doc.sa2_name,doc.sa2_code,doc.sentiment,doc.user_id])}"
        },
        "tweets_content": {
            "map": "function(doc){emit(doc.timestamp,doc.text)}"
        }
    }
}
DESIGN_DOCS_STATS = {
    "_id": "_design/stats",
    "views": {
        "historic_stats": {
            "map": "function(doc){if(doc.sa2_name,doc.avg){emit([doc.sa2_name,doc.sa2_code,doc.start_time,doc.end_time], [doc.count,doc.avg])}}",
        }
    }
}
