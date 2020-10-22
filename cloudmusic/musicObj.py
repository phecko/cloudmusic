import json

from . import download
from . import sessions
from . import api

import re


class MusicNotFoundException(Exception):

    def __str__(self):
        return "音乐信息获取失败"


class MusicLevelNotAvailableException(Exception):
    def __str__(self):
        return "音质不支持下载"


def get_real_level(br, file_type):
    print(br, file_type)
    if file_type == "flac":
        return "lossless"
    limit = [(128000, "standard"), (192000,"higher"), (320000, "exhigh")]
    for b, level in limit:
        if br < b:
            return level
    return "lossless"




def createObj(ids, level):
    api = sessions.api.Api()
    musicUrl = api.get_song_url(dict(ID = ids, level = level))['data']
    musicDetails = api.get_song_detail(dict(ID = ids))
    musicInfo = musicDetails['songs']
    musicOtp = []
    for i in range(len(ids)):
        mu = musicUrl[i]
        info = {}
        real_level = get_real_level(mu["br"], mu["type"])
        print("real level:{} br:{} size:{} url:{}".format(real_level, mu["br"], mu["size"],mu["url"]))
        if real_level != level:
            continue
        for mi in musicInfo:
            if mi['id'] == mu['id']:
                name = mi['name'] + " " + mi['alia'][0] if mi['alia'] else mi['name']
                artist = [ar['name'] for ar in mi['ar']]
                artistId = [ar['id'] for ar in mi['ar']]
                album = mi['al']['name']
                albumId = mi['al']['id']
                picUrl = mi['al']['picUrl']
                duration = mi["dt"]
                info = dict(name = name, artist = artist, album = album, picUrl = picUrl, artistId = artistId,
                            albumId = albumId, duration=duration, bitrate=mu["br"])
                musicInfo.remove(mi)
                break
        if not info:
            print("获取歌曲 %d 信息失败" % (ids[i]))
            continue

        total_levels =  [ "standard", "higher", "exhigh", "lossless"]
        available_levels = []
        chargeInfoList = musicDetails["privileges"][0]["chargeInfoList"]
        for i, v in enumerate(chargeInfoList):
            if musicDetails["privileges"][0]["downloadMaxbr"] >= v["rate"]:
                available_levels.append(total_levels[i])

        level = mu.get("level") if mu.get("level") else level
        musicOtp.append(Music(mu["id"], mu["url"], level, mu["size"], mu["type"], info, available_levels=available_levels))
    if len(musicUrl)==1 and len(musicOtp)==0:
        raise MusicNotFoundException()

    if len(musicOtp) == 1:
        return musicOtp[0]
    return musicOtp

    # musicOtp = []
    # info = {"name": "","artist": "","album": ""}
    # musicOtp = []
    # for d in data:
    #     # if detail:
    #     #     info = query.getSongInfo(d["id"])
    #     # if not info:
    #     #     print("歌曲不存在 id=" + str(d["id"]))
    #     #     continue
    #     musicOtp.append(Music(d["id"], d["url"], d["level"], d["size"], d["type"], info))
    #     if len(data) == 1:
    #         return musicOtp[0]
    



class Music:
    def __init__(self, id_, url, level, size, type_, info, available_levels=[]):
        self.url = url
        self.id = str(id_)
        self.level = level
        self.size = int(size)
        self.type = type_
        self.name = info['name']
        self.duration = info['duration']
        self.bitrate = info["bitrate"]
        self.artist =  info['artist']
        self.album = info['album']
        self.artistId = info['artistId']
        self.albumId = info['albumId']
        self.picUrl = info['picUrl']
        self.available_levels=available_levels
        self.para = {
            "clas" : "",
            "ID" : self.id,
            "number" : 15,
            "offset" : 0,
        }
        self.levels = ["standard", "higher", "exhigh", "lossless"]


    def __repr__(self):
        return "<Music object - "+ self.id +">"

    def download(self, dirs="", level=None, name=None, exist_ok=False):
        if self.type:
            if level is None or level == self.level:
                return download.download(dirs, self, name=name, exist_ok=exist_ok)
            elif level in self.available_levels:
                music =createObj([self.id], level)
                if isinstance(music, Music):
                    return music.download(dirs=dirs, name=name, exist_ok=exist_ok)
                else:
                    raise MusicLevelNotAvailableException()

            else:
                # level = self.available_levels[-1] if self.available_levels else "standard"
                # print("没有这个level, 默认最高质量: %s" % level)
                # return createObj([self.id], level).download()
                raise MusicLevelNotAvailableException()
        else:
            print("download failed - " + self.id)
            return None

    # 获取评论数量
    def getCommentsCount(self):
        self.para["clas"] = "count"
        with sessions.Session() as session:
            return session.comment(self.para)

    # 获取热评，上限15
    def getHotComments(self, number=15):
        self.para["clas"] = "hot"
        self.para["number"] = number
        with sessions.Session() as session:
            return session.comment(self.para)
    
    # 获取评论，时间顺序，从最近的一直向后
    def getComments(self, number):
        self.para["clas"] = "new"
        self.para["number"] = str(number)
        with sessions.Session() as session:
            return session.comment(self.para)

    # 获取歌词
    def getLyrics(self):
        lrc =  api.Api().get_lyrics(dict(ID = self.id))
        lyric = ""
        tlyric = ""
        
        if "lrc" in lrc:
            lyric = lrc["lrc"]["lyric"]
            if "lyric" in lrc["tlyric"]:
                tlyric = lrc["tlyric"]["lyric"]

        return [lyric, tlyric]

