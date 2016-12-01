import re
import uuid
import time

NAME = 'WatchAir'
ART = R('art.png')
ICON = R('waicon.png')
PREFIX = "/video/watchair"

CHANNELCACHE=600

def Start():
    Log("Start called")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    ObjectContainer.title1 = NAME
    ObjectContainer.view_group = "List"
    DirectConnect()
    GetChannels()


def ValidatePrefs():
    pattern = re.compile(r'(([01]?[0-9]?[0-9]|2[0-4][0-9]|2[5][0-5])\.){3}([01]?[0-9]?[0-9]|2[0-4][0-9]|2[5][0-5])(:[0-9]+)?')
    if not pattern.match(Prefs["watchair_ip"]):
        return ObjectContainer(header="Error", message="The provided IP address '%s' is not valid")
    else:
        try:
            DirectConnect()
        except Exception as err:
            print "Error: %s" % (str(err))



@route(PREFIX + "/error/{message}")
def ErrorMessage(message):
    return ObjectContainer(header="Error", message=message)

def timestamp():
    return int(time.time())

def clearChannelCache():
    if "channel_expire_epoch" in Dict: del Dict["channel_expire_epoch"]
    if "channels" in Dict: del Dict["channels"]
    Dict.Save()

def GetChannels(fresh=False):

    if fresh:
        clearChannelCache()

    if "channel_expire_epoch" in Dict:
        if timestamp() > int(Dict["channel_expire_epoch"]):
            Log("Expiring channel cache")
            clearChannelCache()
        else:
            Log("Returning cached channels")
            return Dict["channels"]


    url = "http://"+Prefs["watchair_ip"]+"/mml.do?cmd=getServiceList&sessionid=%s" % (Dict["sid"])
    channel_xml = XML.ElementFromURL(url,timeout=5,cacheTime=CHANNELCACHE)
    ar = {}
    for ch in channel_xml.xpath("//Body/ServiceList/Service"):
        title = "%s (%s.%s)" % (ch.xpath("ShortName")[0].text, ch.xpath("MajorChannelNumber")[0].text, ch.xpath("MinorChannelNumber")[0].text)
        channel_id = int(ch.xpath("UniqueId")[0].text)
        ar[channel_id] = title

    Dict["channels"] = ar
    Dict["channel_expire_epoch"] = timestamp() + CHANNELCACHE
    Dict.Save()

    return ar


def DirectConnect():
    oc = ObjectContainer(title1=NAME)
    try:
        if "cid" in Dict:
            cid = Dict["cid"]
        else:
            cid = str(uuid.uuid4()).upper()
            Dict["cid"] = cid
            Dict.Save()

        dev_url = "http://"+Prefs["watchair_ip"]+"/mml.do?cmd=connect&clientid=%s&timeout=0" % (cid)
        dev_info = XML.ElementFromURL(dev_url,timeout=5,cacheTime=0)
        Dict["sid"] = dev_info.xpath('//Hdr/SessionID')[0].text
        Dict.Save()
        GetChannels()
    except Exception as err:
        oc.add(DirectoryObject(key = Callback(ErrorMessage, message = "WatchAir: Not detected. Check IP"), title = "Error: WatchAir"))
        Log.Error("WatchAir: %s" % (str(err)))


@route(PREFIX + '/PlayLive')
@indirect
def PlayLive(channel=None, bitrate=None, container=True, change=False):
    channels = GetChannels()
    ch = channels[int(channel)]
    Log("[ Channel ID: %s, Bitrate: %s ]" % (channel, bitrate))

    if change:
        churl = "http://"+Prefs["watchair_ip"]+"/mml.do?cmd=startstreamingdata&sessionid=%s&uniqueid=%d&tvbps=%d&force=1" % (Dict["sid"], int(channel), int(bitrate))
        Log("churl: " + churl)
        change_xml = XML.ElementFromURL(churl,timeout=5,cacheTime=60)
        Log(XML.StringFromObject(change_xml))
        url = change_xml.xpath("//Body/Media/Url")[0].text

        Log("Url: %s" % (url))

        media = VideoClipObject(
            key = Callback(PlayLive, channel=channel, bitrate=bitrate, change=True, container=True),
            rating_key = ch,
            title = ch,
            items = [
                MediaObject(
                    video_resolution = 720,
                    optimized_for_streaming = True,
                    parts = [PartObject(key = HTTPLiveStreamURL(url=url))]
                )
            ]
        )
    else:
        media = VideoClipObject(
            key = Callback(PlayLive, channel=channel, bitrate=bitrate, change=True, container=True),
            rating_key = ch,
            title = ch
        )

    if container:
        return ObjectContainer(objects=[media],no_cache=True)
    else:
        return media


