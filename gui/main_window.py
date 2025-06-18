#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主界面窗口
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QFileDialog, 
                             QScrollArea, QGridLayout, QMessageBox, QProgressBar,
                             QTextEdit, QSplitter, QListWidget, QListWidgetItem,
                             QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QFont, QColor
from crawler.image_crawler import ImageCrawler
from utils.file_manager import FileManager
from utils.config_manager import ConfigManager
from queue import Queue
import threading

class CrawlerThread(QThread):
    """爬虫线程"""
    progress_updated = pyqtSignal(str)  # 进度更新信号
    image_downloaded = pyqtSignal(str)  # 图片下载完成信号
    finished_signal = pyqtSignal(bool, str, str)  # 完成信号 (成功, 消息, URL)
    
    def __init__(self, url, save_path, config_manager):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.config_manager = config_manager
        self.crawler = ImageCrawler()
        
    def run(self):
        """运行爬虫"""
        try:
            self.progress_updated.emit(f"开始处理: {self.url}")
            images = self.crawler.crawl_images(self.url, self.save_path, self.progress_callback)
            self.finished_signal.emit(True, f"成功下载 {len(images)} 张图片", self.url)
        except Exception as e:
            self.finished_signal.emit(False, f"爬取失败: {str(e)}", self.url)
    
    def progress_callback(self, message, image_path=None):
        """进度回调函数"""
        self.progress_updated.emit(message)
        if image_path:
            self.image_downloaded.emit(image_path)

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.save_path = ""
        self.file_manager = FileManager()
        self.config_manager = ConfigManager()
        self.crawler_thread = None
        
        # URL队列管理
        self.url_queue = Queue()
        self.is_processing = False
        self.current_url = ""
        
        # 图片显示状态
        self.show_images = True
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("BBS图片爬虫程序 - 队列版")
        
        # 从配置中获取窗口几何信息
        geometry = self.config_manager.get_window_geometry()
        self.setGeometry(geometry['x'], geometry['y'], geometry['width'], geometry['height'])
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧面板 - URL输入和队列管理
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # 右侧面板 - 图片显示和日志
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 2)
        
    def create_left_panel(self):
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # URL输入区域
        input_group = QGroupBox("URL输入")
        input_group.setFont(QFont("Arial", 12, QFont.Bold))  # 组标题字体
        input_layout = QVBoxLayout(input_group)
        
        # URL输入框
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入BBS帖子网址...")
        self.url_input.setFont(QFont("Arial", 12))  # 调大输入框字体
        self.url_input.setMinimumHeight(35)  # 增加输入框高度
        self.url_input.returnPressed.connect(self.add_url_to_queue)  # 回车添加到队列
        input_layout.addWidget(self.url_input)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("添加到队列")
        self.add_button.setFont(QFont("Arial", 11))  # 调大按钮字体
        self.add_button.setMinimumHeight(35)  # 增加按钮高度
        self.add_button.clicked.connect(self.add_url_to_queue)
        button_layout.addWidget(self.add_button)
        
        self.start_button = QPushButton("开始处理队列")
        self.start_button.setFont(QFont("Arial", 11))
        self.start_button.setMinimumHeight(35)
        self.start_button.clicked.connect(self.start_queue_processing)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("停止处理")
        self.stop_button.setFont(QFont("Arial", 11))
        self.stop_button.setMinimumHeight(35)
        self.stop_button.clicked.connect(self.stop_queue_processing)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        input_layout.addLayout(button_layout)
        layout.addWidget(input_group)
        
        # 路径选择区域
        path_group = QGroupBox("保存设置")
        path_group.setFont(QFont("Arial", 12, QFont.Bold))
        path_layout = QVBoxLayout(path_group)
        
        path_button_layout = QHBoxLayout()
        self.path_button = QPushButton("选择保存路径")
        self.path_button.setFont(QFont("Arial", 11))
        self.path_button.setMinimumHeight(35)
        self.path_button.clicked.connect(self.select_save_path)
        path_button_layout.addWidget(self.path_button)
        path_layout.addLayout(path_button_layout)
        
        self.path_label = QLabel("未选择保存路径")
        self.path_label.setFont(QFont("Arial", 11))  # 调大路径标签字体
        self.path_label.setStyleSheet("color: gray;")
        self.path_label.setWordWrap(True)
        path_layout.addWidget(self.path_label)
        
        layout.addWidget(path_group)
        
        # 显示设置区域
        display_group = QGroupBox("显示设置")
        display_group.setFont(QFont("Arial", 12, QFont.Bold))
        display_layout = QVBoxLayout(display_group)
        
        # 图片显示切换按钮
        self.show_images_checkbox = QCheckBox("显示下载的图片")
        self.show_images_checkbox.setFont(QFont("Arial", 11))  # 调大复选框字体
        self.show_images_checkbox.setChecked(True)  # 默认显示
        self.show_images_checkbox.stateChanged.connect(self.toggle_image_display)
        display_layout.addWidget(self.show_images_checkbox)
        
        # 添加说明标签
        info_label = QLabel("取消勾选可隐藏图片网格，\n提高处理性能")
        info_label.setFont(QFont("Arial", 10))  # 调大说明文字
        info_label.setStyleSheet("color: gray;")
        info_label.setWordWrap(True)
        display_layout.addWidget(info_label)
        
        layout.addWidget(display_group)
        
        # URL队列显示
        queue_group = QGroupBox("URL队列")
        queue_group.setFont(QFont("Arial", 12, QFont.Bold))
        queue_layout = QVBoxLayout(queue_group)
        
        # 队列状态
        self.queue_status_label = QLabel("队列状态: 空闲")
        self.queue_status_label.setFont(QFont("Arial", 11))  # 调大状态标签字体
        queue_layout.addWidget(self.queue_status_label)
        
        # 队列列表
        self.queue_list = QListWidget()
        self.queue_list.setFont(QFont("Arial", 10))  # 调大列表字体
        self.queue_list.setMaximumHeight(200)
        queue_layout.addWidget(self.queue_list)
        
        # 队列操作按钮
        queue_button_layout = QHBoxLayout()
        
        self.clear_queue_button = QPushButton("清空队列")
        self.clear_queue_button.setFont(QFont("Arial", 10))
        self.clear_queue_button.setMinimumHeight(30)
        self.clear_queue_button.clicked.connect(self.clear_queue)
        queue_button_layout.addWidget(self.clear_queue_button)
        
        self.remove_selected_button = QPushButton("删除选中")
        self.remove_selected_button.setFont(QFont("Arial", 10))
        self.remove_selected_button.setMinimumHeight(30)
        self.remove_selected_button.clicked.connect(self.remove_selected_url)
        queue_button_layout.addWidget(self.remove_selected_button)
        
        queue_layout.addLayout(queue_button_layout)
        layout.addWidget(queue_group)
        
        # 进度显示
        progress_group = QGroupBox("处理进度")
        progress_group.setFont(QFont("Arial", 12, QFont.Bold))
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)  # 增加进度条高度
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("准备就绪")
        self.status_label.setFont(QFont("Arial", 11))  # 调大状态字体
        self.status_label.setWordWrap(True)
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        return panel
    
    def create_right_panel(self):
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 创建分割器
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        
        # 图片显示区域
        self.image_group = QGroupBox("下载的图片")
        self.image_group.setFont(QFont("Arial", 12, QFont.Bold))
        image_layout = QVBoxLayout(self.image_group)
        
        # 图片统计信息
        self.image_count_label = QLabel("已下载图片: 0 张")
        self.image_count_label.setFont(QFont("Arial", 11))  # 调大计数标签字体
        self.image_count_label.setStyleSheet("color: gray;")
        image_layout.addWidget(self.image_count_label)
        
        self.image_scroll_area = self.create_image_area()
        image_layout.addWidget(self.image_scroll_area)
        
        splitter.addWidget(self.image_group)
        
        # 日志区域
        log_group = QGroupBox("操作日志")
        log_group.setFont(QFont("Arial", 12, QFont.Bold))
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setFont(QFont("Consolas", 11))  # 调大日志字体
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        splitter.addWidget(log_group)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        
        return panel
    
    def create_image_area(self):
        """创建图片显示区域"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        
        # 创建图片容器
        self.image_widget = QWidget()
        self.image_layout = QGridLayout(self.image_widget)
        self.image_layout.setSpacing(10)
        
        scroll_area.setWidget(self.image_widget)
        return scroll_area
    
    def toggle_image_display(self, state):
        """切换图片显示状态"""
        self.show_images = state == Qt.Checked
        
        if self.show_images:
            # 显示图片区域
            self.image_group.setVisible(True)
            self.log_message("✅ 已开启图片显示")
        else:
            # 隐藏图片区域
            self.image_group.setVisible(False)
            self.log_message("❌ 已关闭图片显示（提高性能）")
        
        # 保存设置到配置文件
        self.config_manager.config['show_images'] = self.show_images
        self.config_manager.save_config()
    
    def load_settings(self):
        """加载设置"""
        # 加载上次保存的路径
        last_path = self.config_manager.get_last_save_path()
        if last_path:
            self.save_path = last_path
            self.path_label.setText(f"保存路径: {last_path}")
            self.path_label.setStyleSheet("color: black;")
            self.log_message(f"已加载上次保存路径: {last_path}")
        else:
            self.log_message("首次使用，请选择保存路径")
        
        # 加载图片显示设置
        show_images = self.config_manager.config.get('show_images', True)
        self.show_images = show_images
        self.show_images_checkbox.setChecked(show_images)
        
        if not show_images:
            self.image_group.setVisible(False)
            self.log_message("已加载设置: 图片显示已关闭")
    
    def add_url_to_queue(self):
        """添加URL到队列"""
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "警告", "请输入网址!")
            return
        
        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, "警告", "请输入有效的网址（以http://或https://开头）!")
            return
        
        # 检查是否已存在
        for i in range(self.queue_list.count()):
            if self.queue_list.item(i).text() == url:
                QMessageBox.information(self, "提示", "该URL已在队列中!")
                return
        
        # 添加到队列
        self.url_queue.put(url)
        
        # 添加到显示列表
        item = QListWidgetItem(url)
        item.setToolTip(url)
        self.queue_list.addItem(item)
        
        # 清空输入框
        self.url_input.clear()
        
        # 更新状态
        self.update_queue_status()
        self.log_message(f"已添加到队列: {url}")
        
        # 如果没有在处理，自动开始处理
        if not self.is_processing:
            self.start_queue_processing()
    
    def start_queue_processing(self):
        """开始处理队列"""
        if not self.save_path:
            QMessageBox.warning(self, "警告", "请先选择保存路径!")
            return
        
        if self.url_queue.empty():
            QMessageBox.information(self, "提示", "队列为空，请先添加URL!")
            return
        
        if self.is_processing:
            return
        
        self.is_processing = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        self.process_next_url()
    
    def process_next_url(self):
        """处理队列中的下一个URL"""
        if self.url_queue.empty() or not self.is_processing:
            self.finish_queue_processing()
            return
        
        # 获取下一个URL
        self.current_url = self.url_queue.get()
        
        # 从显示列表中移除第一个项目并标记为正在处理
        if self.queue_list.count() > 0:
            item = self.queue_list.item(0)
            item.setText(f"🔄 正在处理: {self.current_url}")
            item.setBackground(QColor(255, 255, 0, 50))  # 黄色背景
        
        # 更新状态
        self.update_queue_status()
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        
        # 清空之前的图片（可选，如果想保留所有图片可以注释掉）
        # self.clear_images()
        
        # 创建并启动爬虫线程
        self.crawler_thread = CrawlerThread(self.current_url, self.save_path, self.config_manager)
        self.crawler_thread.progress_updated.connect(self.update_progress)
        self.crawler_thread.image_downloaded.connect(self.add_image)
        self.crawler_thread.finished_signal.connect(self.url_processing_finished)
        self.crawler_thread.start()
        
        self.log_message(f"开始处理: {self.current_url}")
    
    def url_processing_finished(self, success, message, url):
        """单个URL处理完成"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        # 从显示列表中移除已完成的项目
        if self.queue_list.count() > 0:
            item = self.queue_list.takeItem(0)
            del item
        
        # 记录结果
        status = "✅ 成功" if success else "❌ 失败"
        self.log_message(f"{status}: {url} - {message}")
        
        # 更新状态
        self.update_queue_status()
        
        # 处理下一个URL
        QTimer.singleShot(1000, self.process_next_url)  # 延迟1秒处理下一个
    
    def stop_queue_processing(self):
        """停止处理队列"""
        self.is_processing = False
        
        if self.crawler_thread and self.crawler_thread.isRunning():
            self.crawler_thread.terminate()
            self.crawler_thread.wait()
        
        self.finish_queue_processing()
        self.log_message("用户停止了队列处理")
    
    def finish_queue_processing(self):
        """完成队列处理"""
        self.is_processing = False
        self.current_url = ""
        
        # 恢复按钮状态
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        # 更新状态
        self.update_queue_status()
        
        if self.url_queue.empty():
            self.status_label.setText("队列处理完成")
            self.log_message("🎉 所有URL处理完成!")
            QMessageBox.information(self, "完成", "所有URL处理完成!")
        else:
            self.status_label.setText("队列处理已停止")
    
    def clear_queue(self):
        """清空队列"""
        if self.is_processing:
            reply = QMessageBox.question(
                self, 
                '确认清空', 
                '正在处理队列，确定要清空吗？这将停止当前处理。',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
            self.stop_queue_processing()
        
        # 清空队列
        while not self.url_queue.empty():
            self.url_queue.get()
        
        # 清空显示列表
        self.queue_list.clear()
        
        # 更新状态
        self.update_queue_status()
        self.log_message("已清空队列")
    
    def remove_selected_url(self):
        """删除选中的URL"""
        current_item = self.queue_list.currentItem()
        if not current_item:
            QMessageBox.information(self, "提示", "请先选择要删除的URL!")
            return
        
        if current_item.text().startswith("🔄 正在处理:"):
            QMessageBox.warning(self, "警告", "无法删除正在处理的URL!")
            return
        
        # 从队列中移除（这里需要重建队列，因为Queue不支持随机删除）
        url_to_remove = current_item.text()
        temp_urls = []
        
        while not self.url_queue.empty():
            url = self.url_queue.get()
            if url != url_to_remove:
                temp_urls.append(url)
        
        for url in temp_urls:
            self.url_queue.put(url)
        
        # 从显示列表中移除
        row = self.queue_list.row(current_item)
        self.queue_list.takeItem(row)
        
        # 更新状态
        self.update_queue_status()
        self.log_message(f"已删除: {url_to_remove}")
    
    def update_queue_status(self):
        """更新队列状态"""
        queue_size = self.url_queue.qsize()
        
        if self.is_processing:
            if self.current_url:
                self.queue_status_label.setText(f"正在处理，队列剩余: {queue_size}")
            else:
                self.queue_status_label.setText(f"处理中，队列剩余: {queue_size}")
        else:
            if queue_size > 0:
                self.queue_status_label.setText(f"队列等待中: {queue_size} 个URL")
            else:
                self.queue_status_label.setText("队列状态: 空闲")
    
    def select_save_path(self):
        """选择保存路径"""
        # 如果有上次的路径，从那里开始选择
        start_dir = self.save_path if self.save_path else os.path.expanduser("~")
        
        path = QFileDialog.getExistingDirectory(
            self, 
            "选择图片保存路径", 
            start_dir
        )
        
        if path:
            self.save_path = path
            self.path_label.setText(f"保存路径: {path}")
            self.path_label.setStyleSheet("color: black;")
            
            # 保存到配置文件
            self.config_manager.set_last_save_path(path)
            
            self.log_message(f"已选择保存路径: {path}")
    
    def update_progress(self, message):
        """更新进度"""
        self.status_label.setText(message)
        self.log_message(message)
    
    def add_image(self, image_path):
        """添加图片到显示区域"""
        if not os.path.exists(image_path):
            return
        
        # 更新图片计数
        current_count = self.image_layout.count()
        self.image_count_label.setText(f"已下载图片: {current_count + 1} 张")
        
        # 如果图片显示被关闭，只更新计数，不显示图片
        if not self.show_images:
            return
            
        try:
            # 创建图片标签
            image_label = QLabel()
            pixmap = QPixmap(image_path)
            
            # 缩放图片
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("border: 1px solid gray; margin: 2px;")
            image_label.setToolTip(os.path.basename(image_path))
            
            # 添加到网格布局
            row = self.image_layout.count() // 5
            col = self.image_layout.count() % 5
            self.image_layout.addWidget(image_label, row, col)
            
        except Exception as e:
            self.log_message(f"显示图片失败: {str(e)}")
    
    def clear_images(self):
        """清空图片显示"""
        while self.image_layout.count():
            child = self.image_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 重置图片计数
        self.image_count_label.setText("已下载图片: 0 张")
    
    def log_message(self, message):
        """记录日志消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 如果正在处理，询问用户
        if self.is_processing:
            reply = QMessageBox.question(
                self, 
                '确认退出', 
                '正在处理队列，确定要退出吗？',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
            
            # 停止处理
            self.stop_queue_processing()
        
        # 保存窗口几何信息
        geometry = self.geometry()
        self.config_manager.set_window_geometry(
            geometry.x(), 
            geometry.y(), 
            geometry.width(), 
            geometry.height()
        )
        
        event.accept() 