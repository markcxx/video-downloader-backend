# coding:utf-8
# B站视频解析器
# 基于BiliTools项目的实现原理

import re
import json
import time
import hashlib
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, parse_qs


class BilibiliCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com/',
            'Origin': 'https://www.bilibili.com',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }
        self.session.headers.update(self.headers)
        self._init_cookies()
    
    def _init_cookies(self):
        """初始化必要的cookies"""
        try:
            # 获取基础cookies
            resp = self.session.get('https://www.bilibili.com')
            
            # 获取buvid
            buvid_resp = self.session.get('https://api.bilibili.com/x/frontend/finger/spi')
            if buvid_resp.status_code == 200:
                buvid_data = buvid_resp.json()
                if buvid_data.get('code') == 0:
                    data = buvid_data.get('data', {})
                    self.session.cookies.set('buvid3', data.get('b_3', ''))
                    self.session.cookies.set('buvid4', data.get('b_4', ''))
        except Exception as e:
            print(f"初始化cookies失败: {e}")
    
    def extract_video_id(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """从URL中提取视频ID"""
        try:
            # 处理短链接
            if 'b23.tv' in url or 'bili2233.cn' in url:
                resp = self.session.get(url, allow_redirects=True)
                url = resp.url
            
            # 提取BV号或AV号
            bv_match = re.search(r'BV([a-zA-Z0-9]+)', url)
            if bv_match:
                return f"BV{bv_match.group(1)}", 'bvid'
            
            av_match = re.search(r'av(\d+)', url)
            if av_match:
                return av_match.group(1), 'aid'
            
            # 提取番剧ID
            ss_match = re.search(r'ss(\d+)', url)
            if ss_match:
                return ss_match.group(1), 'ss'
            
            ep_match = re.search(r'ep(\d+)', url)
            if ep_match:
                return ep_match.group(1), 'ep'
            
            return None, None
        except Exception as e:
            print(f"提取视频ID失败: {e}")
            return None, None
    
    def get_video_info(self, video_id: str, id_type: str) -> Dict[str, Any]:
        """获取视频基本信息"""
        try:
            if id_type in ['bvid', 'aid']:
                # 普通视频
                url = 'https://api.bilibili.com/x/web-interface/view'
                params = {id_type: video_id}
            elif id_type in ['ss', 'ep']:
                # 番剧
                url = 'https://api.bilibili.com/pgc/view/web/season'
                params = {'season_id' if id_type == 'ss' else 'ep_id': video_id}
            else:
                raise ValueError(f"不支持的ID类型: {id_type}")
            
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            
            data = resp.json()
            if data.get('code') != 0:
                raise Exception(f"API返回错误: {data.get('message', '未知错误')}")
            
            return self._parse_video_info(data['data'], id_type)
        
        except Exception as e:
            raise Exception(f"获取视频信息失败: {e}")
    
    def _parse_video_info(self, data: Dict[str, Any], id_type: str) -> Dict[str, Any]:
        """
        解析视频信息
        
        返回数据字段说明：
        - title: 视频标题
        - desc: 视频描述/简介
        - cover: 视频封面图片URL
        - duration: 视频时长（秒）
        - pubdate: 发布时间（Unix时间戳）
        - aid: 视频AV号（数字ID）
        - bvid: 视频BV号（字符串ID，推荐使用）
        - cid: 视频CID（分P标识，用于获取播放链接）
        - owner: 作者信息（name: UP主昵称, mid: UP主ID, face: 头像URL）
        - stat: 统计数据（view: 播放量, like: 点赞数, coin: 投币数等）
        - pages: 分P信息列表（多P视频会有多个元素）
        - type: 视频类型（video: 普通视频, bangumi: 番剧）
        """
        if id_type in ['bvid', 'aid']:
            # 普通视频
            return {
                'title': data.get('title', ''),                    # 视频标题
                'desc': data.get('desc', ''),                      # 视频描述
                'cover': data.get('pic', ''),                      # 封面图片URL
                'duration': data.get('duration', 0),               # 视频时长（秒）
                'pubdate': data.get('pubdate', 0),                 # 发布时间戳
                'aid': data.get('aid', 0),                         # AV号
                'bvid': data.get('bvid', ''),                      # BV号
                'cid': data.get('cid', 0),                         # 分P标识
                'owner': {                                          # 作者信息
                    'name': data.get('owner', {}).get('name', ''),     # UP主昵称
                    'mid': data.get('owner', {}).get('mid', 0),        # UP主ID
                    'face': data.get('owner', {}).get('face', '')      # UP主头像
                },
                'stat': {                                           # 统计数据
                    'view': data.get('stat', {}).get('view', 0),       # 播放量
                    'danmaku': data.get('stat', {}).get('danmaku', 0), # 弹幕数
                    'reply': data.get('stat', {}).get('reply', 0),     # 评论数
                    'like': data.get('stat', {}).get('like', 0),       # 点赞数
                    'coin': data.get('stat', {}).get('coin', 0),       # 投币数
                    'favorite': data.get('stat', {}).get('favorite', 0), # 收藏数
                    'share': data.get('stat', {}).get('share', 0)      # 分享数
                },
                'pages': data.get('pages', []),                    # 分P信息
                'type': 'video'                                    # 视频类型
            }
        else:
            # 番剧
            return {
                'title': data.get('season_title', ''),
                'desc': data.get('evaluate', ''),
                'cover': data.get('cover', ''),
                'season_id': data.get('season_id', 0),
                'episodes': data.get('episodes', []),
                'stat': {
                    'view': data.get('stat', {}).get('views', 0),
                    'danmaku': data.get('stat', {}).get('danmakus', 0),
                    'reply': data.get('stat', {}).get('reply', 0),
                    'like': data.get('stat', {}).get('likes', 0),
                    'coin': data.get('stat', {}).get('coins', 0),
                    'favorite': data.get('stat', {}).get('favorite', 0),
                    'share': data.get('stat', {}).get('share', 0)
                },
                'type': 'bangumi'
            }
    
    def get_play_url(self, aid: int, cid: int, qn: int = 64) -> Dict[str, Any]:
        """
        获取播放链接
        
        参数说明：
        - aid: 视频AV号
        - cid: 分P标识
        - qn: 清晰度 (16=360P, 32=480P, 64=720P, 80=1080P, 120=4K)
        
        返回数据说明：
        - quality: 当前清晰度
        - format: 视频格式
        - accept_quality: 可用清晰度列表
        - accept_format: 可用格式列表
        - videos: 视频文件信息列表
          - url: 视频下载直链（重要！）
          - backup_url: 备用下载链接
          - size: 文件大小（字节）
          - length: 时长（毫秒）
        - dash: DASH格式信息（高清视频音画分离）
        """
        try:
            url = 'https://api.bilibili.com/x/player/playurl'
            params = {
                'avid': aid,
                'cid': cid,
                'qn': qn,  # 清晰度
                'fnver': 0,
                'fnval': 16,  # 返回格式
                'fourk': 1
            }
            
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            
            data = resp.json()
            if data.get('code') != 0:
                raise Exception(f"获取播放链接失败: {data.get('message', '未知错误')}")
            
            result = data['data']
            
            # 解析播放链接
            play_info = {
                'quality': result.get('quality', qn),              # 当前清晰度
                'format': result.get('format', ''),               # 视频格式
                'accept_quality': result.get('accept_quality', []), # 可用清晰度列表
                'accept_format': result.get('accept_format', ''),  # 可用格式列表
                'videos': []                                       # 视频文件列表
            }
            
            # 处理durl格式（MP4/FLV - 音视频合并格式）
            if 'durl' in result:
                for item in result['durl']:
                    play_info['videos'].append({
                        'url': item.get('url', ''),               # 视频下载直链（最重要）
                        'backup_url': item.get('backup_url', []), # 备用下载链接
                        'size': item.get('size', 0),              # 文件大小（字节）
                        'length': item.get('length', 0)           # 时长（毫秒）
                    })
            
            # 处理dash格式（音视频分离格式，高清视频常用）
            elif 'dash' in result:
                dash = result['dash']
                play_info['dash'] = {
                    'video': dash.get('video', []),  # 视频流列表（无音频）
                    'audio': dash.get('audio', [])   # 音频流列表（需要合并）
                }
            
            return play_info
        
        except Exception as e:
            raise Exception(f"获取播放链接失败: {e}")
    
    def parse_url(self, url: str) -> Dict[str, Any]:
        """解析B站URL，返回完整信息"""
        try:
            # 提取视频ID
            video_id, id_type = self.extract_video_id(url)
            if not video_id or not id_type:
                raise Exception("无法从URL中提取有效的视频ID")
            
            # 获取视频信息
            video_info = self.get_video_info(video_id, id_type)
            
            # 如果是普通视频，获取播放链接
            if video_info['type'] == 'video':
                try:
                    play_info = self.get_play_url(
                        video_info['aid'], 
                        video_info['cid']
                    )
                    video_info['play_info'] = play_info
                except Exception as e:
                    print(f"获取播放链接失败: {e}")
                    video_info['play_info'] = None
            
            return {
                'success': True,
                'data': video_info,
                'original_url': url
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'original_url': url
            }


if __name__ == "__main__":
    # 测试代码
    crawler = BilibiliCrawler()
    
    # 测试URL
    test_urls = [
        "https://www.bilibili.com/video/BV1SM3UzhEhj/?spm_id_from=333.1007.tianma.6-3-21.clic",
        "https://b23.tv/BV1xx411c7mD"
    ]
    
    for url in test_urls:
        print(f"\n测试URL: {url}")
        result = crawler.parse_url(url)
        print(json.dumps(result, indent=2, ensure_ascii=False))