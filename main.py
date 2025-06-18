#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BBS图片爬虫程序主入口
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("BBS图片爬虫")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("ImageCrawler")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 