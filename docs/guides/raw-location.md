# Raw Location History Data

Raw Location History data consists of a list of timestamped location records in chronological order for all the historical location data available and presumably at the most granular level possible.

This raw Location History data is found in the `Records.json` file (see [General Structure]).
Inside this file we can find a single flat `locations` array containing all of the location records:

```json title="Records.json"
{
  "locations" : [...]
}
```

Each of the location records in this array has a very similar structure.
A location record might look like this:

```json title="Example location record"
{
    "timestamp": "2022-01-12T17:18:24.190Z",
    "latitudeE7": 414216106,
    "longitudeE7": 21684775,
    "accuracy": 47,
    "velocity": 0,
    "heading": 188,
    "altitude": 89,
    "verticalAccuracy": 27,
    "source": "WIFI",
    "deviceTag": 1234567890,
    "platformType": "ANDROID"
}
```

From this, the most essential fields are:

  - **`timestamp`**: Timestamp of the record as a string in [ISO 8601] format (`YYYY-MM-DDTHH:mm:ss.sssZ`).
  The suffixed `Z` indicates that the time is in the [UTC] time zone.
  - **`latitudeE7`** and **`longitudeE7`**: Coordinates (latitude and longitude) of the location reported as integers.
  The values need to be divided by 10^7^ to be in the expected range.

For more information on the other possible fields see the full [format definition][Location Record].

[General Structure]: general-structure.md
[Location Record]: ../reference/records.md#location-record
[ISO 8601]: https://en.wikipedia.org/wiki/ISO_8601
[UTC]: https://en.wikipedia.org/wiki/Coordinated_Universal_Time
