"""
通用工具函数
"""
import os
import colorsys

def generate_colors(num_colors):
    """
    生成区分度高的颜色列表
    """
    colors = []
    for i in range(num_colors):
        hue = i / num_colors
        saturation = 0.7 + 0.3 * (i % 2)
        lightness = 0.5 + 0.2 * (i % 3)
        r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
        colors.append((int(r * 255), int(g * 255), int(b * 255)))
    return colors

def get_files_in_dir(directory, extensions):
    """
    获取目录下指定后缀的文件列表
    """
    files = []
    if not os.path.exists(directory):
        return files
    for f in os.listdir(directory):
        if os.path.splitext(f)[1].lower() in [ext.lower() for ext in extensions]:
            files.append(os.path.join(directory, f))
    return sorted(files)
