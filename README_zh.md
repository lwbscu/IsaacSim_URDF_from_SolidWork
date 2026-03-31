# Isaac Sim URDF 资产清洗专家

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![Language](https://img.shields.io/badge/Language-English%20%7C%20%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-success)](#)

*选择语言: [English](readme.md), [简体中文](README_zh.md).*

一款轻量级、中英双语的 PyQt5 图形化工具，专为深度清洗和重构 URDF 机器人资产（尤其是 SolidWorks 导出的模型）而设计。它能确保你的机器人模型零报错、丝滑地导入 **NVIDIA Isaac Sim**，彻底告别由底层 USD 严苛规范和 ROS 绝对路径依赖引起的 `Null Prim` 崩溃问题。

## 核心特性

- **命名合规化清洗**: 自动扫描并批量替换物理文件、文件夹以及 URDF 内部属性（Link/Joint/Mesh）中包含的非法字符（中文、空格、连字符 `-`），严格满足 USD 规范。
- **依赖路径重构**: 自动剥离 ROS/ROS2 导出插件生成的 `package://` 绝对路径，并将其无损转化为支持跨设备解析的相对路径（如 `../meshes/xxx.STL`）。
- **关节拓扑分析器**: 深度解析 URDF 的 XML 树结构，分类统计关节类型（旋转、滑动、固定）。有效帮助开发者在导入前排查因配置失误被焊死的“Fixed”轮子或夹爪。
- **双语无缝切换**: 界面支持一键切换英文 / 简体中文。
- **开箱即用的启动器**: 内置的 `run.sh` 脚本可全自动进行依赖体检，交互式安装缺失的 `PyQt5` 库，并物理屏蔽 Linux 底层无害的 GUI 渲染警告，保持终端极度清爽。

## 快速开始

### 环境要求
- Ubuntu / Linux 系统 (或 WSL2)
- Python 3.x

### 安装与运行
克隆仓库并执行启动脚本即可：

```bash
git clone [https://github.com/YourUsername/IsaacSim-URDF-Cleaner.git](https://github.com/YourUsername/IsaacSim-URDF-Cleaner.git)
cd IsaacSim-URDF-Cleaner
chmod +x run.sh
./run.sh
```

（注：如果你的环境中缺失 PyQt5，脚本会优雅地询问并自动调用 pip 为你安装。）

## 使用指南

通过 ./run.sh 启动界面。
选择目标所在文件夹路径: 点击“浏览”选择资产的根目录。
选择原 URDF 路径: 点击“浏览”定位到原始的 .urdf 文件（工具具备智能推断能力，会自动帮你补全根目录）。
期望改名后的名称: 输入纯净的资产名（如 robot_v2，仅限纯英文与下划线，无需加后缀）。
点击 [2. 一键清洗重构 (Clean)]。
打开 NVIDIA Isaac Sim -> 点击菜单栏 File -> Import -> 选中新生成的 .urdf 文件即可完美导入！

## 作者

Liwenbo
