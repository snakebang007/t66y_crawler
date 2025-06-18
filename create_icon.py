#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为程序创建图标文件
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """创建程序图标"""
    # 创建一个 256x256 的图标
    size = 256
    img = Image.new('RGBA', (size, size), (70, 130, 180, 255))  # 钢蓝色背景
    draw = ImageDraw.Draw(img)
    
    # 绘制一个简单的图片框图标
    margin = 40
    
    # 外框
    draw.rectangle([margin, margin, size-margin, size-margin], 
                  outline=(255, 255, 255, 255), width=8, fill=(100, 149, 237, 255))
    
    # 内部装饰
    inner_margin = margin + 20
    draw.rectangle([inner_margin, inner_margin, size-inner_margin, size-inner_margin], 
                  outline=(255, 255, 255, 255), width=4)
    
    # 绘制一个简单的图片符号
    center_x, center_y = size // 2, size // 2
    
    # 山形图案
    points = [
        (center_x - 60, center_y + 30),
        (center_x - 20, center_y - 20),
        (center_x + 20, center_y),
        (center_x + 60, center_y - 30),
        (center_x + 60, center_y + 30)
    ]
    draw.polygon(points, fill=(255, 255, 255, 255))
    
    # 太阳
    draw.ellipse([center_x - 80, center_y - 60, center_x - 50, center_y - 30], 
                fill=(255, 255, 0, 255))
    
    # 保存为不同尺寸的图标
    sizes = [256, 128, 64, 48, 32, 16]
    images = []
    
    for s in sizes:
        resized = img.resize((s, s), Image.Resampling.LANCZOS)
        images.append(resized)
    
    # 保存为 .ico 文件
    img.save('app_icon.ico', format='ICO', sizes=[(s, s) for s in sizes])
    print("✅ 已创建图标文件: app_icon.ico")

if __name__ == "__main__":
    create_icon() 