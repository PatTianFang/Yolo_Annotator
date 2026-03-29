"""
全局配置文件
"""

# 支持的图像格式
SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".bmp", ".JPG", ".JPEG", ".PNG", ".BMP"]

# UI 配置
WINDOW_TITLE = "YOLO 辅助标注软件"
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800

# 标注相关配置
DEFAULT_LINE_WIDTH = 2
DEFAULT_POINT_RADIUS = 4

# 颜色配置 (RGB)
COLOR_BBOX_NORMAL = (0, 255, 0)      # 默认框颜色
COLOR_BBOX_SELECTED = (255, 0, 0)    # 选中框颜色
COLOR_BBOX_HOVER = (255, 255, 0)     # 悬停框颜色
COLOR_CROSSHAIR = (255, 255, 255)    # 十字准星颜色
COLOR_BACKGROUND = (40, 40, 40)      # 画布背景颜色


# ============================================
# 辅助标注算法参数配置
# ============================================

# 边缘检测 (Canny Edge Detector) 参数
# 基于 Canny 算法的边缘检测，用于检测物体轮廓
EDGE_CANNY_THRESHOLD1 = 50           # 低阈值：低于此值的边缘被丢弃
EDGE_CANNY_THRESHOLD2 = 150          # 高阈值：高于此值的边缘被保留，中间的边缘根据连通性决定
EDGE_GAUSSIAN_BLUR_SIZE = 5          # 高斯模糊核大小，用于降噪
EDGE_DILATE_ITERATIONS = 1           # 膨胀迭代次数，用于连接断裂的边缘
EDGE_DILATE_KERNEL_SIZE = 3          # 膨胀核大小
# 边缘检测 - 界面参数范围
EDGE_CANNY_THRESHOLD_MIN = 0         # Canny阈值设置范围的最小值
EDGE_CANNY_THRESHOLD_MAX = 255       # Canny阈值设置范围的最大值

# 颜色分割 (K-Means Color Segmentation) 参数
# 基于 K-Means 聚类的颜色分割，将图像按颜色聚类分割成不同区域
COLOR_KMEANS_K = 3                   # 聚类中心数量 (K值)，即将图像分割成多少种颜色区域
COLOR_KMEANS_CRITERIA_EPS = 1.0      # 算法收敛的epsilon值
COLOR_KMEANS_CRITERIA_MAX_ITER = 10  # 最大迭代次数
COLOR_KMEANS_ATTEMPTS = 10           # 使用不同初始标签执行算法的次数
COLOR_MORPH_OPEN_KERNEL_SIZE = 5     # 开运算核大小，用于去除噪点
# 颜色分割 - 界面参数范围
COLOR_KMEANS_K_MIN = 2               # K-Means聚类数设置范围的最小值
COLOR_KMEANS_K_MAX = 20              # K-Means聚类数设置范围的最大值

# 显著性检测 (Saliency Detection) 参数
# 基于谱残差法的显著性检测，用于检测图像中最引人注目的区域
SALIENCY_FALLBACK_BLUR_SIZE = 11     # Fallback模式下的高斯模糊核大小
SALIENCY_FALLBACK_THRESHOLD = 200    # Fallback模式下的二值化阈值 (0-255)

# MSER (Maximally Stable Extremal Regions) 参数
# 用于检测斑点、文本区域等，对视角变化具有鲁棒性
MSER_DELTA = 5                       # 比较灰度值以确定稳定性的增量值
# MSER - 界面参数范围
MSER_DELTA_MIN = 1                   # MSER Delta设置范围的最小值
MSER_DELTA_MAX = 100                 # MSER Delta设置范围的最大值

# OTSU (大津法/最大类间方差法) 参数
# 自动计算最佳阈值进行图像二值化，同时检测亮物体和暗物体
OTSU_BLUR_SIZE = 5                   # 高斯模糊核大小，用于降噪（必须是奇数）
# OTSU - 界面参数范围
OTSU_BLUR_SIZE_MIN = 1               # Otsu高斯核大小设置范围的最小值
OTSU_BLUR_SIZE_MAX = 31              # Otsu高斯核大小设置范围的最大值
OTSU_BLUR_SIZE_STEP = 2              # Otsu高斯核大小设置的步长（必须为奇数）

# GrabCut 前景分割参数
# 基于图割算法的前景/背景分割，需要迭代优化
GRABCUT_ITER_COUNT = 5               # 迭代次数，次数越多分割越精确但越慢
GRABCUT_MARGIN = 10                  # 初始前景矩形边距（从图像边缘内缩的像素数）
GRABCUT_MORPH_KERNEL_SIZE = 5        # 形态学运算核大小，用于去噪和平滑分割结果
# GrabCut - 界面参数范围
GRABCUT_ITER_COUNT_MIN = 1           # GrabCut迭代次数设置范围的最小值
GRABCUT_ITER_COUNT_MAX = 20          # GrabCut迭代次数设置范围的最大值
GRABCUT_MARGIN_MIN = 1               # GrabCut边缘留白设置范围的最小值
GRABCUT_MARGIN_MAX = 500             # GrabCut边缘留白设置范围的最大值

# YOLO 智能识别参数
# 基于YOLO深度学习模型的目标检测，用于自动识别和标注目标
YOLO_MODEL_PATH = ""                 # YOLO模型权重文件路径，留空则自动使用model文件夹中的模型
YOLO_CONF_THRESHOLD = 0.4            # YOLO检测的置信度阈值 (0-1)，越高越严格

# 框提议 (Box Proposal) 通用参数
# 控制所有检测算法生成标注框的后处理
BOX_MIN_AREA = 400                   # 最小框面积阈值，小于此面积的框被过滤
BOX_MIN_AREA_MIN = 10                # 最小框面积设置范围的最小值
BOX_MIN_AREA_MAX = 100000            # 最小框面积设置范围的最大值
BOX_MIN_AREA_STEP = 100              # 最小框面积设置的步长

BOX_NMS_THRESHOLD = 0.3              # 非极大值抑制 (NMS) 的IoU阈值 (0-1)，越大保留的框越多
BOX_NMS_THRESHOLD_MIN = 0.01         # NMS阈值设置范围的最小值
BOX_NMS_THRESHOLD_MAX = 1.0          # NMS阈值设置范围的最大值
BOX_NMS_THRESHOLD_STEP = 0.1         # NMS阈值设置的步长
