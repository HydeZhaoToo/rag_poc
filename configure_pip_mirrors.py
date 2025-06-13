#!/usr/bin/env python3
"""
配置 pip 镜像源的工具脚本
Tool script to configure pip mirrors for faster downloads in China
"""

import os
import sys
from pathlib import Path

# 国内镜像源配置
MIRRORS = {
    "tsinghua": {
        "name": "清华大学",
        "url": "https://pypi.tuna.tsinghua.edu.cn/simple",
        "host": "pypi.tuna.tsinghua.edu.cn",
        "description": "推荐：国内最稳定的镜像源"
    },
    "aliyun": {
        "name": "阿里云",
        "url": "https://mirrors.aliyun.com/pypi/simple/",
        "host": "mirrors.aliyun.com",
        "description": "阿里云提供，速度较快"
    },
    "ustc": {
        "name": "中国科技大学",
        "url": "https://pypi.mirrors.ustc.edu.cn/simple/",
        "host": "pypi.mirrors.ustc.edu.cn",
        "description": "中科大提供，学术网络友好"
    },
    "douban": {
        "name": "豆瓣",
        "url": "https://pypi.douban.com/simple/",
        "host": "pypi.douban.com",
        "description": "豆瓣提供，历史悠久"
    },
    "baidu": {
        "name": "百度",
        "url": "https://mirror.baidu.com/pypi/simple/",
        "host": "mirror.baidu.com", 
        "description": "百度提供"
    }
}

def create_pip_config(mirror_key="tsinghua"):
    """创建 pip 配置文件"""
    
    if mirror_key not in MIRRORS:
        print(f"❌ 错误：镜像源 '{mirror_key}' 不存在")
        return False
    
    mirror = MIRRORS[mirror_key]
    
    # 创建 pip 配置目录
    pip_config_dir = Path.home() / ".pip"
    pip_config_dir.mkdir(exist_ok=True)
    
    # 生成配置内容
    config_content = f"""[global]
index-url = {mirror['url']}
trusted-host = {mirror['host']}

[install]
trusted-host = {mirror['host']}
"""
    
    # 写入配置文件
    config_file = pip_config_dir / "pip.conf"
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✅ 成功配置 pip 镜像源: {mirror['name']}")
        print(f"   URL: {mirror['url']}")
        print(f"   配置文件: {config_file}")
        return True
        
    except Exception as e:
        print(f"❌ 配置失败: {e}")
        return False

def test_mirror_speed():
    """测试镜像源速度"""
    print("🧪 测试镜像源连通性...")
    
    import subprocess
    import time
    
    for key, mirror in MIRRORS.items():
        print(f"\n测试 {mirror['name']} ({key})...")
        try:
            start_time = time.time()
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', mirror['url']],
                capture_output=True, 
                text=True, 
                timeout=10
            )
            end_time = time.time()
            
            if result.returncode == 0 and result.stdout == '200':
                print(f"  ✅ 连通正常 - 响应时间: {end_time - start_time:.2f}s")
            else:
                print(f"  ❌ 连通失败 - HTTP状态: {result.stdout}")
                
        except subprocess.TimeoutExpired:
            print(f"  ⏱️  超时 (>10s)")
        except Exception as e:
            print(f"  ❌ 错误: {e}")

def install_docling_with_mirror(mirror_key="tsinghua"):
    """使用指定镜像安装 Docling"""
    
    if mirror_key not in MIRRORS:
        print(f"❌ 错误：镜像源 '{mirror_key}' 不存在")
        return False
    
    mirror = MIRRORS[mirror_key]
    
    print(f"📦 使用 {mirror['name']} 安装 Docling...")
    
    # 安装命令
    packages = [
        "torch==2.2.2",
        "torchvision==0.17.2",
        "docling",
        "langchain",
        "langchain-community", 
        "langchain-openai",
        "faiss-cpu",
        "python-dotenv",
        "openai",
        "tiktoken",
        "beautifulsoup4",
        "lxml",
        "numpy",
        "pypdf2",
        "pandas"
    ]
    
    import subprocess
    
    try:
        for package in packages:
            print(f"正在安装 {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                package, 
                "-i", mirror['url'],
                "--trusted-host", mirror['host']
            ], check=True, capture_output=True, text=True)
            
        print("✅ 所有包安装完成!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def show_usage():
    """显示使用说明"""
    print("🔧 pip 镜像源配置工具")
    print("=" * 50)
    print("\n可用镜像源:")
    
    for key, mirror in MIRRORS.items():
        print(f"  {key:10} - {mirror['name']:10} - {mirror['description']}")
    
    print(f"\n使用方法:")
    print(f"  python {sys.argv[0]} config [镜像名]     # 配置镜像源")
    print(f"  python {sys.argv[0]} test              # 测试镜像源速度") 
    print(f"  python {sys.argv[0]} install [镜像名]   # 使用指定镜像安装Docling")
    print(f"  python {sys.argv[0]} help              # 显示帮助")
    
    print(f"\n示例:")
    print(f"  python {sys.argv[0]} config tsinghua   # 配置清华镜像")
    print(f"  python {sys.argv[0]} install aliyun    # 使用阿里云镜像安装")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "help":
        show_usage()
    elif command == "config":
        mirror_key = sys.argv[2] if len(sys.argv) > 2 else "tsinghua"
        create_pip_config(mirror_key)
    elif command == "test":
        test_mirror_speed()
    elif command == "install":
        mirror_key = sys.argv[2] if len(sys.argv) > 2 else "tsinghua"
        # 先配置镜像
        create_pip_config(mirror_key)
        # 再安装
        install_docling_with_mirror(mirror_key)
    else:
        print(f"❌ 未知命令: {command}")
        show_usage()

if __name__ == "__main__":
    main()