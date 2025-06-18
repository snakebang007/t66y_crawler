#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows exe 打包脚本
使用 PyInstaller 将 BBS 图片爬虫程序打包成独立的 Windows 可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_spec_file():
    """创建 PyInstaller 规格文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gui', 'gui'),
        ('crawler', 'crawler'),
        ('utils', 'utils'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'requests',
        'bs4',
        'PIL',
        'lxml',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'soupsieve',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BBS图片爬虫',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',
)
'''
    
    with open('bbs_crawler.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 已创建 PyInstaller 规格文件: bbs_crawler.spec")

def build_exe():
    """执行打包过程"""
    print("🔨 开始打包 Windows 可执行文件...")
    
    # 清理之前的构建文件
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("🧹 清理旧的构建目录")
    
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("🧹 清理旧的分发目录")
    
    # 执行 PyInstaller 打包
    try:
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'bbs_crawler.spec']
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ PyInstaller 打包完成")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print("❌ 打包失败:")
        print(e.stderr)
        return False
    
    return True

def create_installer_info():
    """创建安装说明文件"""
    info_content = """# BBS图片爬虫 - Windows 版本

## 安装说明

1. 下载 `BBS图片爬虫.exe` 文件
2. 将文件放置在任意目录（建议创建专门的文件夹）
3. 双击运行即可使用

## 系统要求

- Windows 7 或更高版本
- 64位操作系统
- 至少 100MB 可用磁盘空间

## 使用说明

1. 启动程序后，在输入框中输入 BBS 帖子网址
2. 选择图片保存路径
3. 点击"开始爬取"按钮
4. 等待下载完成，图片会显示在界面中

## 注意事项

- 首次运行可能需要较长时间启动（约10-30秒）
- 程序会自动记住您的设置和保存路径
- 请确保网络连接正常
- 遵守相关网站的使用条款

## 配置文件位置

程序配置保存在：`%USERPROFILE%\\.bbs_image_crawler\\config.json`

## 卸载

直接删除程序文件即可，如需完全清理，可删除配置目录。
"""
    
    with open('Windows安装说明.txt', 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    print("📝 已创建 Windows 安装说明文件")

def main():
    """主函数"""
    print("🚀 BBS图片爬虫 Windows 打包工具")
    print("=" * 50)
    
    # 检查是否在正确的目录
    if not os.path.exists('main.py'):
        print("❌ 错误: 请在项目根目录运行此脚本")
        return
    
    # 创建规格文件
    create_spec_file()
    
    # 执行打包
    if build_exe():
        print("\n🎉 打包成功!")
        print(f"📦 可执行文件位置: {os.path.abspath('dist/BBS图片爬虫.exe')}")
        
        # 创建安装说明
        create_installer_info()
        
        print("\n📋 文件清单:")
        print("  - dist/BBS图片爬虫.exe (主程序)")
        print("  - Windows安装说明.txt (使用说明)")
        
        print("\n💡 提示:")
        print("  1. 将 'dist/BBS图片爬虫.exe' 复制到 Windows 电脑上运行")
        print("  2. 首次运行可能需要较长启动时间")
        print("  3. 程序包含了所有必需的依赖，无需额外安装")
        
    else:
        print("\n❌ 打包失败，请检查错误信息")

if __name__ == "__main__":
    main() 