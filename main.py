# coding:utf-8
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sys
import os

# 添加当前目录到Python路径
# sys.path.append(os.path.dirname(__file__))

from singleVideoCrawler import Single_Video_Crawler

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
    
class VideoResponse(BaseModel):
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
    video_url: List[str]
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

@app.get("/")
async def root():
    return {"message": "抖音视频爬虫API服务正在运行", "status": "success"}

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
            raise HTTPException(status_code=400, detail="无法解析视频链接，请检查链接是否正确")
        
        # 获取视频详细信息
        video_info = await crawler.get_video_info(video_id, video_type)
        
        return VideoResponse(**video_info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析视频时发生错误: {str(e)}")

@app.get("/api/health")
async def health_check():
    """
    健康检查接口
    """
    return {"status": "healthy", "message": "服务运行正常"}

# Vercel需要的ASGI应用入口点
# handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)