DESIGN_DOCS_TWEETS = {
    "_id": "_design/sentiment",
    "views": {
        "all_tweets": {
            "map": "function (doc){emit(doc)}"
        },
        "zones_sentiment": {
            "map": "function(doc){if(doc.place,doc.sentiment){emit([doc.place], doc.sentiment)}}",
            "reduce": "_stats"
        },
        "realtime_zone": {
            "map": "function(doc){if(doc.timestamp,doc.place,doc.sentiment,doc.user_id)emit(doc.timestamp,[doc.place,doc.sentiment,doc.user_id,doc.text])}"
        },
    }
}
DESIGN_DOCS_STATS = {
    "_id": "_design/stats",
    "views": {
        "historic_stats": {
            "map": "function(doc){if(doc.place,doc.avg){emit([doc.place,doc.start_time,doc.end_time], [doc.count,doc.avg])}}",
        }
    }
}
