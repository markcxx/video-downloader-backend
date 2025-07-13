# 抖音视频下载器 API 文档

## 概述

本API提供抖音视频信息获取和多质量下载功能，支持获取视频的详细信息包括多种分辨率选项。

## 基础信息

- **基础URL**: `https://videoflow.markingchen.cn/api`
- **请求方式**: POST
- **内容类型**: application/json
- **编码**: UTF-8

## API 接口

### 1. 获取视频信息

#### 接口地址
```
POST /video/info
```

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| video_url | string | 是 | 抖音视频分享链接 |

#### 请求示例

```json
{
    "video_url": "https://v.douyin.com/6KnqjH0WRfY/"
}
```

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | int | 状态码，200表示成功 |
| message | string | 响应消息 |
| data | object | 视频信息数据 |

#### data 字段说明

| 参数名 | 类型 | 说明 |
|--------|------|------|
| base_url | string | 原始分享链接 |
| aweme_id | string | 视频唯一ID |
| author_name | string | 作者昵称 |
| author_avatar | string | 作者头像URL |
| author_id | string | 作者ID |
| author_signature | string | 作者签名 |
| author_fans | int | 作者粉丝数 |
| author_total_favorited | int | 作者获赞总数 |
| description | string | 视频描述 |
| description_title | string | 视频标题 |
| caption | string | 视频字幕 |
| duration | int | 视频时长（毫秒） |
| music_author | string | 背景音乐作者 |
| music_avatar | string | 音乐封面URL |
| music_url | string | 音乐播放地址 |
| video_url | array | 默认视频播放地址（最高质量） |
| **video_quality_options** | array | **视频质量选项列表** |
| video_cover | string | 视频封面URL |
| video_dynamic_cover | string | 视频动态封面URL |
| video_heart | int | 点赞数 |
| video_comment | int | 评论数 |
| video_share | int | 分享数 |
| video_collect | int | 收藏数 |
| update_time | int | 发布时间戳 |
| author_age | int | 作者年龄 |
| video_type | string | 视频类型（video/slides/note） |
| video_name | string | 视频文件名 |

#### video_quality_options 字段详解

每个质量选项包含以下字段：

| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| quality_index | int | 质量选项索引 | 0 |
| resolution | string | 分辨率 | "1080p", "720p", "540p" |
| bitrate | string | 码率 | "1.36 Mbps" |
| size | string | 文件大小 | "5.09 MB" |
| encoding | string | 编码格式 | "H.264编码", "H.265编码" |
| url | string | 视频播放地址 | "https://..." |
| gear_name | string | 质量等级名称 | "normal_1080_0" |
| format | string | 视频格式 | "mp4" |
| fps | int | 帧率 | 30 |

#### 响应示例

```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "base_url": "https://v.douyin.com/6KnqjH0WRfY/",
        "aweme_id": "7523941361876651302",
        "author_name": "用户昵称",
        "author_avatar": "https://...",
        "author_id": "MS4wLjABAAAA...",
        "author_signature": "用户签名",
        "author_fans": 12345,
        "author_total_favorited": 67890,
        "description": "视频描述内容",
        "description_title": "视频标题",
        "caption": "视频字幕",
        "duration": 31280,
        "music_author": "音乐作者",
        "music_avatar": "https://...",
        "music_url": "https://...",
        "video_url": ["https://..."],
        "video_quality_options": [
            {
                "quality_index": 0,
                "resolution": "1080p",
                "bitrate": "1.36 Mbps",
                "size": "5.09 MB",
                "encoding": "H.264编码",
                "url": "https://v3-weba.douyinvod.com/...",
                "gear_name": "normal_1080_0",
                "format": "mp4",
                "fps": 30
            },
            {
                "quality_index": 1,
                "resolution": "720p",
                "bitrate": "0.91 Mbps",
                "size": "3.43 MB",
                "encoding": "H.264编码",
                "url": "https://v3-weba.douyinvod.com/...",
                "gear_name": "normal_720_0",
                "format": "mp4",
                "fps": 30
            },
            {
                "quality_index": 2,
                "resolution": "540p",
                "bitrate": "0.64 Mbps",
                "size": "2.41 MB",
                "encoding": "H.265编码",
                "url": "https://v3-weba.douyinvod.com/...",
                "gear_name": "540_2_1",
                "format": "mp4",
                "fps": 30
            }
        ],
        "video_cover": "https://...",
        "video_dynamic_cover": "https://...",
        "video_heart": 690294,
        "video_comment": 19917,
        "video_share": 83577,
        "video_collect": 54308,
        "update_time": 1751804115,
        "author_age": 25,
        "video_type": "video",
        "video_name": "用户昵称_7523941361876651302"
    }
}
```

