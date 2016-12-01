# WatchAir Plex Channel Plugin

## Installation

  1. Clone this repository locally `git clone https://github.com/bsharper/WatchAir.bundle`
  2. Find the Plex plugins path [(click here for more information)](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-)
  3. Copy the whole WatchAir.bundle folder into your Plugins folder.
  4. Open the Plex **web interface**. If Plex is running locally, [http://127.0.0.1:32400/web/index.html](http://127.0.0.1:32400/web/index.html) should work.
  5. On the left side of the page underneath your libraries, click "Channels"
  6. **IMPORTANT: Click on the settings (gear) button on the WatchAir channel before trying to use the channel. You'll need to enter the IP address of the WatchAir device**. If you can't find the IP address, look in the official app under settings.
  7. Open Plex on the Apple TV. Open Channels, WatchAir, TV Channels, pick a channel, and that's it!


## Bugs

Yep, there are many bugs. This is my first Plex plug-in, so I'm sure there are many issues lurking under the surface. Tuning to a channel doesn't always work on the Plex Web Client. The work-around for this is to tune in to the channel using Plex ATV / iOS / Android, then trying the same channel on the Web Client. This seems to work reasonably well on the Apple TV 4 on the official Plex app, which was my target device.

If you want to help but are just getting started, take a look at some other channel plugins to get an idea of how things are put together: [https://github.com/plexinc-plugins](https://github.com/plexinc-plugins)

## Quality

Open `__init__.py` under Content/Code and search for `bitrate=3000000`. Changing that number changes the bitrate. For example, changing it to `bitrate=5000000` seems to work for me, but it depends on your router.
