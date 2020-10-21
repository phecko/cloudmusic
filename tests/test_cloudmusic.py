from unittest import TestCase
import cloudmusic
import time

class TestCloudmusic(TestCase):

    def test_getMusic(self):

        music_obj = cloudmusic.getMusic(1486622313)

        for l in music_obj.available_levels:
            try:
                music_obj.download(level=l)
                print("level {} 获取成功 {}".format(l, music_obj.bitrate))
            except (cloudmusic.MusicLevelNotAvailableException, cloudmusic.MusicNotFoundException):
                print("level {} 获取失败".format(l))

        self.assertIsNotNone(music_obj)
        pass