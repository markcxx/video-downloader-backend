#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试部署脚本
用于验证所有依赖是否正确安装
"""

def test_imports():
    """测试所有必要的导入"""
    try:
        import fastapi
        print("✓ FastAPI 导入成功")
        
        import uvicorn
        print("✓ Uvicorn 导入成功")
        
        import pydantic
        print("✓ Pydantic 导入成功")
        
        import requests
        print("✓ Requests 导入成功")
        
        try:
            from f2.apps.douyin.handler import DouyinHandler
            print("✓ F2 库导入成功")
        except ImportError as e:
            print(f"✗ F2 库导入失败: {e}")
            return False
            
        from apiproxy.common import utils
        print("✓ 本地工具模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    try:
        from singleVideoCrawler import Single_Video_Crawler
        print("✓ 爬虫模块导入成功")
        
        # 测试实例化
        test_url = "https://v.douyin.com/test"
        crawler = Single_Video_Crawler(test_url)
        print("✓ 爬虫实例创建成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始部署测试...")
    print("=" * 50)
    
    import_success = test_imports()
    print("=" * 50)
    
    if import_success:
        functionality_success = test_basic_functionality()
        print("=" * 50)
        
        if functionality_success:
            print("✓ 所有测试通过！部署应该可以正常工作。")
        else:
            print("✗ 功能测试失败，请检查代码逻辑。")
    else:
        print("✗ 导入测试失败，请检查依赖安装。")