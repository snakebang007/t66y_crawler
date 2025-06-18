#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级反反爬虫破解器
使用多种技术绕过网站保护
"""

import requests
import time
import random
import json
import base64
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import re
import sys
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AdvancedBypassCrawler:
    """高级绕过爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_advanced_session()
        self.cookies_jar = {}
        
    def setup_advanced_session(self):
        """设置高级会话配置"""
        # 配置重试策略
        retry_strategy = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504, 520, 521, 522, 524],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 高级浏览器指纹
        self.user_agents = [
            # Chrome 最新版本
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Firefox 最新版本
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            # Safari
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            # Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        ]
        
        # 设置基础请求头
        self.base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Sec-GPC': '1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
    def get_random_headers(self, referer=None):
        """获取随机请求头"""
        headers = self.base_headers.copy()
        headers['User-Agent'] = random.choice(self.user_agents)
        
        if referer:
            headers['Referer'] = referer
            
        # 随机添加一些可选头
        if random.choice([True, False]):
            headers['X-Requested-With'] = 'XMLHttpRequest'
            
        return headers
    
    def method_1_direct_access(self, url):
        """方法1: 直接访问"""
        print("🔄 方法1: 直接访问")
        try:
            headers = self.get_random_headers()
            response = self.session.get(url, headers=headers, timeout=15, verify=False)
            return self.process_response(response, "直接访问")
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return None
    
    def method_2_with_referer(self, url):
        """方法2: 带Referer访问"""
        print("🔄 方法2: 带Referer访问")
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            headers = self.get_random_headers(referer=base_url)
            response = self.session.get(url, headers=headers, timeout=15, verify=False)
            return self.process_response(response, "带Referer访问")
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return None
    
    def method_3_step_by_step(self, url):
        """方法3: 分步访问模拟真实用户"""
        print("🔄 方法3: 分步访问模拟真实用户")
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # 步骤1: 访问主页
            print("   📍 步骤1: 访问主页")
            headers = self.get_random_headers()
            try:
                home_response = self.session.get(base_url, headers=headers, timeout=10, verify=False)
                time.sleep(random.uniform(2, 4))
                print(f"   ✅ 主页访问成功: {home_response.status_code}")
            except:
                print("   ⚠️ 主页访问失败，继续...")
            
            # 步骤2: 访问robots.txt
            print("   📍 步骤2: 访问robots.txt")
            try:
                robots_headers = self.get_random_headers(referer=base_url)
                robots_response = self.session.get(f"{base_url}/robots.txt", headers=robots_headers, timeout=5, verify=False)
                time.sleep(random.uniform(1, 2))
                print(f"   ✅ robots.txt访问: {robots_response.status_code}")
            except:
                print("   ⚠️ robots.txt访问失败，继续...")
            
            # 步骤3: 访问favicon
            print("   📍 步骤3: 访问favicon")
            try:
                favicon_headers = self.get_random_headers(referer=base_url)
                favicon_response = self.session.get(f"{base_url}/favicon.ico", headers=favicon_headers, timeout=5, verify=False)
                time.sleep(random.uniform(1, 2))
                print(f"   ✅ favicon访问: {favicon_response.status_code}")
            except:
                print("   ⚠️ favicon访问失败，继续...")
            
            # 步骤4: 访问目标页面
            print("   📍 步骤4: 访问目标页面")
            target_headers = self.get_random_headers(referer=base_url)
            target_headers['Cache-Control'] = 'no-cache'
            target_headers['Pragma'] = 'no-cache'
            
            response = self.session.get(url, headers=target_headers, timeout=15, verify=False)
            return self.process_response(response, "分步访问")
            
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return None
    
    def method_4_js_simulation(self, url):
        """方法4: 模拟JavaScript执行"""
        print("🔄 方法4: 模拟JavaScript执行")
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # 先获取页面
            headers = self.get_random_headers(referer=base_url)
            response = self.session.get(url, headers=headers, timeout=15, verify=False)
            
            if response.status_code == 200:
                # 检查是否有main.js
                if 'main.js' in response.text:
                    print("   📍 检测到main.js，尝试获取...")
                    try:
                        js_headers = self.get_random_headers(referer=url)
                        js_headers['Accept'] = 'application/javascript, */*;q=0.1'
                        js_response = self.session.get(f"{base_url}/main.js", headers=js_headers, timeout=10, verify=False)
                        print(f"   ✅ main.js获取: {js_response.status_code}")
                        
                        # 等待一段时间模拟JS执行
                        time.sleep(random.uniform(2, 5))
                        
                        # 再次请求目标页面
                        final_headers = self.get_random_headers(referer=url)
                        final_response = self.session.get(url, headers=final_headers, timeout=15, verify=False)
                        return self.process_response(final_response, "JS模拟执行")
                        
                    except Exception as js_e:
                        print(f"   ⚠️ JS处理失败: {js_e}")
            
            return self.process_response(response, "JS模拟")
            
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return None
    
    def method_5_mobile_ua(self, url):
        """方法5: 使用移动端User-Agent"""
        print("🔄 方法5: 使用移动端User-Agent")
        try:
            mobile_uas = [
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0',
                'Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
            ]
            
            headers = self.base_headers.copy()
            headers['User-Agent'] = random.choice(mobile_uas)
            headers['sec-ch-ua-mobile'] = '?1'
            headers['sec-ch-ua-platform'] = '"Android"'
            
            response = self.session.get(url, headers=headers, timeout=15, verify=False)
            return self.process_response(response, "移动端UA")
            
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return None
    
    def method_6_search_engine_bot(self, url):
        """方法6: 模拟搜索引擎爬虫"""
        print("🔄 方法6: 模拟搜索引擎爬虫")
        try:
            bot_uas = [
                'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
                'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)'
            ]
            
            headers = {
                'User-Agent': random.choice(bot_uas),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = self.session.get(url, headers=headers, timeout=15, verify=False)
            return self.process_response(response, "搜索引擎Bot")
            
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return None
    
    def method_7_curl_simulation(self, url):
        """方法7: 模拟curl请求"""
        print("🔄 方法7: 模拟curl请求")
        try:
            headers = {
                'User-Agent': 'curl/8.4.0',
                'Accept': '*/*',
                'Connection': 'keep-alive'
            }
            
            response = self.session.get(url, headers=headers, timeout=15, verify=False)
            return self.process_response(response, "curl模拟")
            
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return None
    
    def process_response(self, response, method_name):
        """处理响应"""
        if response.status_code == 200:
            # 确保正确解码
            if response.encoding is None:
                response.encoding = response.apparent_encoding or 'utf-8'
            
            content = response.text
            print(f"   ✅ {method_name}成功: 状态码{response.status_code}, 内容长度{len(content)}")
            print(f"   📄 内容预览: {content[:100]}...")
            
            # 检查是否被拦截
            if "Access disabled" in content:
                print(f"   ⚠️ 检测到访问被拒绝")
                return None
            elif len(content) < 200:
                print(f"   ⚠️ 内容太短，可能被拦截")
                return None
            else:
                print(f"   🎉 成功绕过保护!")
                return content
        else:
            print(f"   ❌ {method_name}失败: 状态码{response.status_code}")
            return None
    
    def extract_images_from_content(self, content, base_url):
        """从内容中提取图片"""
        if not content:
            return []
        
        soup = BeautifulSoup(content, 'html.parser')
        image_urls = set()
        
        print("🖼️ 开始提取图片...")
        
        # 方法1: img标签
        img_tags = soup.find_all('img')
        print(f"   📊 找到 {len(img_tags)} 个img标签")
        
        for img in img_tags:
            src = img.get('src') or img.get('data-src') or img.get('data-original') or img.get('data-lazy')
            if src:
                full_url = urljoin(base_url, src)
                if self.is_image_url(full_url):
                    image_urls.add(full_url)
                    print(f"   🖼️ 找到图片: {full_url}")
        
        # 方法2: a标签中的图片链接
        a_tags = soup.find_all('a', href=True)
        image_links = 0
        for a in a_tags:
            href = a['href']
            if self.is_image_url(href):
                full_url = urljoin(base_url, href)
                image_urls.add(full_url)
                image_links += 1
                print(f"   🔗 从链接找到图片: {full_url}")
        
        print(f"   📊 从a标签找到 {image_links} 个图片链接")
        
        # 方法3: 正则表达式搜索
        patterns = [
            r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|gif|bmp|webp|svg)',
            r'["\']([^"\']+\.(?:jpg|jpeg|png|gif|bmp|webp|svg))["\']',
            r'src\s*=\s*["\']([^"\']+\.(?:jpg|jpeg|png|gif|bmp|webp|svg))["\']',
            r'data-src\s*=\s*["\']([^"\']+\.(?:jpg|jpeg|png|gif|bmp|webp|svg))["\']'
        ]
        
        regex_found = 0
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else ''
                if match:
                    full_url = urljoin(base_url, match)
                    if self.is_image_url(full_url) and full_url not in image_urls:
                        image_urls.add(full_url)
                        regex_found += 1
                        print(f"   🔍 正则匹配找到: {full_url}")
        
        print(f"   📊 正则表达式找到 {regex_found} 个新图片")
        
        # 方法4: CSS背景图片
        style_elements = soup.find_all(style=True)
        bg_found = 0
        for element in style_elements:
            style = element.get('style', '')
            bg_matches = re.findall(r'background-image:\s*url\(["\']?([^"\']+)["\']?\)', style)
            for bg_match in bg_matches:
                full_url = urljoin(base_url, bg_match)
                if self.is_image_url(full_url) and full_url not in image_urls:
                    image_urls.add(full_url)
                    bg_found += 1
                    print(f"   🎨 CSS背景图片: {full_url}")
        
        print(f"   📊 CSS背景图片找到 {bg_found} 个")
        
        return list(image_urls)
    
    def is_image_url(self, url):
        """检查是否是图片URL"""
        if not url or len(url) < 5:
            return False
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
        url_lower = url.lower()
        
        # 检查扩展名
        if any(ext in url_lower for ext in image_extensions):
            return True
        
        # 检查关键词
        if any(keyword in url_lower for keyword in ['image', 'img', 'photo', 'pic', 'avatar']):
            return True
        
        return False
    
    def crack_website(self, url):
        """破解网站"""
        print(f"🎯 开始破解网站: {url}")
        print("=" * 60)
        
        # 尝试所有方法
        methods = [
            self.method_1_direct_access,
            self.method_2_with_referer,
            self.method_3_step_by_step,
            self.method_4_js_simulation,
            self.method_5_mobile_ua,
            self.method_6_search_engine_bot,
            self.method_7_curl_simulation
        ]
        
        for i, method in enumerate(methods, 1):
            print(f"\n🔧 尝试方法 {i}/{len(methods)}")
            content = method(url)
            
            if content:
                print(f"🎉 方法 {i} 成功破解!")
                
                # 提取图片
                images = self.extract_images_from_content(content, url)
                
                return {
                    'success': True,
                    'method': f"方法{i}: {method.__name__}",
                    'content_length': len(content),
                    'images': images,
                    'image_count': len(images),
                    'content_preview': content[:500]
                }
            
            # 添加随机延时避免被检测
            time.sleep(random.uniform(1, 3))
        
        print("\n❌ 所有方法都失败了")
        return {
            'success': False,
            'message': '无法破解网站保护',
            'images': []
        }

def main():
    if len(sys.argv) < 2:
        print("使用方法: python3 bypass_crawler.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    crawler = AdvancedBypassCrawler()
    result = crawler.crack_website(url)
    
    print("\n" + "=" * 60)
    print("🏆 最终结果:")
    print(f"   成功: {result['success']}")
    
    if result['success']:
        print(f"   破解方法: {result['method']}")
        print(f"   内容长度: {result['content_length']}")
        print(f"   找到图片: {result['image_count']} 张")
        
        if result['images']:
            print(f"   图片列表:")
            for i, img_url in enumerate(result['images'], 1):
                print(f"      {i}. {img_url}")
        
        print(f"\n   内容预览:")
        print(f"   {result['content_preview']}")
    else:
        print(f"   失败原因: {result['message']}")
    
    # 输出JSON结果
    print(f"\n📋 JSON结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main() 