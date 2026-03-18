#!/bin/bash
# Search Is All You Need - 开发环境安装脚本

set -e

echo "=========================================="
echo "🚀 Search Is All You Need 开发环境安装"
echo "=========================================="
echo ""

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "📁 项目目录: $PROJECT_ROOT"
echo ""

# 步骤1: 检查Python版本
echo "🔍 检查Python版本..."
PYTHON_CMD=""
if command -v python3.8 &> /dev/null; then
    PYTHON_CMD="python3.8"
elif command -v python3.9 &> /dev/null; then
    PYTHON_CMD="python3.9"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ 未找到Python 3.8+，请先安装Python"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version | awk '{print $2}')
echo "✅ Python版本: $PYTHON_VERSION"
echo ""

# 步骤2: 创建虚拟环境
echo "📦 创建Python虚拟环境..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    echo "✅ 虚拟环境已创建"
else
    echo "ℹ️  虚拟环境已存在，跳过创建"
fi
echo ""

# 步骤3: 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate
echo "✅ 虚拟环境已激活"
echo ""

# 步骤4: 升级pip
echo "⬆️  升级pip..."
pip install --upgrade pip
echo ""

# 步骤5: 安装依赖
echo "📦 安装Python依赖..."
pip install -r backend/requirements.txt
echo ""

# 步骤6: 配置环境变量
echo "⚙️  配置环境变量..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env文件已创建，请编辑配置API密钥"
else
    echo "ℹ️  .env文件已存在，跳过创建"
fi
echo ""

# 步骤7: 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data/downloads
echo "✅ 数据目录已创建"
echo ""

# 步骤8: 检查Node.js（可选，用于前端开发）
echo "🔍 检查Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js版本: $NODE_VERSION"
    
    # 检查是否需要安装前端依赖
    if [ ! -d "frontend/node_modules" ]; then
        echo ""
        echo "📦 安装前端依赖..."
        cd frontend && npm install && cd ..
        echo "✅ 前端依赖已安装"
    fi
else
    echo "ℹ️  未找到Node.js，跳过前端安装（仅后端API可用）"
    echo "   如需前端开发，请安装Node.js 18+"
fi
echo ""

# 完成
echo "=========================================="
echo "🎉 开发环境安装完成！"
echo "=========================================="
echo ""
echo "📝 下一步操作："
echo "1. 编辑 .env 文件，配置你的API密钥"
echo "2. 激活虚拟环境: source venv/bin/activate"
echo "3. 启动后端: python backend/app.py"
echo ""
echo "🌐 访问地址："
echo "   - 后端API: http://localhost:5000"
echo "   - 前端开发: http://localhost:5173 (如果安装了前端)"
echo ""
echo "🔧 快速启动（一键）："
echo "   bash run.sh"
echo ""
