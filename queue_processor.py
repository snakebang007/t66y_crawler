#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
队列处理器 - 从Redis队列中取出任务并执行
"""

import os
import sys
import json
import time
import redis
import logging
from datetime import datetime
from qinglong_crawler import QinglongCrawler

class QueueProcessor:
    """队列处理器"""
    
    def __init__(self):
        self.setup_logging()
        self.load_config()
        self.setup_redis()
        self.crawler = QinglongCrawler()
        
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """加载配置"""
        self.config = {
            # Redis配置
            'REDIS_HOST': os.getenv('REDIS_HOST', 'localhost'),
            'REDIS_PORT': int(os.getenv('REDIS_PORT', '6379')),
            'REDIS_PASSWORD': os.getenv('REDIS_PASSWORD', ''),
            'REDIS_DB': int(os.getenv('REDIS_DB', '0')),
            
            # 处理配置
            'QUEUE_NAME': os.getenv('QUEUE_NAME', 'bbs_crawler_queue'),
            'PROCESS_INTERVAL': int(os.getenv('PROCESS_INTERVAL', '5')),  # 秒
            'MAX_RETRIES': int(os.getenv('MAX_RETRIES', '3')),
            'RETRY_DELAY': int(os.getenv('RETRY_DELAY', '60')),  # 秒
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
            self.logger.info("Redis连接成功")
        except Exception as e:
            self.logger.error(f"Redis连接失败: {e}")
            sys.exit(1)
    
    def process_queue(self):
        """处理队列"""
        self.logger.info("开始处理队列...")
        
        while True:
            try:
                # 从队列中取出任务（阻塞式，超时5秒）
                result = self.redis_client.brpop(self.config['QUEUE_NAME'], timeout=5)
                
                if result:
                    queue_name, task_json = result
                    self.process_task(task_json)
                else:
                    # 队列为空，等待一段时间
                    time.sleep(self.config['PROCESS_INTERVAL'])
                    
            except KeyboardInterrupt:
                self.logger.info("收到中断信号，停止处理队列")
                break
            except Exception as e:
                self.logger.error(f"处理队列异常: {e}")
                time.sleep(self.config['PROCESS_INTERVAL'])
    
    def process_task(self, task_json):
        """处理单个任务"""
        try:
            # 解析任务数据
            task_data = json.loads(task_json)
            url = task_data.get('url')
            source = task_data.get('source', 'unknown')
            timestamp = task_data.get('timestamp')
            retry_count = task_data.get('retry_count', 0)
            
            self.logger.info(f"处理任务: {url} (来源: {source}, 重试: {retry_count})")
            
            # 执行爬虫任务
            result = self.crawler.crawl_images(url)
            
            if result['success']:
                self.logger.info(f"任务完成: {result['message']}")
                
                # 记录成功任务
                self.record_task_result(task_data, result, 'success')
                
            else:
                self.logger.error(f"任务失败: {result['message']}")
                
                # 检查是否需要重试
                if retry_count < self.config['MAX_RETRIES']:
                    self.retry_task(task_data, retry_count + 1)
                else:
                    self.logger.error(f"任务达到最大重试次数，放弃: {url}")
                    self.record_task_result(task_data, result, 'failed')
                    
        except Exception as e:
            self.logger.error(f"处理任务异常: {e}")
            
            # 尝试重新解析任务数据进行重试
            try:
                task_data = json.loads(task_json)
                retry_count = task_data.get('retry_count', 0)
                
                if retry_count < self.config['MAX_RETRIES']:
                    self.retry_task(task_data, retry_count + 1)
                else:
                    self.record_task_result(task_data, {'success': False, 'message': str(e)}, 'error')
            except:
                self.logger.error(f"无法解析任务数据: {task_json}")
    
    def retry_task(self, task_data, retry_count):
        """重试任务"""
        task_data['retry_count'] = retry_count
        task_data['retry_timestamp'] = datetime.now().isoformat()
        
        # 延迟重试
        delay = self.config['RETRY_DELAY'] * retry_count
        self.logger.info(f"任务将在 {delay} 秒后重试: {task_data['url']}")
        
        # 添加到延迟队列（这里简化处理，直接延迟后重新加入队列）
        time.sleep(delay)
        
        try:
            self.redis_client.lpush(self.config['QUEUE_NAME'], json.dumps(task_data))
            self.logger.info(f"任务已重新加入队列: {task_data['url']}")
        except Exception as e:
            self.logger.error(f"重新加入队列失败: {e}")
    
    def record_task_result(self, task_data, result, status):
        """记录任务结果"""
        try:
            # 创建结果记录
            record = {
                'task': task_data,
                'result': result,
                'status': status,
                'completed_at': datetime.now().isoformat()
            }
            
            # 保存到Redis（使用有序集合，按时间排序）
            score = int(time.time())
            self.redis_client.zadd('bbs_crawler_results', {json.dumps(record): score})
            
            # 只保留最近1000条记录
            self.redis_client.zremrangebyrank('bbs_crawler_results', 0, -1001)
            
            self.logger.info(f"任务结果已记录: {status}")
            
        except Exception as e:
            self.logger.error(f"记录任务结果失败: {e}")
    
    def get_queue_status(self):
        """获取队列状态"""
        try:
            queue_length = self.redis_client.llen(self.config['QUEUE_NAME'])
            result_count = self.redis_client.zcard('bbs_crawler_results')
            
            return {
                'queue_length': queue_length,
                'result_count': result_count,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"获取队列状态失败: {e}")
            return None
    
    def clear_queue(self):
        """清空队列"""
        try:
            cleared = self.redis_client.delete(self.config['QUEUE_NAME'])
            self.logger.info(f"队列已清空，删除了 {cleared} 个键")
            return cleared
        except Exception as e:
            self.logger.error(f"清空队列失败: {e}")
            return 0

def main():
    """主函数"""
    processor = QueueProcessor()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'status':
            # 显示队列状态
            status = processor.get_queue_status()
            if status:
                print(json.dumps(status, ensure_ascii=False, indent=2))
            else:
                print("无法获取队列状态")
            return
            
        elif command == 'clear':
            # 清空队列
            cleared = processor.clear_queue()
            print(f"队列已清空，删除了 {cleared} 个任务")
            return
            
        elif command == 'help':
            print("队列处理器使用说明:")
            print("  python3 queue_processor.py          - 启动队列处理器")
            print("  python3 queue_processor.py status   - 查看队列状态")
            print("  python3 queue_processor.py clear    - 清空队列")
            print("  python3 queue_processor.py help     - 显示帮助")
            return
    
    # 启动队列处理
    try:
        processor.logger.info("队列处理器启动")
        processor.logger.info(f"Redis: {processor.config['REDIS_HOST']}:{processor.config['REDIS_PORT']}")
        processor.logger.info(f"队列名称: {processor.config['QUEUE_NAME']}")
        processor.logger.info(f"处理间隔: {processor.config['PROCESS_INTERVAL']}秒")
        processor.logger.info(f"最大重试: {processor.config['MAX_RETRIES']}次")
        
        # 显示初始状态
        status = processor.get_queue_status()
        if status:
            processor.logger.info(f"当前队列长度: {status['queue_length']}")
            processor.logger.info(f"历史结果数: {status['result_count']}")
        
        # 开始处理队列
        processor.process_queue()
        
    except KeyboardInterrupt:
        processor.logger.info("队列处理器已停止")
    except Exception as e:
        processor.logger.error(f"队列处理器异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 