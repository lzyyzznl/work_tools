#!/usr/bin/env python3
"""
通用Nuitka构建器
包含所有构建逻辑，避免代码重复
"""

import logging
import os
import subprocess
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class NuitkaBuilder:
    """通用Nuitka构建器"""

    def __init__(self, app_config, debug_mode=False):
        """
        初始化构建器
        
        app_config: dict 包含以下键值：
        - name: 应用名称（中文）
        - exe_name: exe文件名（英文，不含.exe后缀）
        - entry_point: 入口文件路径
        - app_dir: 应用目录（用于资源文件）
        - icon_path: 图标文件路径
        """
        self.app_name = app_config["name"]
        self.exe_name = app_config["exe_name"]
        self.entry_point = app_config["entry_point"]
        self.app_dir = app_config["app_dir"]
        self.icon_path = app_config["icon_path"]
        self.output_dir = "dist"
        self.debug_mode = debug_mode

    def build_executable(self):
        """构建可执行文件"""
        logger.info(f"开始构建 {self.app_name}...")
        logger.info(f"调试模式: {'开启' if self.debug_mode else '关闭'}")

        # 构建基本命令
        cmd = [
            sys.executable, "-m", "nuitka",
            "--standalone",                 # 独立模式（必须）
            "--enable-plugin=pyside6",       # PySide6插件
            f"--output-filename={self.exe_name}.exe",  # 使用英文文件名避免编码问题
            f"--output-dir={self.output_dir}",
            f"--include-data-dir={self.app_dir}/resources=resources",  # 包含资源文件
            "--assume-yes-for-downloads",   # 自动下载依赖
            "--show-progress",              # 显示构建进度
        ]

        # Windows特定设置
        if os.name == "nt":
            if self.debug_mode:
                # 调试模式：保留控制台窗口，显示错误信息
                cmd.append("--windows-console-mode=force")
                logger.info("调试模式：启用控制台窗口")
            else:
                # 发布模式：禁用控制台
                cmd.append("--windows-console-mode=disable")
                logger.info("发布模式：禁用控制台窗口")
            
            # 如果图标文件存在，添加图标
            if os.path.exists(self.icon_path):
                cmd.append(f"--windows-icon-from-ico={self.icon_path}")
                logger.info(f"使用图标: {self.icon_path}")
            else:
                logger.warning(f"图标文件不存在: {self.icon_path}")

        # 发布模式参数
        if not self.debug_mode:
            cmd.extend([
                "--onefile",                    # 单文件打包
                "--lto=yes",                    # 链接时优化
                "--remove-output",              # 删除临时文件
                "--python-flag=no_asserts",     # 禁用断言提升性能
            ])
            logger.info("发布模式：优化性能，单文件打包")
           

        # 添加入口点
        cmd.append(self.entry_point)

        logger.info(f"执行命令: {' '.join(cmd)}")

        try:
            # 执行构建
            result = subprocess.run(cmd, cwd=".", check=False)
            
            if result.returncode == 0:
                if self.debug_mode:
                    exe_path = f"{self.output_dir}/{self.exe_name}.dist/{self.exe_name}.exe"
                else:
                    exe_path = f"{self.output_dir}/{self.exe_name}.exe"
                
                if os.path.exists(exe_path):
                    size = os.path.getsize(exe_path) / 1024 / 1024  # MB
                    logger.info(f"✅ 构建成功: {exe_path} ({size:.1f} MB)")
                    
                    if self.debug_mode:
                        logger.info("🐛 调试模式构建完成，exe运行时会显示控制台窗口用于调试")
                    else:
                        logger.info("🚀 发布模式构建完成，如果运行有问题请用调试模式重新构建")
                    
                    return True
                else:
                    logger.error(f"❌ 构建完成但未找到输出文件: {exe_path}")
                    # 尝试查找可能的输出文件
                    if os.path.exists(f"{self.output_dir}"):
                        logger.info(f"输出目录 {self.output_dir} 内容:")
                        for item in os.listdir(self.output_dir):
                            logger.info(f"  - {item}")
                    return False
            else:
                logger.error(f"❌ 构建失败，返回码: {result.returncode}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 构建过程异常: {e}")
            return False

    def run(self):
        """执行构建流程"""
        logger.info(f"=== 开始构建 {self.app_name} ===")
        
        # 检查Nuitka
        if not self.check_nuitka():
            logger.error("请先安装Nuitka: pip install nuitka")
            sys.exit(1)
        
        # 检查入口文件
        if not self.check_entry_point():
            sys.exit(1)
        
        # 构建
        if self.build_executable():
            logger.info(f"=== {self.app_name} 构建完成 ===")
            if self.debug_mode:
                print("\n📋 下一步：")
                print("1. 运行生成的exe文件")
                print("2. 查看控制台输出的错误信息")
                print("3. 根据错误信息修复问题")
                print(f"4. 修复后用正常模式重新构建")
        else:
            logger.error(f"=== {self.app_name} 构建失败 ===")
            sys.exit(1) 

    def check_nuitka(self):
        """检查Nuitka是否可用"""
        try:
            result = subprocess.run([sys.executable, "-m", "nuitka", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Nuitka版本: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"Nuitka不可用: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"检查Nuitka失败: {e}")
            return False

    def check_entry_point(self):
        """检查入口文件是否存在"""
        if not os.path.exists(self.entry_point):
            logger.error(f"入口文件不存在: {self.entry_point}")
            return False
        logger.info(f"入口文件: {self.entry_point}")
        return True

    