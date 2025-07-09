# coding:utf-8
import requests
import json
import asyncio

def test_backend_api():
    """
    测试Backend FastAPI接口
    """
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("抖音视频爬虫 Backend API 测试")
    print("=" * 60)
    
    # 测试根路径
    print("\n1. 测试根路径...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   ❌ 根路径测试失败: {e}")
        print("   请确保后端服务已启动")
        return
    
    # 测试健康检查
    print("\n2. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   ❌ 健康检查测试失败: {e}")
        return
    
    # 测试API文档
    print("\n3. 测试API文档访问...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print(f"   ✅ API文档可访问: {base_url}/docs")
        else:
            print(f"   ⚠️  API文档状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API文档访问失败: {e}")
    
    # 测试视频解析接口
    print("\n4. 测试视频解析接口...")
    test_url = input("   请输入抖音分享链接进行测试（或按回车跳过）: ").strip()
    
    if test_url:
        try:
            data = {"url": test_url}
            print(f"   正在解析: {test_url}")
            response = requests.post(f"{base_url}/api/parse_video", json=data, timeout=30)
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("   ✅ 解析成功！")
                print(f"   📹 视频标题: {result.get('description', 'N/A')}")
                print(f"   👤 作者: {result.get('author_name', 'N/A')}")
                print(f"   📱 视频类型: {result.get('video_type', 'N/A')}")
                print(f"   ❤️  点赞数: {result.get('video_heart', 'N/A')}")
                print(f"   💬 评论数: {result.get('video_comment', 'N/A')}")
                print(f"   🔗 视频链接数量: {len(result.get('video_url', []))}")
                print(f"   ⏱️  时长: {result.get('duration', 'N/A')}秒")
            else:
                print(f"   ❌ 解析失败: {response.text}")
                
        except requests.exceptions.Timeout:
            print("   ⏰ 请求超时，可能是网络问题或视频解析耗时较长")
        except Exception as e:
            print(f"   ❌ 视频解析测试失败: {e}")
    else:
        print("   ⏭️  跳过视频解析测试")
    
    print("\n=" * 60)
    print("测试完成！")
    print(f"API文档地址: {base_url}/docs")
    print(f"健康检查地址: {base_url}/api/health")
    print(f"视频解析接口: {base_url}/api/parse_video")
    print("=" * 60)

if __name__ == "__main__":
    print("请确保后端服务已启动:")
    print("cd backend && python main.py")
    print("或者运行: cd backend && start_backend.bat")
    print()
    
    input("按回车键开始测试...")
    test_backend_api()