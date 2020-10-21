from unittest import TestCase
import cloudmusic


class TestCloudmusic(TestCase):

    def test_getMusic(self):


        music_obj = cloudmusic.getMusic(1479289902)
        #

        for l in music_obj.available_levels:
            print(l, music_obj.size)

        print(music_obj.available_levels)

        self.assertIsNotNone(music_obj)
        pass