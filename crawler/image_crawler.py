#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片爬虫核心功能
"""

import os
import re
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from utils.file_manager import FileManager
import ssl
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ImageCrawler:
    """图片爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.file_manager = FileManager()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置请求头，模拟浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 支持的图片格式
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'}
        
    def crawl_images(self, url, save_path, progress_callback=None):
        """
        爬取图片
        
        Args:
            url: 目标网址
            save_path: 保存路径
            progress_callback: 进度回调函数
            
        Returns:
            list: 下载的图片路径列表
        """
        downloaded_images = []
        
        try:
            if progress_callback:
                progress_callback("正在获取网页内容...")
            
            # 获取网页内容，添加SSL和重试处理
            response = self._safe_request(url)
            
            if progress_callback:
                progress_callback("正在解析网页...")
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有图片链接
            image_urls = self._extract_image_urls(soup, url, response.text)
            
            if not image_urls:
                if progress_callback:
                    progress_callback("未找到图片链接")
                return downloaded_images
            
            if progress_callback:
                progress_callback(f"找到 {len(image_urls)} 个图片链接，开始下载...")
            
            # 创建保存目录 - 使用网页标题作为文件夹名
            folder_name = self._generate_folder_name(soup, url)
            save_dir = os.path.join(save_path, folder_name)
            os.makedirs(save_dir, exist_ok=True)
            
            # 下载图片
            for i, img_url in enumerate(image_urls, 1):
                try:
                    if progress_callback:
                        progress_callback(f"正在下载第 {i}/{len(image_urls)} 张图片...")
                    
                    image_path = self._download_image(img_url, save_dir)
                    if image_path:
                        downloaded_images.append(image_path)
                        if progress_callback:
                            progress_callback(f"已下载: {os.path.basename(image_path)}", image_path)
                    
                    # 添加延时，避免请求过快
                    time.sleep(0.5)
                    
                except Exception as e:
                    if progress_callback:
                        progress_callback(f"下载图片失败: {str(e)}")
                    continue
            
            if progress_callback:
                progress_callback(f"下载完成，共保存 {len(downloaded_images)} 张图片到: {save_dir}")
                
        except Exception as e:
            raise Exception(f"爬取失败: {str(e)}")
        
        return downloaded_images
    
    def _safe_request(self, url, max_retries=3):
        """
        安全的网络请求，处理SSL错误和重试
        
        Args:
            url: 请求URL
            max_retries: 最大重试次数
            
        Returns:
            Response对象
        """
        for attempt in range(max_retries):
            try:
                # 尝试正常请求
                response = self.session.get(url, timeout=15, verify=True)
                response.raise_for_status()
                response.encoding = response.apparent_encoding
                return response
                
            except requests.exceptions.SSLError as e:
                if attempt < max_retries - 1:
                    print(f"SSL错误，尝试使用不验证SSL的方式 (尝试 {attempt + 1}/{max_retries})")
                    try:
                        # 尝试不验证SSL
                        response = self.session.get(url, timeout=15, verify=False)
                        response.raise_for_status()
                        response.encoding = response.apparent_encoding
                        return response
                    except Exception as e2:
                        print(f"不验证SSL也失败: {e2}")
                        if attempt < max_retries - 1:
                            time.sleep(2 ** attempt)  # 指数退避
                            continue
                        else:
                            raise e2
                else:
                    raise e
                    
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    print(f"连接错误，重试中 (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    raise e
                    
            except requests.exceptions.Timeout as e:
                if attempt < max_retries - 1:
                    print(f"请求超时，重试中 (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise e
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"其他错误，重试中 (尝试 {attempt + 1}/{max_retries}): {e}")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    raise e
    
    def _generate_folder_name(self, soup, url):
        """
        生成文件夹名称，基于网页标题
        
        Args:
            soup: BeautifulSoup对象
            url: 网页URL
            
        Returns:
            str: 清理后的文件夹名称
        """
        # 尝试获取网页标题
        title = ""
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            title = title_tag.string.strip()
        
        # 如果没有标题，尝试获取h1标签
        if not title:
            h1_tag = soup.find('h1')
            if h1_tag:
                title = h1_tag.get_text().strip()
        
        # 如果还是没有标题，使用域名作为备选
        if not title:
            domain = urlparse(url).netloc
            title = f"images_from_{domain}"
        
        # 清理标题，去掉非法字符
        cleaned_title = self._clean_filename(title)
        
        # 如果清理后的标题为空或太短，使用备选方案
        if len(cleaned_title) < 3:
            domain = urlparse(url).netloc
            timestamp = int(time.time())
            cleaned_title = f"images_{domain}_{timestamp}"
            cleaned_title = self._clean_filename(cleaned_title)
        
        # 限制文件夹名长度（Windows路径限制）
        if len(cleaned_title) > 100:
            cleaned_title = cleaned_title[:100]
        
        # 添加时间戳避免重复（可选，如果需要唯一性）
        timestamp = int(time.time())
        final_name = f"{cleaned_title}_{timestamp}"
        
        return final_name
    
    def _clean_filename(self, filename):
        """
        清理文件名，去掉Windows和macOS不支持的字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        if not filename:
            return "untitled"
        
        # Windows和macOS都不支持的字符
        illegal_chars = r'[<>:"/\\|?*]'
        
        # 替换非法字符为下划线
        cleaned = re.sub(illegal_chars, '_', filename)
        
        # 去掉控制字符（ASCII 0-31）
        cleaned = re.sub(r'[\x00-\x1f]', '', cleaned)
        
        # 去掉多余的空格和标点
        cleaned = re.sub(r'\s+', ' ', cleaned)  # 多个空格变成一个
        cleaned = cleaned.strip()  # 去掉首尾空格
        cleaned = cleaned.strip('.')  # 去掉首尾的点
        
        # Windows保留名称检查
        windows_reserved = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        if cleaned.upper() in windows_reserved:
            cleaned = f"_{cleaned}_"
        
        # 如果清理后为空，使用默认名称
        if not cleaned:
            cleaned = "untitled"
        
        return cleaned
    
    def _extract_image_urls(self, soup, base_url, page_content):
        """
        提取图片URL
        
        Args:
            soup: BeautifulSoup对象
            base_url: 基础URL
            page_content: 网页原始内容
            
        Returns:
            list: 图片URL列表
        """
        image_urls = set()
        
        # 方法1: 查找img标签
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src') or img.get('data-src') or img.get('data-original') or img.get('data-lazy')
            if src:
                # 转换为绝对URL
                absolute_url = urljoin(base_url, src)
                if self._is_valid_image_url(absolute_url):
                    image_urls.add(absolute_url)
        
        # 方法2: 查找a标签中的图片链接
        a_tags = soup.find_all('a', href=True)
        for a in a_tags:
            href = a['href']
            absolute_url = urljoin(base_url, href)
            if self._is_valid_image_url(absolute_url):
                image_urls.add(absolute_url)
        
        # 方法3: 查找CSS背景图片
        style_tags = soup.find_all(['div', 'span', 'section'], style=True)
        for tag in style_tags:
            style = tag.get('style', '')
            bg_images = re.findall(r'background-image:\s*url\(["\']?([^"\']+)["\']?\)', style)
            for bg_img in bg_images:
                absolute_url = urljoin(base_url, bg_img)
                if self._is_valid_image_url(absolute_url):
                    image_urls.add(absolute_url)
        
        # 方法4: 使用正则表达式在整个页面内容中搜索图片URL（新增）
        image_patterns = [
            # 匹配完整的HTTP/HTTPS图片URL
            r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|gif|bmp|webp|svg)',
            # 匹配src属性中的图片
            r'src\s*=\s*["\']([^"\']+\.(?:jpg|jpeg|png|gif|bmp|webp|svg))["\']',
            # 匹配data-src属性中的图片
            r'data-src\s*=\s*["\']([^"\']+\.(?:jpg|jpeg|png|gif|bmp|webp|svg))["\']',
            # 匹配data-original属性中的图片
            r'data-original\s*=\s*["\']([^"\']+\.(?:jpg|jpeg|png|gif|bmp|webp|svg))["\']',
            # 匹配JavaScript中的图片URL
            r'["\']([^"\']*(?:https?://)?[^"\']*\.(?:jpg|jpeg|png|gif|bmp|webp|svg))["\']'
        ]
        
        for pattern in image_patterns:
            matches = re.findall(pattern, page_content, re.IGNORECASE)
            for match in matches:
                # 处理元组结果（某些正则表达式会返回元组）
                if isinstance(match, tuple):
                    match = next((m for m in match if m), '')
                
                if match:
                    # 转换为绝对URL
                    if match.startswith(('http://', 'https://')):
                        absolute_url = match
                    else:
                        absolute_url = urljoin(base_url, match)
                    
                    if self._is_valid_image_url(absolute_url):
                        image_urls.add(absolute_url)
        
        return list(image_urls)
    
    def _is_valid_image_url(self, url):
        """
        检查是否为有效的图片URL
        
        Args:
            url: 图片URL
            
        Returns:
            bool: 是否有效
        """
        if not url or not url.startswith(('http://', 'https://')):
            return False
        
        # 过滤掉明显的非图片URL
        if any(keyword in url.lower() for keyword in ['javascript:', 'mailto:', 'tel:', '#']):
            return False
        
        # 检查文件扩展名
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        # 直接检查扩展名
        for ext in self.image_extensions:
            if path.endswith(ext):
                return True
        
        # 检查是否包含图片相关关键词
        if any(keyword in url.lower() for keyword in ['image', 'img', 'photo', 'pic', 'avatar']):
            return True
        
        # 检查是否是常见的图片托管服务
        image_hosts = ['imgur.com', 'i.imgur.com', '66img.cc', '23img.com', 'postimg.cc', 'imgbb.com']
        for host in image_hosts:
            if host in url.lower():
                return True
        
        return False
    
    def _download_image(self, url, save_dir):
        """
        下载单张图片
        
        Args:
            url: 图片URL
            save_dir: 保存目录
            
        Returns:
            str: 保存的文件路径，失败返回None
        """
        try:
            # 设置特殊的请求头，某些图片服务器需要Referer
            headers = self.session.headers.copy()
            headers.update({
                'Referer': url,
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
            })
            
            # 获取图片，使用安全请求方法
            response = self._safe_image_request(url, headers)
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '').lower()
            if not (content_type.startswith('image/') or 'image' in content_type):
                # 如果Content-Type不是图片，但URL看起来像图片，仍然尝试下载
                if not any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
                    return None
            
            # 生成文件名
            filename = self._generate_filename(url, content_type)
            file_path = os.path.join(save_dir, filename)
            
            # 避免重复下载
            if os.path.exists(file_path):
                return file_path
            
            # 保存图片
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 验证文件大小
            if os.path.getsize(file_path) < 500:  # 小于500字节的文件可能不是有效图片
                os.remove(file_path)
                return None
            
            return file_path
            
        except Exception as e:
            return None
    
    def _safe_image_request(self, url, headers, max_retries=2):
        """
        安全的图片请求
        
        Args:
            url: 图片URL
            headers: 请求头
            max_retries: 最大重试次数
            
        Returns:
            Response对象
        """
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=15, stream=True, headers=headers, verify=True)
                response.raise_for_status()
                return response
                
            except requests.exceptions.SSLError:
                if attempt < max_retries - 1:
                    try:
                        # 尝试不验证SSL
                        response = self.session.get(url, timeout=15, stream=True, headers=headers, verify=False)
                        response.raise_for_status()
                        return response
                    except Exception:
                        time.sleep(1)
                        continue
                else:
                    raise
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    raise e
    
    def _generate_filename(self, url, content_type):
        """
        生成文件名
        
        Args:
            url: 图片URL
            content_type: 内容类型
            
        Returns:
            str: 文件名
        """
        # 从URL中提取文件名
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        if path and '.' in os.path.basename(path):
            filename = os.path.basename(path)
            # 移除查询参数
            if '?' in filename:
                filename = filename.split('?')[0]
        else:
            # 根据content-type生成扩展名
            ext_map = {
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'image/gif': '.gif',
                'image/bmp': '.bmp',
                'image/webp': '.webp',
                'image/svg+xml': '.svg'
            }
            ext = ext_map.get(content_type, '.jpg')
            filename = f"image_{int(time.time() * 1000)}{ext}"
        
        # 清理文件名
        filename = self._clean_filename(filename)
        
        return filename 