DESIGN_DOCS = {
    "_id": "_design/statistics",
    "views": {
        "all_tweets": {
            "map": "function (doc){emit(doc)}"
        },
    }
}
