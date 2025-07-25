# coding:utf-8
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
import sys
import os

# 添加当前目录到Python路径
# sys.path.append(os.path.dirname(__file__))

from singleVideoCrawler import Single_Video_Crawler
from bilibili_crawler import BilibiliCrawler

app = FastAPI(
    title="抖音视频爬虫API",
    description="用于解析抖音分享链接并获取视频信息的API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

class BilibiliRequest(BaseModel):
    url: str
    
class VideoQualityOption(BaseModel):
    quality_index: int
    resolution: str
    bitrate: str
    size: str
    encoding: str
    url: str
    gear_name: str
    format: str
    fps: int

class VideoData(BaseModel):
    base_url: str
    aweme_id: str
    author_name: str
    author_avatar: str
    author_id: str
    author_signature: str
    author_fans: int
    author_total_favorited: int
    description: str
    duration: int
    music_author: str
    music_avatar: str
    music_url: str
    video_quality_options: List[VideoQualityOption]  # 视频质量选项（包含URL）
    video_cover: str
    video_dynamic_cover: str
    video_heart: int
    video_comment: int
    video_share: int
    video_collect: int
    update_time: int
    author_age: int
    description_title: str
    caption: str
    video_type: str
    video_name: str

class BilibiliData(BaseModel):
    success: bool
    title: str
    desc: str
    cover: str
    duration: int
    pubdate: int
    aid: int
    bvid: str
    cid: int
    owner: dict
    stat: dict
    pages: List[dict]
    play_info: dict = None
    video_type: str
    original_url: str

class StandardResponse(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

class VideoResponse(StandardResponse):
    data: Optional[VideoData] = None

class BilibiliResponse(StandardResponse):
    data: Optional[BilibiliData] = None

@app.get("/")
async def root():
    return StandardResponse(
        code=200,
        message="抖音视频爬虫API服务正在运行",
        data={"status": "success"}
    )

@app.post("/api/parse_video", response_model=VideoResponse)
async def parse_video(request: VideoRequest):
    """
    解析抖音视频分享链接，返回视频详细信息
    
    Args:
        request: 包含视频分享链接的请求体
        
    Returns:
        VideoResponse: 视频的详细信息
        
    Raises:
        HTTPException: 当解析失败时抛出异常
    """
    try:
        # 创建爬虫实例
        crawler = Single_Video_Crawler(request.url)
        
        # 获取视频ID和类型
        video_id, video_type = crawler.get_video_id()
        
        if not video_id or not video_type:
            return VideoResponse(
                code=400,
                message="无法解析视频链接，请检查链接是否正确",
                data=None
            )
        
        # 获取视频详细信息
        video_info = await crawler.get_video_info(video_id, video_type)
        
        return VideoResponse(
            code=200,
            message="解析成功",
            data=VideoData(**video_info)
        )
        
    except Exception as e:
        return VideoResponse(
            code=500,
            message=f"解析视频时发生错误: {str(e)}",
            data=None
        )

@app.post("/api/parse_bilibili", response_model=BilibiliResponse)
async def parse_bilibili(request: BilibiliRequest):
    """
    解析B站视频链接，返回视频详细信息
    
    Args:
        request: 包含B站视频链接的请求体
        
    Returns:
        BilibiliResponse: 视频的详细信息
        
    Raises:
        HTTPException: 当解析失败时抛出异常
    """
    try:
        # 创建B站爬虫实例
        crawler = BilibiliCrawler()
        
        # 解析视频URL
        result = crawler.parse_url(request.url)
        
        if not result['success']:
            return BilibiliResponse(
                code=400,
                message=f"解析失败: {result['error']}",
                data=None
            )
        
        video_data = result['data']
        
        # 构造响应数据
        response_data = {
            "success": True,
            "title": video_data.get('title', ''),
            "desc": video_data.get('desc', ''),
            "cover": video_data.get('cover', ''),
            "duration": video_data.get('duration', 0),
            "pubdate": video_data.get('pubdate', 0),
            "aid": video_data.get('aid', 0),
            "bvid": video_data.get('bvid', ''),
            "cid": video_data.get('cid', 0),
            "owner": video_data.get('owner', {}),
            "stat": video_data.get('stat', {}),
            "pages": video_data.get('pages', []),
            "play_info": video_data.get('play_info'),
            "video_type": video_data.get('type', 'video'),
            "original_url": request.url
        }
        
        return BilibiliResponse(
            code=200,
            message="解析成功",
            data=BilibiliData(**response_data)
        )
        
    except Exception as e:
        return BilibiliResponse(
            code=500,
            message=f"解析视频时发生错误: {str(e)}",
            data=None
        )

@app.get("/api/health")
async def health_check():
    """
    健康检查接口
    """
    return StandardResponse(
        code=200,
        message="服务运行正常",
        data={"status": "healthy"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)