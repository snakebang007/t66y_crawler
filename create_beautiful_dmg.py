#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建美观的DMG安装包
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_background_image():
    """创建DMG背景图片"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 创建背景图片 (600x400)
        width, height = 600, 400
        img = Image.new('RGB', (width, height), color='#f0f0f0')
        draw = ImageDraw.Draw(img)
        
        # 绘制渐变背景
        for y in range(height):
            color_value = int(240 - (y / height) * 20)
            color = (color_value, color_value, color_value + 10)
            draw.line([(0, y), (width, y)], fill=color)
        
        # 添加标题文字
        try:
            # 尝试使用系统字体
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        except:
            # 如果找不到字体，使用默认字体
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # 绘制标题
        title_text = "BBS图片爬虫"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 50), title_text, fill='#333333', font=title_font)
        
        # 绘制副标题
        subtitle_text = "拖拽应用程序到 Applications 文件夹进行安装"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (width - subtitle_width) // 2
        draw.text((subtitle_x, 100), subtitle_text, fill='#666666', font=subtitle_font)
        
        # 绘制箭头指示
        arrow_y = 200
        # 从应用程序位置到Applications文件夹的箭头
        draw.line([(200, arrow_y), (400, arrow_y)], fill='#4CAF50', width=3)
        # 箭头头部
        draw.polygon([(390, arrow_y-10), (400, arrow_y), (390, arrow_y+10)], fill='#4CAF50')
        
        # 保存背景图片
        img.save('dmg_background.png')
        print("✅ 背景图片创建成功")
        return True
        
    except ImportError:
        print("⚠️  PIL未安装，跳过背景图片创建")
        return False
    except Exception as e:
        print(f"⚠️  背景图片创建失败: {e}")
        return False

def create_beautiful_dmg():
    """创建美观的DMG"""
    print("🎨 开始创建美观的DMG安装包...")
    
    app_name = "BBS图片爬虫"
    dmg_name = f"{app_name}-1.0.0-Beautiful.dmg"
    
    # 检查应用程序是否存在
    app_path = f"dist/{app_name}.app"
    if not os.path.exists(app_path):
        print("❌ 找不到应用程序，请先构建应用程序")
        return False
    
    # 创建临时DMG目录
    dmg_temp_dir = "dmg_beautiful_temp"
    if os.path.exists(dmg_temp_dir):
        shutil.rmtree(dmg_temp_dir)
    os.makedirs(dmg_temp_dir)
    
    # 复制应用程序到临时目录
    shutil.copytree(app_path, f"{dmg_temp_dir}/{app_name}.app")
    
    # 创建Applications符号链接
    os.symlink("/Applications", f"{dmg_temp_dir}/Applications")
    
    # 创建背景图片
    has_background = create_background_image()
    if has_background:
        shutil.copy("dmg_background.png", f"{dmg_temp_dir}/.background.png")
    
    # 创建DS_Store文件来设置Finder视图
    background_line = 'set background picture of viewOptions to file ".background.png"' if has_background else ""
    ds_store_script = f"""
tell application "Finder"
    tell disk "{app_name}"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {{100, 100, 700, 500}}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 128
        {background_line}
        set position of item "{app_name}.app" of container window to {{150, 200}}
        set position of item "Applications" of container window to {{450, 200}}
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
"""
    
    # 创建临时AppleScript文件
    with open("setup_dmg.applescript", "w") as f:
        f.write(ds_store_script)
    
    # 首先创建基本DMG
    temp_dmg = f"{app_name}-temp.dmg"
    if os.path.exists(temp_dmg):
        os.remove(temp_dmg)
    
    cmd = [
        "hdiutil", "create",
        "-volname", app_name,
        "-srcfolder", dmg_temp_dir,
        "-ov",
        "-format", "UDRW",  # 读写格式，便于修改
        temp_dmg
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print("✅ 临时DMG创建成功")
    except subprocess.CalledProcessError as e:
        print(f"❌ 临时DMG创建失败: {e}")
        return False
    
    # 挂载DMG进行自定义
    print("🔧 正在自定义DMG布局...")
    try:
        # 挂载DMG
        mount_result = subprocess.run(
            ["hdiutil", "attach", temp_dmg, "-readwrite", "-noverify", "-noautoopen"],
            capture_output=True, text=True
        )
        
        if mount_result.returncode == 0:
            # 运行AppleScript设置布局
            subprocess.run(["osascript", "setup_dmg.applescript"], check=False)
            
            # 等待一下让设置生效
            import time
            time.sleep(3)
            
            # 卸载DMG
            subprocess.run(["hdiutil", "detach", f"/Volumes/{app_name}"], check=False)
            
    except Exception as e:
        print(f"⚠️  DMG自定义失败: {e}")
    
    # 转换为最终的压缩DMG
    if os.path.exists(dmg_name):
        os.remove(dmg_name)
    
    cmd = [
        "hdiutil", "convert", temp_dmg,
        "-format", "UDZO",
        "-imagekey", "zlib-level=9",
        "-o", dmg_name
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ 美观DMG创建成功: {dmg_name}")
        
        # 清理临时文件
        os.remove(temp_dmg)
        shutil.rmtree(dmg_temp_dir)
        if os.path.exists("setup_dmg.applescript"):
            os.remove("setup_dmg.applescript")
        if os.path.exists("dmg_background.png"):
            os.remove("dmg_background.png")
        
        # 显示文件大小
        dmg_size = os.path.getsize(dmg_name) / (1024 * 1024)
        print(f"📦 DMG文件大小: {dmg_size:.1f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 最终DMG创建失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🎨 BBS图片爬虫 - 美观DMG制作工具")
    print("=" * 60)
    
    # 检查当前目录
    if not os.path.exists("main.py"):
        print("❌ 错误: 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 检查应用程序是否已构建
    if not os.path.exists("dist/BBS图片爬虫.app"):
        print("❌ 应用程序未找到，请先运行 python3 build_app.py")
        sys.exit(1)
    
    # 创建美观DMG
    if not create_beautiful_dmg():
        print("❌ 美观DMG创建失败")
        sys.exit(1)
    
    print("\n🎉 美观DMG创建完成!")
    print(f"💿 DMG安装包: BBS图片爬虫-1.0.0-Beautiful.dmg")
    print("\n特性:")
    print("✨ 自定义背景图片")
    print("✨ 优化的图标布局")
    print("✨ 拖拽安装指示")
    print("✨ 专业的外观设计")

if __name__ == "__main__":
    main() 