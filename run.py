#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BBS图片爬虫程序启动脚本
"""

if __name__ == "__main__":
    try:
        from main import main
        main()
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保安装了所有依赖包:")
        print("pip3 install PyQt5 requests beautifulsoup4 Pillow lxml")
    except Exception as e:
        print(f"程序运行错误: {e}")
        import traceback
        traceback.print_exc() 