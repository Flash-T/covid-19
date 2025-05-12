# COVID-19疫情数据分析平台

基于丁香园公开数据的COVID-19疫情数据可视化分析平台，采用Django框架开发。

## 主要功能

- 全国疫情数据总览，显示确诊、疑似、治愈、死亡数据
- 中国疫情地图可视化，展示各省份疫情情况
- 全国疫情趋势图，展示确诊、治愈、死亡人数变化趋势
- 每日新增数据图表，展示每日新增确诊、治愈、死亡病例
- 省份疫情排行榜，展示疫情最严重的省份
- 日期选择器，可查看历史数据
- 省份详情功能，包括省内城市疫情数据

## 技术栈

- 后端：Django (Python)
- 数据库：MySQL
- 前端：Bootstrap 4, jQuery, ECharts
- 数据可视化：pyecharts (基于ECharts的Python库)

## 快速开始

### Windows用户

1. 确保已安装MySQL，并设置好root用户密码
2. 双击运行 `run_project.bat` 或者在命令行中运行 `python start.py`
3. 根据提示进行操作
4. 访问 http://127.0.0.1:8000/ 查看系统

### Linux/MacOS用户

1. 确保已安装MySQL，并设置好root用户密码
2. 在终端中运行 `python start.py`
3. 根据提示进行操作
4. 访问 http://127.0.0.1:8000/ 查看系统

## 安装与使用

### 环境要求

- Python 3.8+
- MySQL 5.7+

### 安装依赖

```bash
pip install django mysqlclient pandas numpy matplotlib pyecharts django-cors-headers
```

### 配置数据库

1. 创建MySQL数据库

```sql
CREATE DATABASE covid_dashboard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 在 `covid_dashboard/settings.py` 中配置数据库连接：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'covid_dashboard',
        'USER': 'root',
        'PASSWORD': 'barry*1394',  # 请修改为你的密码
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 迁移数据库

```bash
python manage.py makemigrations covid_data
python manage.py migrate
```

### 导入疫情数据

```bash
python manage.py import_covid_data --dir=/path/to/json_dxy
```

### 运行开发服务器

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000/ 即可查看系统。

## 目录结构

```
covid_dashboard/
├── covid_data/             # 主应用
│   ├── management/         # 管理命令
│   │   └── commands/       # 自定义命令
│   ├── migrations/         # 数据库迁移文件
│   ├── models.py           # 数据模型
│   ├── views.py            # 视图函数
│   ├── urls.py             # URL配置
│   └── import_data.py      # 数据导入脚本
├── covid_dashboard/        # 项目配置
│   ├── settings.py         # 项目设置
│   ├── urls.py             # 项目URL配置
│   ├── wsgi.py             # WSGI配置
│   └── asgi.py             # ASGI配置
├── templates/              # 模板文件
│   ├── base.html           # 基础模板
│   └── index.html          # 首页模板
├── static/                 # 静态文件
│   ├── css/                # CSS文件
│   ├── js/                 # JavaScript文件
│   └── img/                # 图片文件
├── run_project.bat         # Windows一键启动脚本
├── start.py                # 跨平台启动脚本
└── manage.py               # Django管理脚本
```

## 数据来源

本系统使用的数据来源于丁香园公开的COVID-19疫情数据，数据格式为JSON，存放在`json_dxy`目录中。 