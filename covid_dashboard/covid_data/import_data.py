import os
import json
import datetime
from django.db import transaction
from django.conf import settings
from covid_data.models import Province, City, DailyStatistics

def parse_date_from_filename(filename):
    """从文件名中解析日期"""
    # 文件名格式: COVID-19_2020-01-24(CN-DATA)by_DXY.json
    date_str = filename.split('_')[1].split('(')[0]
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

def import_single_file(file_path, date):
    """导入单个JSON文件数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 每天的全国总计数据
    daily_total = {
        'confirmed_count': 0,
        'suspected_count': 0,
        'cured_count': 0,
        'dead_count': 0
    }
    
    # 获取前一天的数据，用于计算增量
    yesterday = date - datetime.timedelta(days=1)
    prev_stats = DailyStatistics.objects.filter(date=yesterday).first()
    
    # 使用事务确保数据完整性
    with transaction.atomic():
        # 导入省份和城市数据
        for province_data in data:
            province_name = province_data['provinceName']
            province_short_name = province_data['provinceShortName']
            
            # 创建或更新省份数据
            province, created = Province.objects.update_or_create(
                name=province_name,
                data_date=date,
                defaults={
                    'short_name': province_short_name,
                    'confirmed_count': province_data['confirmedCount'],
                    'suspected_count': province_data['suspectedCount'],
                    'cured_count': province_data['curedCount'],
                    'dead_count': province_data['deadCount'],
                    'comment': province_data.get('comment', '')
                }
            )
            
            # 累加到全国总计
            daily_total['confirmed_count'] += province_data['confirmedCount']
            daily_total['suspected_count'] += province_data['suspectedCount']
            daily_total['cured_count'] += province_data['curedCount']
            daily_total['dead_count'] += province_data['deadCount']
            
            # 导入城市数据
            cities = province_data.get('cities', [])
            for city_data in cities:
                city_name = city_data['cityName']
                
                City.objects.update_or_create(
                    province=province,
                    name=city_name,
                    data_date=date,
                    defaults={
                        'confirmed_count': city_data['confirmedCount'],
                        'suspected_count': city_data['suspectedCount'],
                        'cured_count': city_data['curedCount'],
                        'dead_count': city_data['deadCount']
                    }
                )
        
        # 计算增量
        confirmed_incr = daily_total['confirmed_count'] - (prev_stats.confirmed_count if prev_stats else 0)
        suspected_incr = daily_total['suspected_count'] - (prev_stats.suspected_count if prev_stats else 0)
        cured_incr = daily_total['cured_count'] - (prev_stats.cured_count if prev_stats else 0)
        dead_incr = daily_total['dead_count'] - (prev_stats.dead_count if prev_stats else 0)
        
        # 创建或更新每日统计
        DailyStatistics.objects.update_or_create(
            date=date,
            defaults={
                'confirmed_count': daily_total['confirmed_count'],
                'suspected_count': daily_total['suspected_count'],
                'cured_count': daily_total['cured_count'],
                'dead_count': daily_total['dead_count'],
                'confirmed_incr': max(0, confirmed_incr),
                'suspected_incr': max(0, suspected_incr),
                'cured_incr': max(0, cured_incr),
                'dead_incr': max(0, dead_incr)
            }
        )
    
    return True

def import_all_data(data_dir):
    """导入指定目录下的所有JSON文件"""
    # 确保按日期顺序导入文件
    files = sorted([f for f in os.listdir(data_dir) if f.endswith('.json')])
    success_count = 0
    error_count = 0
    
    for filename in files:
        file_path = os.path.join(data_dir, filename)
        try:
            date = parse_date_from_filename(filename)
            if import_single_file(file_path, date):
                success_count += 1
                print(f"成功导入数据: {filename}")
            else:
                error_count += 1
                print(f"导入数据失败: {filename}")
        except Exception as e:
            error_count += 1
            print(f"导入数据出错: {filename}, 错误: {str(e)}")
    
    return {
        'success': success_count,
        'error': error_count,
        'total': success_count + error_count
    }

if __name__ == "__main__":
    # 当作为脚本直接运行时
    import django
    import sys
    import os
    
    # 设置Django环境
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'covid_dashboard.settings')
    django.setup()
    
    # 默认使用上级目录的json_dxy文件夹
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    data_dir = os.path.join(base_dir, 'json_dxy')
    
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    
    print(f"开始导入数据，数据目录: {data_dir}")
    results = import_all_data(data_dir)
    print(f"导入完成: 成功 {results['success']} 个文件, 失败 {results['error']} 个文件, 共 {results['total']} 个文件") 