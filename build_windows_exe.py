#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows exe 跨平台打包脚本
使用 PyInstaller 将 BBS 图片爬虫程序打包成独立的 Windows 可执行文件

注意：此脚本在 macOS/Linux 上运行，生成的是针对当前平台的可执行文件
要生成 Windows exe，需要在 Windows 系统上运行，或使用 Docker/虚拟机
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def create_windows_spec():
    """创建针对 Windows 的 PyInstaller 规格文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
# Windows 专用打包配置

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
        'PyQt5.sip',
        'requests',
        'bs4',
        'PIL',
        'PIL._tkinter_finder',
        'lxml',
        'lxml.etree',
        'lxml._elementpath',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'soupsieve',
        'json',
        'pathlib',
        'threading',
        'queue',
        'time',
        're',
        'os',
        'sys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'jupyter',
        'IPython',
    ],
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
    icon='app_icon.ico' if os.path.exists('app_icon.ico') else None,
    version_file=None,
)
'''
    
    with open('windows_build.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 已创建 Windows PyInstaller 规格文件: windows_build.spec")

def create_batch_script():
    """创建 Windows 批处理打包脚本"""
    batch_content = '''@echo off
chcp 65001 >nul
echo 🚀 BBS图片爬虫 Windows 打包工具
echo ==================================================

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

REM 检查必要文件
if not exist "main.py" (
    echo ❌ 错误: 未找到 main.py，请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 安装 PyInstaller
echo 📦 安装 PyInstaller...
pip install pyinstaller

REM 清理旧文件
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM 执行打包
echo 🔨 开始打包 Windows 可执行文件...
pyinstaller --clean windows_build.spec

REM 检查打包结果
if exist "dist\\BBS图片爬虫.exe" (
    echo.
    echo 🎉 打包成功!
    echo 📦 可执行文件位置: dist\\BBS图片爬虫.exe
    echo.
    echo 💡 提示:
    echo   1. 程序已打包完成，可以直接运行
    echo   2. 首次运行可能需要较长启动时间
    echo   3. 程序包含了所有必需的依赖
    echo.
) else (
    echo ❌ 打包失败，请检查错误信息
)

pause
'''
    
    with open('build_windows.bat', 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print("✅ 已创建 Windows 批处理脚本: build_windows.bat")

def create_docker_solution():
    """创建 Docker 跨平台打包解决方案"""
    dockerfile_content = '''# 使用 Windows 容器来构建 Windows exe
# 注意：需要 Docker Desktop 支持 Windows 容器

FROM python:3.9-windowsservercore

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN pip install -r requirements.txt
RUN pip install pyinstaller

# 执行打包
RUN pyinstaller --clean windows_build.spec

# 输出文件到 /output
CMD ["cmd", "/c", "copy dist\\*.exe C:\\output\\"]
'''
    
    with open('Dockerfile.windows', 'w', encoding='utf-8') as f:
        f.write(dockerfile_content)
    
    docker_compose_content = '''version: '3.8'
services:
  windows-builder:
    build:
      context: .
      dockerfile: Dockerfile.windows
    volumes:
      - ./output:/output
    platform: windows/amd64
'''
    
    with open('docker-compose.windows.yml', 'w', encoding='utf-8') as f:
        f.write(docker_compose_content)
    
    print("✅ 已创建 Docker 跨平台打包配置")

def create_comprehensive_guide():
    """创建完整的打包指南"""
    guide_content = '''# BBS图片爬虫 Windows 打包指南

## 🎯 目标
将 Python 程序打包成独立的 Windows 可执行文件（.exe），无需在目标机器上安装 Python。

## 📋 打包方案

### 方案一：在 Windows 系统上直接打包（推荐）

1. **准备 Windows 环境**
   - Windows 7/8/10/11 系统
   - Python 3.7+ 已安装
   - 所有项目依赖已安装

2. **执行打包**
   ```cmd
   # 双击运行批处理文件
   build_windows.bat
   
   # 或手动执行
   pip install pyinstaller
   pyinstaller --clean windows_build.spec
   ```

3. **获取结果**
   - 可执行文件：`dist/BBS图片爬虫.exe`
   - 文件大小：约 30-50 MB
   - 包含所有依赖，可独立运行

### 方案二：使用虚拟机

1. **安装虚拟机软件**
   - VMware Workstation
   - VirtualBox
   - Parallels Desktop (macOS)

2. **创建 Windows 虚拟机**
   - 安装 Windows 10/11
   - 安装 Python 3.9+
   - 配置开发环境

3. **在虚拟机中打包**
   - 复制项目文件到虚拟机
   - 运行打包脚本
   - 复制生成的 exe 文件

### 方案三：使用 GitHub Actions（自动化）

创建 `.github/workflows/build-windows.yml`：

```yaml
name: Build Windows EXE

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: |
        python create_icon.py
        pyinstaller --clean windows_build.spec
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: BBS图片爬虫-Windows
        path: dist/BBS图片爬虫.exe
```

## 🔧 打包配置说明

### PyInstaller 参数解释

- `--onefile`: 打包成单个 exe 文件
- `--windowed`: 无控制台窗口（GUI 程序）
- `--icon`: 指定程序图标
- `--name`: 指定程序名称
- `--clean`: 清理临时文件

### 隐藏导入模块

程序会自动包含以下模块：
- PyQt5 相关模块
- 网络请求模块（requests, urllib3）
- HTML 解析模块（bs4, lxml）
- 图像处理模块（PIL）

### 排除不必要的模块

为减小文件大小，排除了：
- tkinter (GUI 框架)
- matplotlib (绘图)
- numpy (数值计算)
- pandas (数据分析)

## 📦 打包结果

### 文件信息
- **文件名**: BBS图片爬虫.exe
- **大小**: 约 30-50 MB
- **启动时间**: 首次 10-30 秒，后续 3-10 秒
- **系统要求**: Windows 7+ (64位)

### 功能特性
- ✅ 完全独立运行，无需安装 Python
- ✅ 包含所有必需的依赖库
- ✅ 支持中文界面和文件名
- ✅ 自动记忆用户设置
- ✅ 网络功能正常

## 🚀 分发建议

### 打包分发
1. 创建安装包文件夹
2. 包含以下文件：
   - `BBS图片爬虫.exe` (主程序)
   - `Windows安装说明.txt` (使用说明)
   - `LICENSE` (许可证)

### 压缩分发
```bash
# 创建 ZIP 压缩包
zip -r "BBS图片爬虫-v1.0-Windows.zip" dist/BBS图片爬虫.exe Windows安装说明.txt LICENSE
```

### 在线分发
- 上传到 GitHub Releases
- 使用云存储服务
- 创建下载页面

## ⚠️ 注意事项

1. **杀毒软件**: 某些杀毒软件可能误报，需要添加白名单
2. **首次启动**: 程序首次启动较慢，属于正常现象
3. **文件大小**: exe 文件较大，因为包含了完整的 Python 环境
4. **系统兼容**: 建议在目标系统上测试兼容性

## 🔍 故障排除

### 常见问题

**Q: 打包失败，提示模块找不到？**
A: 检查 hiddenimports 列表，添加缺失的模块

**Q: exe 文件无法运行？**
A: 检查是否在 Windows 系统上打包，确保目标系统兼容

**Q: 程序启动很慢？**
A: 这是正常现象，PyInstaller 打包的程序需要解压时间

**Q: 杀毒软件报警？**
A: 添加程序到杀毒软件白名单，或使用代码签名证书

## 📞 技术支持

如遇到打包问题，请提供：
1. 操作系统版本
2. Python 版本
3. 错误信息截图
4. 打包日志文件
'''
    
    with open('Windows打包指南.md', 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("📝 已创建完整的 Windows 打包指南")

def main():
    """主函数"""
    print("🚀 BBS图片爬虫 Windows 跨平台打包工具")
    print("=" * 60)
    
    current_platform = platform.system()
    print(f"🖥️  当前系统: {current_platform}")
    
    if current_platform != "Windows":
        print("⚠️  注意: 当前不在 Windows 系统上")
        print("   生成的文件需要在 Windows 系统上使用")
    
    # 检查是否在正确的目录
    if not os.path.exists('main.py'):
        print("❌ 错误: 请在项目根目录运行此脚本")
        return
    
    print("\n📦 创建打包配置文件...")
    
    # 创建各种配置文件
    create_windows_spec()
    create_batch_script()
    create_comprehensive_guide()
    
    print("\n✅ 所有配置文件已创建完成!")
    print("\n📋 生成的文件:")
    print("  - windows_build.spec (PyInstaller 配置)")
    print("  - build_windows.bat (Windows 批处理脚本)")
    print("  - Windows打包指南.md (详细说明)")
    
    print("\n🎯 下一步操作:")
    if current_platform == "Windows":
        print("  1. 双击运行 'build_windows.bat'")
        print("  2. 或执行: pyinstaller --clean windows_build.spec")
    else:
        print("  1. 将项目文件复制到 Windows 系统")
        print("  2. 在 Windows 上双击运行 'build_windows.bat'")
        print("  3. 或使用虚拟机/GitHub Actions 自动打包")
    
    print("\n📖 详细说明请查看: Windows打包指南.md")

if __name__ == "__main__":
    main() 