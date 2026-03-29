# Yolo数据集辅助标注

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.4+-green.svg)](https://pypi.org/project/PySide6/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-orange.svg)](https://opencv.org/)
[![YOLO](https://img.shields.io/badge/YOLO-v8+-red.svg)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基于 Python + PySide6 的 YOLO 格式数据集标注工具，具备 LabelImg 的所有核心功能，并集成了传统图形学辅助标注和 YOLO 深度学习智能识别功能，大幅提升标注效率。

[功能特性](#功能特性) • [安装](#安装) • [使用](#使用) • [YOLO智能识别](#yolo智能识别)

---

## 功能特性

### 核心标注功能

| 功能 | 说明 |
|------|------|
| 文件操作 | 打开图片文件夹，支持 JPG、PNG、BMP、JPEG 格式 |
| 图片导航 | 上一张(A)/下一张(D)快速切换 |
| 矩形标注 | 创建、编辑、移动、调整大小 |
| 标注管理 | 删除选中标注框 |
| 撤销重做 | 支持 Ctrl+Z / Ctrl+Shift+Z |
| 文件列表 | 右侧面板显示所有图片，点击切换 |
| 属性面板 | 显示选中标注的类别、宽度、高度信息 |

### 类别管理

- 类别列表显示与管理
- 添加/删除/修改类别
- 快捷键快速切换类别（1-9）
- 类别颜色自动区分
- 从 classes.txt 加载类别

### 辅助标注功能

| 模式 | 算法 | 用途 |
|------|------|------|
| 边缘检测 | Canny | 识别物体轮廓边界 |
| 颜色分割 | K-Means | 基于颜色聚类分割物体 |
| 显著性检测 | 显著性分析 | 定位图像中的显著区域 |
| MSER提取 | MSER | 提取最大稳定极值区域 |
| Otsu二值化 | Otsu | 自动阈值分割 |
| GrabCut前景 | GrabCut | 前景背景分割 |
| YOLO智能识别 | YOLOv8 | 深度学习目标检测自动标注 |

### 配置管理

- 保存当前辅助标注参数为配置文件
- 加载已有配置文件快速应用参数
- 支持 YAML 格式配置持久化

### 显示与导航

- 图片缩放（滚轮/按钮）
- 适应窗口 / 原始大小切换
- 显示/隐藏标注框和标签
- 十字准星辅助定位

---

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `W` | 创建矩形框 |
| `D` | 下一张图片 |
| `A` | 上一张图片 |
| `Delete` | 删除选中标注 |
| `Ctrl+S` | 保存标注 |
| `Ctrl+Z` | 撤销 |
| `Ctrl+Shift+Z` | 重做 |
| `1-9` | 快速切换类别 |

---

## 安装

### 环境要求

- Python >= 3.8
- Windows / Linux / macOS

### 快速开始

```bash
# 克隆仓库
git clone https://github.com/pattianfang/yolo-annotator.git
cd yolo-annotator

# 创建虚拟环境（推荐）
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### 安装依赖

```bash
pip install -r requirements.txt
```

---

## 使用

### 启动程序

```bash
python main.py
```

### 基本流程

1. **打开图片**：点击工具栏"打开"按钮，选择图片文件或文件夹
2. **创建标注**：按 `W` 键或点击"创建矩形框"，在画布上拖拽绘制
3. **选择类别**：在类别列表中选择当前标注的类别
4. **保存标注**：按 `Ctrl+S` 保存，标注文件将保存为同名的 `.txt` 文件

### 使用辅助标注

1. 在左侧面板选择检测模式（边缘检测/颜色分割/显著性检测/MSER提取/Otsu二值化/GrabCut前景/YOLO智能识别）
2. 调整参数配置（如Canny阈值、聚类数等）
3. 点击"执行辅助标注"按钮
4. 系统自动生成候选框
5. 在画布上选择或调整候选框

### 配置管理

1. 点击工具栏"添加配置"按钮
2. 在对话框中调整各算法参数
3. 选择保存路径，将配置保存为 YAML 文件
4. 点击"加载配置"可快速应用已有配置

---

## YOLO智能识别

### 功能说明

YOLO智能识别功能利用深度学习模型自动检测图像中的目标，并生成标注框，大幅提升标注效率。

### 模型准备

1. **准备模型文件**：将训练好的YOLO模型权重文件（.pt格式）放入项目根目录的 `model` 文件夹中
2. **支持的模型**：YOLOv8及以上版本（通过Ultralytics库支持）
3. **自动加载**：如果 `model` 文件夹中有多个模型文件，系统会自动使用第一个找到的.pt文件

### 使用方法

1. 在左侧面板选择"YOLO智能识别"模式
2. 模型路径可以留空，系统会自动查找 `model` 文件夹中的模型
3. 也可以点击"浏览"按钮手动选择模型文件
4. 调整"最小面积"参数过滤掉过小的检测框
5. 点击"执行辅助标注"按钮，系统将自动检测并生成标注框

### 模型训练

如果您需要训练自己的YOLO模型，可以参考以下资源：
- [Ultralytics YOLO 官方文档](https://docs.ultralytics.com/)
- [YOLOv8 训练教程](https://docs.ultralytics.com/modes/train/)

训练完成后，将生成的 `.pt` 权重文件放入 `model` 文件夹即可使用。

---

## 数据格式

### YOLO 格式

每个标注文件为文本格式，每行代表一个目标：

```
<class_id> <x_center> <y_center> <width> <height>
```

- 所有数值均为相对于图片尺寸的归一化值（0-1）
- `class_id`：类别索引，从 0 开始
- `x_center`, `y_center`：边界框中心点坐标
- `width`, `height`：边界框宽高



---

## 项目结构

```
yolo-annotator/
├── main.py                 # 程序入口
├── requirements.txt        # 依赖列表
├── config.py               # 配置文件
├── LICENSE                 # 许可证文件
├── readme.md               # 项目说明
├── model/                  # YOLO模型文件夹（存放.pt权重文件）
├── resources/              # 资源文件夹
│   └── logo.ico            # 应用程序图标
├── config/                 # 配置文件夹
├── core/                   # 核心模块
│   ├── annotation.py       # 标注数据模型
│   ├── yolo_io.py          # YOLO格式读写
│   ├── image_manager.py    # 图片管理
│   └── history.py          # 撤销重做管理
├── gui/                    # 界面模块
│   ├── main_window.py      # 主窗口
│   ├── canvas.py           # 标注画布
│   ├── label_dialog.py     # 标签选择对话框
│   ├── class_manager.py    # 类别管理面板
│   ├── property_panel.py   # 属性面板
│   ├── assistant_panel.py  # 辅助标注面板
│   ├── config_dialog.py    # 配置对话框
│   └── load_config_dialog.py # 加载配置对话框
├── assistant/              # 辅助标注模块
│   ├── box_proposer.py     # 候选框生成
│   ├── edge_detector.py    # 边缘检测
│   ├── color_segmenter.py  # 颜色分割
│   ├── saliency_detector.py # 显著性检测
│   ├── mser_detector.py    # MSER提取
│   ├── otsu_detector.py    # Otsu二值化
│   ├── grabcut_detector.py # GrabCut前景分割
│   └── yolo_detector.py    # YOLO智能识别
└── utils/                  # 工具模块
    └── helpers.py
```

---

## 技术栈

- **GUI 框架**：PySide6
- **图像处理**：OpenCV
- **数值计算**：NumPy
- **深度学习**：Ultralytics YOLO
- **配置解析**：PyYAML

---

## 打包

### Windows

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包为单文件可执行程序
pyinstaller -F -w -i resources\logo.ico main.py
```

### Linux/macOS

```bash
pip install pyinstaller
pyinstaller -F -w -i resources/logo.ico main.py
```

### 打包参数说明

| 参数 | 说明 |
|------|------|
| `-F` | 打包为单文件 |
| `-w` | 不显示控制台窗口 |
| `-i` | 指定图标文件 |

打包后的可执行文件将位于 `dist/` 目录下。

### 使用 spec 文件打包（高级）

```bash
pyinstaller main.spec
```

---

## 贡献

欢迎提交 Issue 或 Pull Request，共同改进项目。



## 许可证

本项目基于 [MIT](LICENSE) 许可证开源。
