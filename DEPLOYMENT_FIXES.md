# Vercel 部署修复说明

## 问题诊断

原始代码在 Vercel 部署时出现错误，主要原因包括：

1. **缺少 f2 依赖**: `requirements.txt` 中没有包含 `f2` 库，但代码中使用了 `from f2.apps.douyin.handler import DouyinHandler`
2. **Vercel 配置不完整**: `vercel.json` 配置不适合 FastAPI 应用
3. **文件结构不符合 Vercel 要求**: 缺少适合 Vercel 的 API 文件结构

## 修复内容

### 1. 更新依赖文件
- 在 `requirements.txt` 中添加了 `f2` 库

### 2. 创建 Vercel 兼容的 API 结构
- 创建了 `api/index.py` 文件，包含完整的 FastAPI 应用
- 添加了正确的 ASGI 应用入口点 (`handler = app`)

### 3. 更新 Vercel 配置
- 更新 `vercel.json` 指向 `api/index.py`
- 添加了 `version: 2` 和环境变量配置
- 设置了 `PYTHONPATH` 环境变量

### 4. 添加部署优化文件
- 创建 `.vercelignore` 文件排除不必要的文件
- 添加了测试脚本用于本地验证

## 文件变更列表

### 新增文件
- `api/index.py` - Vercel 兼容的 FastAPI 应用入口
- `.vercelignore` - 部署时忽略的文件列表
- `test_deployment.py` - 本地测试脚本
- `DEPLOYMENT_FIXES.md` - 本说明文件

### 修改文件
- `requirements.txt` - 添加 f2 依赖
- `vercel.json` - 更新配置指向新的 API 文件
- `main.py` - 添加 handler 变量（保持向后兼容）

## 部署说明

1. 确保所有文件都已提交到 GitHub 仓库
2. 在 Vercel 中重新部署项目
3. 部署成功后，API 将在以下端点可用：
   - `GET /` - 根路径，返回服务状态
   - `POST /api/parse_video` - 解析抖音视频链接
   - `GET /api/health` - 健康检查

## 注意事项

- f2 库可能需要特定的网络环境才能正常工作
- 如果仍然遇到部署问题，请检查 Vercel 的构建日志
- 确保所有依赖都在 `requirements.txt` 中正确列出