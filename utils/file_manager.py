#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理工具
"""

import os
import shutil
from datetime import datetime
from PIL import Image

class FileManager:
    """文件管理类"""
    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    
    def create_directory(self, path):
        """
        创建目录
        
        Args:
            path: 目录路径
            
        Returns:
            bool: 是否创建成功
        """
        try:    
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建目录失败: {e}")
            return False
    
    def is_valid_image(self, file_path):
        """
        检查是否为有效图片文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否为有效图片
        """
        if not os.path.exists(file_path):
            return False
        
        # 检查文件扩展名
        _, ext = os.path.splitext(file_path.lower())
        if ext not in self.supported_formats:
            return False
        
        # 尝试打开图片验证
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def get_file_size(self, file_path):
        """
        获取文件大小
        
        Args:
            file_path: 文件路径
            
        Returns:
            int: 文件大小（字节）
        """
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0
    
    def format_file_size(self, size_bytes):
        """
        格式化文件大小
        
        Args:
            size_bytes: 字节数
            
        Returns:
            str: 格式化后的大小
        """
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def get_image_info(self, file_path):
        """
        获取图片信息
        
        Args:
            file_path: 图片路径
            
        Returns:
            dict: 图片信息
        """
        info = {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': 0,
            'size_formatted': '0B',
            'width': 0,
            'height': 0,
            'format': 'Unknown',
            'created_time': '',
            'valid': False
        }
        
        try:
            if os.path.exists(file_path):
                # 文件基本信息
                stat = os.stat(file_path)
                info['size'] = stat.st_size
                info['size_formatted'] = self.format_file_size(stat.st_size)
                info['created_time'] = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                
                # 图片信息
                with Image.open(file_path) as img:
                    info['width'] = img.width
                    info['height'] = img.height
                    info['format'] = img.format
                    info['valid'] = True
                    
        except Exception as e:
            print(f"获取图片信息失败: {e}")
        
        return info
    
    def clean_filename(self, filename):
        """
        清理文件名，移除非法字符
        
        Args:
            filename: 原文件名
            
        Returns:
            str: 清理后的文件名
        """
        import re
        # 移除或替换非法字符
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 移除多余的空格和点
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = cleaned.strip('.')
        
        # 确保文件名不为空
        if not cleaned:
            cleaned = f"image_{int(datetime.now().timestamp())}"
        
        return cleaned
    
    def move_file(self, src_path, dst_path):
        """
        移动文件
        
        Args:
            src_path: 源路径
            dst_path: 目标路径
            
        Returns:
            bool: 是否移动成功
        """
        try:
            # 确保目标目录存在
            dst_dir = os.path.dirname(dst_path)
            self.create_directory(dst_dir)
            
            shutil.move(src_path, dst_path)
            return True
        except Exception as e:
            print(f"移动文件失败: {e}")
            return False
    
    def copy_file(self, src_path, dst_path):
        """
        复制文件
        
        Args:
            src_path: 源路径
            dst_path: 目标路径
            
        Returns:
            bool: 是否复制成功
        """
        try:
            # 确保目标目录存在
            dst_dir = os.path.dirname(dst_path)
            self.create_directory(dst_dir)
            
            shutil.copy2(src_path, dst_path)
            return True
        except Exception as e:
            print(f"复制文件失败: {e}")
            return False
    
    def delete_file(self, file_path):
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否删除成功
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"删除文件失败: {e}")
            return False
    
    def list_images_in_directory(self, directory):
        """
        列出目录中的所有图片文件
        
        Args:
            directory: 目录路径
            
        Returns:
            list: 图片文件路径列表
        """
        images = []
        
        if not os.path.exists(directory):
            return images
        
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path) and self.is_valid_image(file_path):
                    images.append(file_path)
        except Exception as e:
            print(f"列出图片文件失败: {e}")
        
        return sorted(images)
    
    def create_thumbnail(self, image_path, thumbnail_path, size=(150, 150)):
        """
        创建缩略图
        
        Args:
            image_path: 原图片路径
            thumbnail_path: 缩略图保存路径
            size: 缩略图尺寸
            
        Returns:
            bool: 是否创建成功
        """
        try:
            with Image.open(image_path) as img:
                # 转换为RGB模式（处理RGBA等格式）
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # 创建缩略图
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # 确保目标目录存在
                thumbnail_dir = os.path.dirname(thumbnail_path)
                self.create_directory(thumbnail_dir)
                
                # 保存缩略图
                img.save(thumbnail_path, 'JPEG', quality=85)
                
            return True
        except Exception as e:
            print(f"创建缩略图失败: {e}")
            return False 