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

    def _parse_video_quality_options(self, bit_rates):
        """解析视频质量选项"""
        quality_options = []
        
        for i, bitrate_info in enumerate(bit_rates):
            # 获取分辨率
            width = bitrate_info.get('play_addr', {}).get('width', 0)
            height = bitrate_info.get('play_addr', {}).get('height', 0)
            
            # 判断分辨率等级
            if height >= 1080:
                resolution = "1080p"
            elif height >= 720:
                resolution = "720p"
            elif height >= 540:
                resolution = "540p"
            else:
                resolution = f"{height}p"
            
            # 获取码率（转换为Mbps）
            bit_rate = bitrate_info.get('bit_rate', 0)
            bitrate_mbps = round(bit_rate / 1000000, 2) if bit_rate > 0 else 0
            
            # 获取文件大小（转换为MB）
            data_size = bitrate_info.get('play_addr', {}).get('data_size', 0)
            size_mb = round(data_size / (1024 * 1024), 2) if data_size > 0 else 0
            
            # 判断编码格式
            is_h265 = bitrate_info.get('is_h265', 0) == 1
            is_bytevc1 = bitrate_info.get('is_bytevc1', 0) == 1
            
            if is_h265 or is_bytevc1:
                encoding = "H.265编码"
            else:
                encoding = "H.264编码"
            
            # 获取播放地址
            url_list = bitrate_info.get('play_addr', {}).get('url_list', [])
            video_url = url_list[2] if len(url_list) > 2 else (url_list[0] if url_list else "")
            
            quality_option = {
                "quality_index": i,
                "resolution": resolution,
                "bitrate": f"{bitrate_mbps} Mbps",
                "size": f"{size_mb} MB",
                "encoding": encoding,
                "url": video_url,
                "gear_name": bitrate_info.get('gear_name', ''),
                "format": bitrate_info.get('format', 'mp4'),
                "fps": bitrate_info.get('FPS', 30)
            }
            
            quality_options.append(quality_option)
        
        return quality_options

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
        
        # 处理视频质量选项和封面
        video_quality_options = []
        if video_type == "video":
            # 解析所有质量选项
            bit_rates = Detail['video']['bit_rate']
            video_quality_options = self._parse_video_quality_options(bit_rates)
            video_cover = Detail['video']['cover']['url_list'][0]
            video_dynamic_cover = Detail['video']['dynamic_cover']['url_list'][0]
        elif video_type == "slides":
            # 对于图集类型，创建图片URL列表作为质量选项
            try:
                image_urls = [i['video']['play_addr']['url_list'][2] for i in Detail['images']]
            except KeyError:
                image_urls = [i['url_list'][0] for i in Detail['images']]
            
            # 为图集创建质量选项
            for i, url in enumerate(image_urls):
                video_quality_options.append({
                    "quality_index": i,
                    "resolution": "原图",
                    "bitrate": "N/A",
                    "size": "N/A",
                    "encoding": "图片",
                    "url": url,
                    "gear_name": f"image_{i}",
                    "format": "jpg",
                    "fps": 0
                })
            video_cover = Detail['video']['cover']['url_list'][0]
            video_dynamic_cover = ""
        elif video_type == "note":
            # 对于笔记类型，创建图片URL列表作为质量选项
            try:
                image_urls = [i['video']['play_addr']['url_list'][2] for i in Detail['images']]
            except KeyError as e:
                image_urls = [i['url_list'][0] for i in Detail['images']]
            
            # 为笔记创建质量选项
            for i, url in enumerate(image_urls):
                video_quality_options.append({
                    "quality_index": i,
                    "resolution": "原图",
                    "bitrate": "N/A",
                    "size": "N/A",
                    "encoding": "图片",
                    "url": url,
                    "gear_name": f"note_{i}",
                    "format": "jpg",
                    "fps": 0
                })
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
            "video_quality_options": video_quality_options,  # 视频质量选项（包含URL）
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