@route(PREFIX + "/ChannelMenu", channel = int)
def ChannelMenu(channel = None):
    channels = GetChannels()
    channel = int(channel)
    bitrates = {
        1500000: "Low",
        3000000: "Medium",
        5000000: "High"
    }
    chtitle = channels[channel]
    oc = ObjectContainer()
    for br in bitrates.keys():
        desc = bitrates[br]
        title = "%s - %s quality" % (chtitle, desc)
        oc.add(DirectoryObject(key=Callback(PlayLive, channel = channel, bitrate=br, container = True), title=title))

    return oc

@route(PREFIX + "/Reboot")
def RebootDevice():
    oc = ObjectContainer()
    sid = Dict["sid"]
    dev_url = "http://"+Prefs["watchair_ip"]+"/mml.do?cmd=reboot&sessionid=%s" % (sid)
    dev_info = XML.ElementFromURL(dev_url,timeout=5,cacheTime=0)
    Log(XML.StringFromObject(dev_info))

    oc.add(DirectoryObject(key=Callback(CommandMenu), title="Device is rebooting, please wait 60 seconds then select this option", thumb=ICON, art=ART))
    return oc

@route(PREFIX + "/ClearCache")
def ClearCache():
    Dict.Reset()
    Dict.Save()
    return CommandMenu()

@route(PREFIX + "/Confirm")
def Confirm(ConfirmF, CancelF, msg=""):
    oc = ObjectContainer()
    if len(msg) > 0: oc.add(DirectoryObject(key=Callback(Confirm, ConfirmF=ConfirmF, CancelF=CancelF, msg=msg), title=msg, thumb=ICON, art=ART))
    oc.add(DirectoryObject(key=Callback(ConfirmF), title="Confirm", thumb=ICON, art=ART))
    oc.add(DirectoryObject(key=Callback(CancelF), title="Cancel", thumb=ICON, art=ART))
    return oc

@route(PREFIX + "/Commands")
def CommandMenu():
    oc = ObjectContainer()
    oc.add(DirectoryObject(key=Callback(ClearCache), title="Clear cache", thumb=ICON, art=ART))
    oc.add(DirectoryObject(key=Callback(RebootDevice), title="Reboot", thumb=ICON, art=ART))
    oc.add(DirectoryObject(key=Callback(MainMenu), title="Back", thumb=ICON, art=ART))
    return oc

@route(PREFIX + "/AllChannels")
def AllChannels():
    change = True
    if Client.Product in ["Plex Web"]:
        change = False

    Log("AllChannels: " + Client.Product)
    Log("Change value: " + str(change))
    channels = GetChannels()
    oc = ObjectContainer()
    Log("MainMenu channel count: %d" % (len(channels.keys())))
    ks = [ int(x) for x in channels.keys() ]
    ks.sort()
    Log(ks)
    for k in ks:
        v = channels[k]
        oc.add(VideoClipObject(key=Callback(PlayLive, channel = k, bitrate=3000000, change=change, container = True), thumb=ICON, art=ART, title=v, rating_key=v))
    return oc


@handler(PREFIX, NAME, thumb="waicon.png", art="art.png")
def MainMenu():
    oc = ObjectContainer()
    if Prefs["watchair_ip"] == None or len(Prefs["watchair_ip"]) ==0:
        Log("IP address not set")
        oc.add(DirectoryObject(key=Callback(MainMenu), title="Set the IP address of the WatchAir device to use this channel"))
        return oc

    oc.add(DirectoryObject(key=Callback(AllChannels), title="TV Channels", thumb=ICON, art=ART))
    oc.add(DirectoryObject(key=Callback(CommandMenu), title="Device Commands", thumb=ICON, art=ART))
    return oc
