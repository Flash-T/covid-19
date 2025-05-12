@echo off
echo ===== COVID-19疫情数据分析平台 =====

REM 创建数据库（仅首次运行需要）
echo 正在创建MySQL数据库...
mysql -u root -p"barry*1394" -e "CREATE DATABASE IF NOT EXISTS covid_dashboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

REM 应用数据库迁移
echo 正在应用数据库迁移...
python manage.py makemigrations covid_data
python manage.py migrate

REM 检查上级目录是否存在json_dxy文件夹
cd ..
cd ..
if exist json_dxy (
    set JSON_DIR=%CD%\json_dxy
    echo 找到默认JSON数据目录: %JSON_DIR%
) else (
    set JSON_DIR=
)
cd code\covid_dashboard

REM 导入数据
set /p import_data=是否导入数据？(y/n)：
if /i "%import_data%"=="y" (
    echo 正在导入数据...
    if not "%JSON_DIR%"=="" (
        python manage.py import_covid_data --dir="%JSON_DIR%"
    ) else (
        set /p custom_dir=请输入JSON文件目录路径: 
        if not "%custom_dir%"=="" (
            python manage.py import_covid_data --dir="%custom_dir%"
        ) else (
            echo 未提供JSON目录，跳过数据导入
        )
    )
)

REM 启动服务器
echo 正在启动服务器...
echo 请访问 http://127.0.0.1:8000 查看系统
python manage.py runserver

pause 