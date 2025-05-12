#!/usr/bin/env python
"""
COVID-19疫情数据分析平台启动脚本
支持Windows和Linux/MacOS系统
"""
import os
import sys
import subprocess
import getpass

def create_database():
    """创建MySQL数据库"""
    print("正在创建MySQL数据库...")
    
    # 获取数据库配置
    db_name = "covid_dashboard"
    db_user = "root"
    db_password = input("请输入MySQL密码 (默认为'barry*1394'): ") or "barry*1394"
    
    try:
        # 检查系统
        if os.name == 'nt':  # Windows
            cmd = f'mysql -u {db_user} -p"{db_password}" -e "CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"'
        else:  # Linux/MacOS
            cmd = f'mysql -u {db_user} -p"{db_password}" -e "CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"'
        
        subprocess.run(cmd, shell=True)
        print(f"数据库 '{db_name}' 创建成功或已存在")
        return True
    except Exception as e:
        print(f"数据库创建出错: {str(e)}")
        return False

def apply_migrations():
    """应用数据库迁移"""
    print("正在应用数据库迁移...")
    try:
        subprocess.run([sys.executable, "manage.py", "makemigrations", "covid_data"], check=True)
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        print("数据库迁移完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"迁移出错: {str(e)}")
        return False

def import_data():
    """导入数据"""
    answer = input("是否导入疫情数据? (y/n): ").lower()
    if answer == 'y':
        print("正在导入数据...")
        try:
            # 获取json_dxy目录路径
            # 尝试查找上级目录的json_dxy文件夹
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(os.path.dirname(script_dir))
            default_json_dir = os.path.join(base_dir, 'json_dxy')
            
            # 如果默认路径存在，使用它，否则让用户输入
            if os.path.exists(default_json_dir):
                print(f"找到默认JSON数据目录: {default_json_dir}")
                json_dir = input(f"请输入JSON文件目录路径 (默认为'{default_json_dir}'): ") or default_json_dir
            else:
                json_dir = input("请输入JSON文件目录路径: ")
            
            if not json_dir:
                print("未提供JSON目录，跳过数据导入")
                return True
                
            if not os.path.exists(json_dir):
                print(f"错误: 目录不存在: {json_dir}")
                return False
                
            # 导入数据
            cmd = [sys.executable, "manage.py", "import_covid_data"]
            if json_dir:
                cmd.extend(["--dir", json_dir])
            
            subprocess.run(cmd, check=True)
            print("数据导入完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"导入数据出错: {str(e)}")
            return False
    return True

def start_server():
    """启动开发服务器"""
    print("正在启动服务器...")
    print("请访问 http://127.0.0.1:8000 查看系统")
    try:
        subprocess.run([sys.executable, "manage.py", "runserver"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"启动服务器出错: {str(e)}")
        return False
    except KeyboardInterrupt:
        print("\n服务器已停止")
        return True

def main():
    """主函数"""
    print("===== COVID-19疫情数据分析平台 =====")
    
    # 获取脚本当前路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查是否在项目目录中
    if not os.path.exists(os.path.join(current_dir, "manage.py")):
        print(f"错误: 未找到manage.py文件")
        print(f"请在Django项目目录下运行此脚本")
        print(f"当前目录: {current_dir}")
        return 1
    
    # 创建数据库
    if not create_database():
        return 1
    
    # 应用数据库迁移
    if not apply_migrations():
        return 1
    
    # 导入数据
    if not import_data():
        return 1
    
    # 启动服务器
    if not start_server():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 