# General Structure

A typical Location History extraction from [Google Takeout] will look something like this:

<pre><code><ic-folder>Takeout/</ic-folder>
├─ <ic-file>archive_browser.html</ic-file>
└─ <ic-folder>Location History/</ic-folder>
   ├─ <ic-file>Records.json</ic-file>
   ├─ <ic-file>Settings.json</ic-file>
   ├─ <ic-file>Timeline Edits.json</ic-file>
   └─ <ic-folder>Semantic Location History/</ic-folder>
      │  ...
      ├─ <ic-folder>2020/</ic-folder>
      │  ├─ <ic-file>2020_JANUARY.json</ic-file>
      │  ├─ <ic-file>2020_FEBRUARY.json</ic-file>
      │  │  ...
      │  └─ <ic-file>2020_DECEMBER.json</ic-file>
      └─ <ic-folder>2021/</ic-folder>
         ├─ <ic-file>2021_JANUARY.json</ic-file>
         ├─ <ic-file>2021_FEBRUARY.json</ic-file>
         │  ...
         └─ <ic-file>2021_DECEMBER.json</ic-file>
</code></pre>


!!! warning

    Folder names might be different for Google accounts in different languages.


From here, the most relevant files and folders are:

<ic-file>**[Records.json]**</ic-file>
:   This file contains all available raw Location History data.
    See [Raw Location History Data] for more information.

<ic-file>**[Settings.json]**</ic-file>
:   This file contains additional auxiliary metadata, like information about the devices used and account settings.

<ic-file>**[Timeline Edits.json]**</ic-file>

<ic-folder>**[Semantic Location History][Semantic Location History Data]**</ic-folder>
:   This folder contains higher-level information about the user's inferred activity and movements.
    There is one subfolder for each year of data, and inside each subfolder one file for each month.
    See [Semantic Location History Data] for more information.


[Google Takeout]: https://takeout.google.com/settings/takeout
[Raw Location History Data]: raw-location.md
[Semantic Location History Data]: semantic-location.md
[Records.json]: ../reference/records.md
[Settings.json]: ../reference/settings.md
[Timeline Edits.json]: ../reference/timeline-edits.md
