# coding:utf-8
# @Time    : 2025/5/6 上午2:17
# @Author  : Mark
# @FileName: singleVideoCrawler.py
import json
import re
from pprint import pprint

import requests
from f2.apps.douyin.handler import DouyinHandler
from apiproxy.common import utils


class Single_Video_Crawler:

    def __init__(self, Video_share_url: str):
        self.url = Video_share_url
        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/122.0.0.0"
                          "Safari/537.36 Edg/122.0.0.0",
        }
        self.kwargs = {
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                              "like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
                "Referer": "https://www.douyin.com/",
            },
            "timeout": 10,
            "proxies": {"http://": None, "https://": None},
            "cookie": f"msToken={utils.generate_random_str(107)}; ttwid={utils.getttwid()}; odin_tt=324fb4ea4a89c0c05827e18a1ed9cf9bf8a17f7705fcc793fec935b637867e2a5a9b8168c885554d029919117a18ba69; passport_csrf_token=f61602fc63757ae0e4fd9d6bdcee4810;",
        }

    def get_video_id(self):
        r = requests.get(url=self.url, headers=self.base_headers, allow_redirects=False)
        if 'Location' in r.headers:
            r = requests.get(url=r.headers['Location'], headers=self.base_headers, allow_redirects=False)
        if 'Location' in r.headers:
            if "video/" in r.headers['Location']:
                video_id = re.findall(r'video/(\d+)(?=[/?])', r.headers['Location'])[0]
                return video_id, "video"
            elif "note/" in r.headers['Location']:
                video_id = re.findall(r'note/(\d+)(?=[/?])', r.headers['Location'])[0]
                return video_id, "note"
            elif "slides/" in r.headers['Location']:
                video_id = re.findall(r'slides/(\d+)(?=[/?])', r.headers['Location'])[0]
                return video_id, "slides"
            else:
                return None, None

    async def get_video_info(self, aweme_id: str, video_type: str):
        video = await DouyinHandler(self.kwargs).fetch_one_video(aweme_id=aweme_id)
        Detail = video._to_raw()['aweme_detail']
        author_name = Detail['author']['nickname']
        author_age = Detail['author']['user_age']
        author_avatar = Detail['author']['avatar_thumb']['url_list'][0]
        author_id = Detail['author']['sec_uid']
        author_signature = Detail['author']['signature']
        author_fans = Detail['author']['follower_count']
        author_total_favorited = Detail['author']['total_favorited']
        description = Detail['desc']
        description_title = Detail['item_title']
        caption = Detail['caption']
        duration = Detail['duration']
        music_author = Detail['music']['author']
        music_avatar = Detail['music']['cover_thumb']['url_list'][0]
        music_url = Detail['music']['play_url']['uri']
        update_time = Detail['create_time']
        if video_type == "video":
            video_url = [Detail['video']['bit_rate'][4]['play_addr']['url_list'][2]]
            video_cover = Detail['video']['cover']['url_list'][0]
            video_dynamic_cover = Detail['video']['dynamic_cover']['url_list'][0]
        elif video_type == "slides":
            try:
                video_url = [i['video']['play_addr']['url_list'][2] for i in Detail['images']]
                video_cover = Detail['video']['cover']['url_list'][0]
                video_dynamic_cover = ""
            except KeyError:
                video_url = [i['url_list'][0] for i in Detail['images']]
                video_cover = Detail['video']['cover']['url_list'][0]
                video_dynamic_cover = ""
        elif video_type == "note":
            try:
                video_url = [i['video']['play_addr']['url_list'][2] for i in Detail['images']]
                video_cover = Detail['video']['cover']['url_list'][0]
                video_dynamic_cover = ""
            except KeyError as e:
                video_url = [i['url_list'][0] for i in Detail['images']]
                video_cover = Detail['video']['cover']['url_list'][0]
                video_dynamic_cover = ""
        video_heart = Detail['statistics']['digg_count']
        video_comment = Detail['statistics']['comment_count']
        video_share = Detail['statistics']['share_count']
        video_collect = Detail['statistics']['collect_count']

        single_video_info = {
            "base_url": self.url,
            "aweme_id": aweme_id,
            "author_name": author_name,
            "author_avatar": author_avatar,
            "author_id": author_id,
            "author_signature": author_signature,
            "author_fans": author_fans,
            "author_total_favorited": author_total_favorited,
            "description": description,
            "duration": duration,
            "music_author": music_author,
            "music_avatar": music_avatar,
            "music_url": music_url,
            "video_url": video_url,
            "video_cover": video_cover,
            "video_dynamic_cover": video_dynamic_cover,
            "video_heart": video_heart,
            "video_comment": video_comment,
            "video_share": video_share,
            "video_collect": video_collect,
            "update_time": update_time,
            "author_age": author_age,
            "description_title": description_title,
            "caption": caption,
            "video_type": video_type,
            "video_name": f"{author_name}_{aweme_id}"
        }

        return single_video_info
