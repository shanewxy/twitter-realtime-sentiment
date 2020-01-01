DESIGN_DOCS = {
    "_id": "_design/statistics",
    "views": {
        "all_tweets": {
            "map": "function (doc){emit(doc)}"
        },
        "zones_sentiment": {
            "map": "function(doc){if(doc.place,doc.score){emit([doc.place], doc.score)}}",
            "reduce": "_stats"
        },
        "realtime_zone": {
            "map": "function(doc){if(doc.timestamp,doc.place,doc.score)emit(doc.timestamp,[doc.place,doc.score])}"
        }
    }
}