## 前端使用示例

### JavaScript (Fetch API)

```javascript
// 获取视频信息
async function getVideoInfo(videoUrl) {
    try {
        const response = await fetch('/api/video/info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                video_url: videoUrl
            })
        });
        
        const result = await response.json();
        
        if (result.code === 200) {
            const videoData = result.data;
            
            // 显示视频基本信息
            console.log('视频标题:', videoData.description_title);
            console.log('作者:', videoData.author_name);
            console.log('时长:', Math.round(videoData.duration / 1000) + '秒');
            
            // 处理视频质量选项
            const qualityOptions = videoData.video_quality_options;
            qualityOptions.forEach((option, index) => {
                console.log(`质量选项 ${index + 1}:`);
                console.log(`  分辨率: ${option.resolution}`);
                console.log(`  码率: ${option.bitrate}`);
                console.log(`  大小: ${option.size}`);
                console.log(`  编码: ${option.encoding}`);
                console.log(`  下载地址: ${option.url}`);
            });
            
            return videoData;
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        console.error('获取视频信息失败:', error);
        throw error;
    }
}

// 使用示例
getVideoInfo('https://v.douyin.com/6KnqjH0WRfY/')
    .then(data => {
        // 处理成功获取的数据
        displayVideoInfo(data);
    })
    .catch(error => {
        // 处理错误
        alert('获取视频信息失败: ' + error.message);
    });
```

### Vue.js 示例

```vue
<template>
  <div class="video-downloader">
    <div class="input-section">
      <input 
        v-model="videoUrl" 
        placeholder="请输入抖音视频链接"
        class="url-input"
      />
      <button @click="fetchVideoInfo" :disabled="loading">获取视频信息</button>
    </div>
    
    <div v-if="videoData" class="video-info">
      <h3>{{ videoData.description_title }}</h3>
      <p>作者: {{ videoData.author_name }}</p>
      <p>时长: {{ Math.round(videoData.duration / 1000) }}秒</p>
      
      <div class="quality-options">
        <h4>下载选项:</h4>
        <div 
          v-for="option in videoData.video_quality_options" 
          :key="option.quality_index"
          class="quality-option"
        >
          <div class="option-info">
            <span class="resolution">{{ option.resolution }}</span>
            <span class="bitrate">{{ option.bitrate }}</span>
            <span class="size">{{ option.size }}</span>
            <span class="encoding">{{ option.encoding }}</span>
          </div>
          <button @click="downloadVideo(option.url, option.resolution)">
            下载
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      videoUrl: '',
      videoData: null,
      loading: false
    }
  },
  methods: {
    async fetchVideoInfo() {
      if (!this.videoUrl.trim()) {
        alert('请输入视频链接');
        return;
      }
      
      this.loading = true;
      try {
        const response = await fetch('/api/video/info', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            video_url: this.videoUrl
          })
        });
        
        const result = await response.json();
        
        if (result.code === 200) {
          this.videoData = result.data;
        } else {
          throw new Error(result.message);
        }
      } catch (error) {
        alert('获取视频信息失败: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    
    downloadVideo(url, resolution) {
      // 创建下载链接
      const link = document.createElement('a');
      link.href = url;
      link.download = `${this.videoData.video_name}_${resolution}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }
}
</script>
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 视频不存在或已删除 |
| 500 | 服务器内部错误 |

## 注意事项

1. **视频质量选项排序**: 质量选项按照质量从高到低排序，索引0为最高质量
2. **编码兼容性**: H.265编码文件更小但兼容性较差，H.264编码兼容性更好
3. **链接有效期**: 视频下载链接有时效性，建议获取后立即使用
4. **请求频率**: 建议控制请求频率，避免被限制访问
5. **错误处理**: 请妥善处理网络错误和API错误响应

## 更新日志

### v2.0.0 (2025-01-13)
- 新增 `video_quality_options` 字段，提供多种视频质量选项
- 每个质量选项包含分辨率、码率、文件大小、编码格式等详细信息
- 支持H.264和H.265两种编码格式
- 优化视频URL获取逻辑

### v1.0.0
- 基础视频信息获取功能
- 支持视频、图集、笔记三种类型内容