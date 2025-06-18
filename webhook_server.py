#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook服务器 - 接收URL并触发青龙面板任务
"""

import os
import json
import time
import requests
from datetime import datetime
from flask import Flask, request, jsonify
import logging
import hashlib
import hmac
import redis
from urllib.parse import urlparse

app = Flask(__name__)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebhookServer:
    """Webhook服务器"""
    
    def __init__(self):
        self.load_config()
        self.setup_redis()
        
    def load_config(self):
        """加载配置"""
        self.config = {
            # 服务器配置
            'HOST': os.getenv('WEBHOOK_HOST', '0.0.0.0'),
            'PORT': int(os.getenv('WEBHOOK_PORT', '5000')),
            'SECRET_KEY': os.getenv('WEBHOOK_SECRET', 'your-secret-key'),
            
            # 青龙面板配置
            'QINGLONG_URL': os.getenv('QINGLONG_URL', 'http://localhost:5700'),
            'QINGLONG_CLIENT_ID': os.getenv('QINGLONG_CLIENT_ID', ''),
            'QINGLONG_CLIENT_SECRET': os.getenv('QINGLONG_CLIENT_SECRET', ''),
            
            # Redis配置（任务队列）
            'REDIS_HOST': os.getenv('REDIS_HOST', 'localhost'),
            'REDIS_PORT': int(os.getenv('REDIS_PORT', '6379')),
            'REDIS_PASSWORD': os.getenv('REDIS_PASSWORD', ''),
            'REDIS_DB': int(os.getenv('REDIS_DB', '0')),
            
            # 消息推送配置
            'PUSH_PLUS_TOKEN': os.getenv('PUSH_PLUS_TOKEN', ''),
            'BARK_URL': os.getenv('BARK_URL', ''),
        }
        
    def setup_redis(self):
        """设置Redis连接"""
        try:
            self.redis_client = redis.Redis(
                host=self.config['REDIS_HOST'],
                port=self.config['REDIS_PORT'],
                password=self.config['REDIS_PASSWORD'] if self.config['REDIS_PASSWORD'] else None,
                db=self.config['REDIS_DB'],
                decode_responses=True
            )
            # 测试连接
            self.redis_client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}")
            self.redis_client = None
    
    def verify_signature(self, payload, signature):
        """验证签名"""
        if not self.config['SECRET_KEY']:
            return True
        
        expected_signature = hmac.new(
            self.config['SECRET_KEY'].encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    def is_valid_url(self, url):
        """验证URL格式"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def add_to_queue(self, url, source='webhook'):
        """添加URL到队列"""
        task_data = {
            'url': url,
            'source': source,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        if self.redis_client:
            try:
                # 添加到Redis队列
                self.redis_client.lpush('bbs_crawler_queue', json.dumps(task_data))
                logger.info(f"任务已添加到队列: {url}")
                return True
            except Exception as e:
                logger.error(f"添加到队列失败: {e}")
        
        # 如果Redis不可用，直接触发任务
        return self.trigger_qinglong_task(url)
    
    def trigger_qinglong_task(self, url):
        """触发青龙面板任务"""
        try:
            # 获取青龙面板访问令牌
            token = self.get_qinglong_token()
            if not token:
                logger.error("无法获取青龙面板访问令牌")
                return False
            
            # 创建任务
            task_data = {
                "name": f"BBS图片爬虫_{datetime.now().strftime('%m%d_%H%M')}",
                "command": f"cd /ql/data/scripts && python3 qinglong_crawler.py '{url}'",
                "schedule": "",  # 立即执行
                "saved": True
            }
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.config['QINGLONG_URL']}/open/crons",
                json=task_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"青龙任务创建成功: {url}")
                return True
            else:
                logger.error(f"青龙任务创建失败: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"触发青龙任务失败: {e}")
            return False
    
    def get_qinglong_token(self):
        """获取青龙面板访问令牌"""
        try:
            auth_data = {
                "client_id": self.config['QINGLONG_CLIENT_ID'],
                "client_secret": self.config['QINGLONG_CLIENT_SECRET']
            }
            
            response = requests.post(
                f"{self.config['QINGLONG_URL']}/open/auth/token",
                json=auth_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('data', {}).get('token')
            else:
                logger.error(f"获取令牌失败: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"获取令牌异常: {e}")
            return None
    
    def send_notification(self, message, title="BBS爬虫通知"):
        """发送通知"""
        # Push Plus
        if self.config['PUSH_PLUS_TOKEN']:
            try:
                url = "http://www.pushplus.plus/send"
                data = {
                    "token": self.config['PUSH_PLUS_TOKEN'],
                    "title": title,
                    "content": message
                }
                requests.post(url, json=data, timeout=10)
                logger.info("Push Plus通知发送成功")
            except Exception as e:
                logger.error(f"Push Plus通知发送失败: {e}")
        
        # Bark
        if self.config['BARK_URL']:
            try:
                url = f"{self.config['BARK_URL']}/{title}/{message}"
                requests.get(url, timeout=10)
                logger.info("Bark通知发送成功")
            except Exception as e:
                logger.error(f"Bark通知发送失败: {e}")

# 创建服务器实例
webhook_server = WebhookServer()

@app.route('/webhook/bbs', methods=['POST'])
def webhook_bbs():
    """接收BBS URL的Webhook"""
    try:
        # 获取请求数据
        payload = request.get_data()
        signature = request.headers.get('X-Hub-Signature-256', '')
        
        # 验证签名
        if not webhook_server.verify_signature(payload, signature):
            logger.warning("签名验证失败")
            return jsonify({'error': '签名验证失败'}), 401
        
        # 解析JSON数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的JSON数据'}), 400
        
        url = data.get('url', '').strip()
        source = data.get('source', 'webhook')
        
        if not url:
            return jsonify({'error': 'URL不能为空'}), 400
        
        if not webhook_server.is_valid_url(url):
            return jsonify({'error': '无效的URL格式'}), 400
        
        # 添加到队列
        success = webhook_server.add_to_queue(url, source)
        
        if success:
            message = f"任务已接收: {url}"
            webhook_server.send_notification(message, "BBS爬虫任务接收")
            logger.info(message)
            
            return jsonify({
                'success': True,
                'message': '任务已添加到队列',
                'url': url,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': '任务添加失败'}), 500
            
    except Exception as e:
        logger.error(f"Webhook处理失败: {e}")
        return jsonify({'error': '服务器内部错误'}), 500

@app.route('/webhook/status', methods=['GET'])
def webhook_status():
    """获取服务状态"""
    status = {
        'service': 'BBS图片爬虫Webhook服务',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'redis_connected': webhook_server.redis_client is not None,
        'qinglong_configured': bool(webhook_server.config['QINGLONG_CLIENT_ID'])
    }
    
    if webhook_server.redis_client:
        try:
            queue_length = webhook_server.redis_client.llen('bbs_crawler_queue')
            status['queue_length'] = queue_length
        except:
            status['queue_length'] = 'unknown'
    
    return jsonify(status)

@app.route('/webhook/queue', methods=['GET'])
def webhook_queue():
    """获取队列状态"""
    if not webhook_server.redis_client:
        return jsonify({'error': 'Redis未连接'}), 500
    
    try:
        # 获取队列长度
        queue_length = webhook_server.redis_client.llen('bbs_crawler_queue')
        
        # 获取最近的任务（最多10个）
        recent_tasks = []
        tasks = webhook_server.redis_client.lrange('bbs_crawler_queue', 0, 9)
        
        for task_json in tasks:
            try:
                task = json.loads(task_json)
                recent_tasks.append(task)
            except:
                continue
        
        return jsonify({
            'queue_length': queue_length,
            'recent_tasks': recent_tasks
        })
        
    except Exception as e:
        logger.error(f"获取队列状态失败: {e}")
        return jsonify({'error': '获取队列状态失败'}), 500

@app.route('/webhook/test', methods=['POST'])
def webhook_test():
    """测试接口"""
    test_url = "https://example.com/test"
    
    success = webhook_server.add_to_queue(test_url, 'test')
    
    return jsonify({
        'success': success,
        'message': '测试任务已提交' if success else '测试任务提交失败',
        'test_url': test_url
    })

if __name__ == '__main__':
    logger.info("启动BBS图片爬虫Webhook服务...")
    logger.info(f"服务地址: http://{webhook_server.config['HOST']}:{webhook_server.config['PORT']}")
    logger.info("接口说明:")
    logger.info("  POST /webhook/bbs - 接收BBS URL")
    logger.info("  GET  /webhook/status - 获取服务状态")
    logger.info("  GET  /webhook/queue - 获取队列状态")
    logger.info("  POST /webhook/test - 测试接口")
    
    app.run(
        host=webhook_server.config['HOST'],
        port=webhook_server.config['PORT'],
        debug=False
    ) 