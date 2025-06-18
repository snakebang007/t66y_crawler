#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理工具
"""

import os
import json
from pathlib import Path

class ConfigManager:
    """配置管理类"""
    
    def __init__(self):
        # 配置文件路径（保存在用户主目录下）
        self.config_dir = Path.home() / '.bbs_image_crawler'
        self.config_file = self.config_dir / 'config.json'
        
        # 默认配置
        self.default_config = {
            'last_save_path': '',
            'window_geometry': {
                'x': 100,
                'y': 100,
                'width': 1000,
                'height': 700
            },
            'download_delay': 0.5,
            'timeout': 15
        }
        
        # 确保配置目录存在
        self.config_dir.mkdir(exist_ok=True)
        
        # 加载配置
        self.config = self.load_config()
    
    def load_config(self):
        """
        加载配置文件
        
        Returns:
            dict: 配置字典
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 合并默认配置（确保新增的配置项有默认值）
                merged_config = self.default_config.copy()
                merged_config.update(config)
                return merged_config
            else:
                # 如果配置文件不存在，返回默认配置
                return self.default_config.copy()
                
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return self.default_config.copy()
    
    def save_config(self):
        """
        保存配置到文件
        
        Returns:
            bool: 是否保存成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get_last_save_path(self):
        """
        获取上次保存路径
        
        Returns:
            str: 上次保存的路径，如果不存在或无效则返回空字符串
        """
        last_path = self.config.get('last_save_path', '')
        
        # 检查路径是否仍然有效
        if last_path and os.path.exists(last_path) and os.path.isdir(last_path):
            return last_path
        else:
            return ''
    
    def set_last_save_path(self, path):
        """
        设置上次保存路径
        
        Args:
            path: 保存路径
        """
        if path and os.path.exists(path) and os.path.isdir(path):
            self.config['last_save_path'] = path
            self.save_config()
    
    def get_window_geometry(self):
        """
        获取窗口几何信息
        
        Returns:
            dict: 窗口位置和大小信息
        """
        return self.config.get('window_geometry', self.default_config['window_geometry'])
    
    def set_window_geometry(self, x, y, width, height):
        """
        设置窗口几何信息
        
        Args:
            x: 窗口x坐标
            y: 窗口y坐标
            width: 窗口宽度
            height: 窗口高度
        """
        self.config['window_geometry'] = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
        self.save_config()
    
    def get_download_delay(self):
        """
        获取下载延时
        
        Returns:
            float: 下载延时（秒）
        """
        return self.config.get('download_delay', 0.5)
    
    def set_download_delay(self, delay):
        """
        设置下载延时
        
        Args:
            delay: 延时时间（秒）
        """
        self.config['download_delay'] = delay
        self.save_config()
    
    def get_timeout(self):
        """
        获取网络超时时间
        
        Returns:
            int: 超时时间（秒）
        """
        return self.config.get('timeout', 15)
    
    def set_timeout(self, timeout):
        """
        设置网络超时时间
        
        Args:
            timeout: 超时时间（秒）
        """
        self.config['timeout'] = timeout
        self.save_config()
    
    def reset_config(self):
        """
        重置配置为默认值
        """
        self.config = self.default_config.copy()
        self.save_config()
    
    def get_config_file_path(self):
        """
        获取配置文件路径
        
        Returns:
            str: 配置文件完整路径
        """
        return str(self.config_file) 