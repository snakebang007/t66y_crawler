#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终极反爬虫破解器
专门针对特殊的反爬虫机制
"""

import requests
import time
import random
import json
import base64
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class UltimateBypass:
    """终极绕过器"""
    
    def __init__(self):
        self.session = requests.Session()
        
    def try_special_methods(self, url):
        """尝试特殊方法"""
        print(f"🎯 开始终极破解: {url}")
        print("=" * 60)
        
        methods = [
            self.method_old_browser,
            self.method_wget_simulation,
            self.method_python_requests,
            self.method_api_client,
            self.method_rss_reader,
            self.method_social_media_bot,
            self.method_archive_crawler,
            self.method_academic_crawler
        ]
        
        for i, method in enumerate(methods, 1):
            print(f"\n🔧 尝试特殊方法 {i}/{len(methods)}")
            try:
                result = method(url)
                if result and self.is_success(result):
                    print(f"🎉 方法 {i} 成功破解!")
                    return result
                else:
                    print(f"❌ 方法 {i} 失败")
            except Exception as e:
                print(f"❌ 方法 {i} 异常: {e}")
            
            time.sleep(random.uniform(1, 2))
        
        return None
    
    def method_old_browser(self, url):
        """方法1: 模拟老版本浏览器"""
        print("🔄 模拟老版本浏览器")
        headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Connection': 'keep-alive'
        }
        response = self.session.get(url, headers=headers, timeout=15, verify=False)
        return self.process_response(response, "老版本浏览器")
    
    def method_wget_simulation(self, url):
        """方法2: 模拟wget"""
        print("🔄 模拟wget工具")
        headers = {
            'User-Agent': 'Wget/1.21.3',
            'Accept': '*/*',
            'Accept-Encoding': 'identity',
            'Connection': 'Keep-Alive'
        }
        response = self.session.get(url, headers=headers, timeout=15, verify=False)
        return self.process_response(response, "wget模拟")
    
    def method_python_requests(self, url):
        """方法3: 模拟Python requests库"""
        print("🔄 模拟Python requests")
        headers = {
            'User-Agent': 'python-requests/2.31.0',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        response = self.session.get(url, headers=headers, timeout=15, verify=False)
        return self.process_response(response, "Python requests")
    
    def method_api_client(self, url):
        """方法4: 模拟API客户端"""
        print("🔄 模拟API客户端")
        headers = {
            'User-Agent': 'PostmanRuntime/7.32.3',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }
        response = self.session.get(url, headers=headers, timeout=15, verify=False)
        return self.process_response(response, "API客户端")
    
    def method_rss_reader(self, url):
        """方法5: 模拟RSS阅读器"""
        print("🔄 模拟RSS阅读器")
        headers = {
            'User-Agent': 'FeedBurner/1.0 (http://www.FeedBurner.com)',
            'Accept': 'application/rss+xml, application/xml, text/xml',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        response = self.session.get(url, headers=headers, timeout=15, verify=False)
        return self.process_response(response, "RSS阅读器")
    
    def method_social_media_bot(self, url):
        """方法6: 模拟社交媒体爬虫"""
        print("🔄 模拟社交媒体爬虫")
        bots = [
            'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
            'Twitterbot/1.0',
            'LinkedInBot/1.0 (compatible; Mozilla/5.0; Apache-HttpClient +http://www.linkedin.com/)'
        ]
        headers = {
            'User-Agent': random.choice(bots),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        response = self.session.get(url, headers=headers, timeout=15, verify=False)
        return self.process_response(response, "社交媒体爬虫")
    
    def method_archive_crawler(self, url):
        """方法7: 模拟存档爬虫"""
        print("🔄 模拟存档爬虫")
        headers = {
            'User-Agent': 'ia_archiver (+http://www.alexa.com/site/help/webmasters; crawler@alexa.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        response = self.session.get(url, headers=headers, timeout=15, verify=False)
        return self.process_response(response, "存档爬虫")
    
    def method_academic_crawler(self, url):
        """方法8: 模拟学术爬虫"""
        print("🔄 模拟学术爬虫")
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; archive.org_bot +http://www.archive.org/details/archive.org_bot)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'From': 'research@university.edu'
        }
        response = self.session.get(url, headers=headers, timeout=15, verify=False)
        return self.process_response(response, "学术爬虫")
    
    def process_response(self, response, method_name):
        """处理响应"""
        if response.encoding is None:
            response.encoding = response.apparent_encoding or 'utf-8'
        
        content = response.text
        print(f"   📊 {method_name}: 状态码{response.status_code}, 长度{len(content)}")
        print(f"   📄 内容预览: {content[:100]}...")
        
        return {
            'method': method_name,
            'status_code': response.status_code,
            'content': content,
            'length': len(content),
            'headers': dict(response.headers)
        }
    
    def is_success(self, result):
        """判断是否成功"""
        content = result['content']
        
        # 如果内容长度太短，认为失败
        if len(content) < 100:
            return False
        
        # 如果包含Access disabled，认为失败
        if "Access disabled" in content:
            return False
        
        # 如果是乱码（包含很多非ASCII字符），认为失败
        try:
            content.encode('ascii')
        except UnicodeEncodeError:
            non_ascii_ratio = sum(1 for c in content if ord(c) > 127) / len(content)
            if non_ascii_ratio > 0.3:  # 如果超过30%是非ASCII字符
                return False
        
        # 如果包含HTML标签，认为可能成功
        if '<html' in content.lower() and '</html>' in content.lower():
            return True
        
        return False
    
    def extract_images_advanced(self, content, base_url):
        """高级图片提取"""
        if not content:
            return []
        
        print("🖼️ 开始高级图片提取...")
        
        soup = BeautifulSoup(content, 'html.parser')
        image_urls = set()
        
        # 1. 标准img标签
        for img in soup.find_all('img'):
            for attr in ['src', 'data-src', 'data-original', 'data-lazy', 'data-srcset']:
                src = img.get(attr)
                if src:
                    urls = self.extract_urls_from_srcset(src)
                    for url in urls:
                        full_url = urljoin(base_url, url)
                        if self.is_image_url(full_url):
                            image_urls.add(full_url)
        
        # 2. picture标签
        for picture in soup.find_all('picture'):
            for source in picture.find_all('source'):
                srcset = source.get('srcset')
                if srcset:
                    urls = self.extract_urls_from_srcset(srcset)
                    for url in urls:
                        full_url = urljoin(base_url, url)
                        if self.is_image_url(full_url):
                            image_urls.add(full_url)
        
        # 3. CSS背景图片
        for element in soup.find_all(style=True):
            style = element.get('style', '')
            bg_matches = re.findall(r'background(?:-image)?\s*:\s*url\(["\']?([^"\']+)["\']?\)', style)
            for match in bg_matches:
                full_url = urljoin(base_url, match)
                if self.is_image_url(full_url):
                    image_urls.add(full_url)
        
        # 4. JavaScript中的图片URL
        for script in soup.find_all('script'):
            if script.string:
                js_matches = re.findall(r'["\']([^"\']*\.(?:jpg|jpeg|png|gif|bmp|webp|svg)[^"\']*)["\']', script.string, re.IGNORECASE)
                for match in js_matches:
                    full_url = urljoin(base_url, match)
                    if self.is_image_url(full_url):
                        image_urls.add(full_url)
        
        # 5. 全文正则搜索
        patterns = [
            r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|gif|bmp|webp|svg)(?:\?[^\s"\'<>]*)?',
            r'["\']([^"\']+\.(?:jpg|jpeg|png|gif|bmp|webp|svg)(?:\?[^"\']*)?)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if match:
                    full_url = urljoin(base_url, match)
                    if self.is_image_url(full_url):
                        image_urls.add(full_url)
        
        result = list(image_urls)
        print(f"   🎯 总共找到 {len(result)} 个图片URL")
        
        return result
    
    def extract_urls_from_srcset(self, srcset):
        """从srcset中提取URL"""
        urls = []
        if srcset:
            # srcset格式: "url1 1x, url2 2x" 或 "url1 100w, url2 200w"
            parts = srcset.split(',')
            for part in parts:
                url = part.strip().split()[0]
                if url:
                    urls.append(url)
        return urls
    
    def is_image_url(self, url):
        """检查是否是图片URL"""
        if not url or len(url) < 5:
            return False
        
        # 过滤掉明显的非图片URL
        if any(bad in url.lower() for bad in ['javascript:', 'mailto:', 'tel:', 'data:']):
            return False
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
        url_lower = url.lower()
        
        # 检查扩展名
        if any(ext in url_lower for ext in image_extensions):
            return True
        
        # 检查关键词
        if any(keyword in url_lower for keyword in ['image', 'img', 'photo', 'pic', 'avatar', 'thumb']):
            return True
        
        return False
    
    def ultimate_crack(self, url):
        """终极破解"""
        result = self.try_special_methods(url)
        
        if result:
            print(f"\n🎉 成功破解! 使用方法: {result['method']}")
            
            # 提取图片
            images = self.extract_images_advanced(result['content'], url)
            
            return {
                'success': True,
                'method': result['method'],
                'status_code': result['status_code'],
                'content_length': result['length'],
                'images': images,
                'image_count': len(images),
                'content_preview': result['content'][:1000],
                'response_headers': result['headers']
            }
        else:
            return {
                'success': False,
                'message': '所有破解方法都失败了',
                'images': []
            }

def main():
    if len(sys.argv) < 2:
        print("使用方法: python3 ultimate_bypass.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    bypass = UltimateBypass()
    result = bypass.ultimate_crack(url)
    
    print("\n" + "=" * 60)
    print("🏆 终极破解结果:")
    print(f"   成功: {result['success']}")
    
    if result['success']:
        print(f"   破解方法: {result['method']}")
        print(f"   状态码: {result['status_code']}")
        print(f"   内容长度: {result['content_length']}")
        print(f"   找到图片: {result['image_count']} 张")
        
        if result['images']:
            print(f"   图片列表:")
            for i, img_url in enumerate(result['images'], 1):
                print(f"      {i}. {img_url}")
        
        print(f"\n   响应头:")
        for key, value in result['response_headers'].items():
            print(f"      {key}: {value}")
        
        print(f"\n   内容预览:")
        print(f"   {result['content_preview']}")
    else:
        print(f"   失败原因: {result['message']}")
    
    print(f"\n📋 JSON结果:")
    # 移除content_preview以避免输出过长
    output_result = result.copy()
    if 'content_preview' in output_result:
        output_result['content_preview'] = output_result['content_preview'][:200] + "..."
    print(json.dumps(output_result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main() 