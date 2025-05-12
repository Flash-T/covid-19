import os
import sys
import django

# 设置Django环境
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'covid_dashboard.settings')
django.setup()

from covid_data.import_data import import_all_data

# 获取json_dxy目录路径
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(os.path.dirname(base_dir), 'json_dxy')

print(f"开始导入数据，数据目录: {data_dir}")
results = import_all_data(data_dir)
print(f"导入完成: 成功 {results['success']} 个文件, 失败 {results['error']} 个文件, 共 {results['total']} 个文件")