# Semantic Location History Data

Semantic Location History data consists of more high-level and processed information compared to the raw Location History data.
This semantic information is the same information that can be seen in the [Timeline] pages on the Google Maps website and app.
Instead of individual raw location records, here the information is aggregated and summarized as a sequence of inferred
*place visits* and *activity segments* between *place visits*, all with a start time and an end time.


![Example screenshot of the Timeline page on the Google Maps website.](../static/images/semantic_example.png)


This semantic data can be found inside the `Semantic Location History` folder.
The data is partitioned by year in different subfolders (named e.g. `2021`,  `2022`...).
And for each year, the data is partitioned again by month in different JSON files (named e.g. `2022_JANUARY.json`, `2022_FEBRUARY.json` etc.).

Inside each semantic JSON file we can find a single flat `timelineObjects` array:
```json title="Example semantic JSON file"
{
  "timelineObjects" : [...]
}
```

Each of the *timeline objects* in this array is either an `activitySegment` or a `placeVisit`.


!!! note "To Do"

    This page is incomplete.


[Timeline]: https://timeline.google.com