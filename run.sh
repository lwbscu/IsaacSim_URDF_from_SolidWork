#!/bin/bash

# 获取脚本所在的当前绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "====================================================="
echo "  Isaac Sim URDF Cleaner - Dependency Check / 依赖检测"

# 定义需要检测的外部库
REQUIRED_PKG="PyQt5"

# 尝试在静默模式下导入该库，判断是否已安装
if python3 -c "import PyQt5" &> /dev/null; then
    echo "[OK] 核心依赖 '$REQUIRED_PKG' 已就绪。"
else
    echo "[Warning] 未检测到必须的图形界面库: $REQUIRED_PKG"
    echo "This tool requires PyQt5 to run the GUI."
    
    # 交互式提问：是否允许安装
    read -p "是否立即使用 pip 自动下载并安装 $REQUIRED_PKG ? (Y/n) [默认: Y]: " choice
    
    # 如果用户直接敲回车，默认视为 'Y'
    choice=${choice:-Y} 

    if [[ "$choice" =~ ^[Yy]$ ]]; then
        echo "正在为您下载并安装 $REQUIRED_PKG，请稍候..."
        # 使用 python3 -m pip 确保安装到当前运行环境，避免多环境冲突
        python3 -m pip install $REQUIRED_PKG
        
        # 检查上一条 pip install 命令是否成功执行
        if [ $? -ne 0 ]; then
            echo "[Error] 安装失败！请检查您的网络，或尝试手动运行: pip install PyQt5"
            exit 1
        fi
        echo "[Success] $REQUIRED_PKG 安装成功！"
    else
        echo "[Abort] 已取消安装。由于缺少依赖，工具无法启动。"
        exit 1
    fi
fi

echo "启动工具 / Starting Tool..."
echo "====================================================="
# 启动 GUI 工具，并使用 2>/dev/null 将底层图形库的报错和警告全部丢弃
python3 "$SCRIPT_DIR/urdf_toolkit.py" 2>/dev/null