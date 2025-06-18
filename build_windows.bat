@echo off
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
if exist "dist\BBS图片爬虫.exe" (
    echo.
    echo 🎉 打包成功!
    echo 📦 可执行文件位置: dist\BBS图片爬虫.exe
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
