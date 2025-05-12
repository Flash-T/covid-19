import os
from django.core.management.base import BaseCommand
from covid_data.import_data import import_all_data

class Command(BaseCommand):
    help = '从JSON文件导入COVID-19疫情数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dir',
            type=str,
            help='包含JSON文件的目录路径',
        )

    def handle(self, *args, **options):
        data_dir = options['dir']
        if not data_dir:
            # 默认使用项目根目录的上级目录下的json_dxy文件夹
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
            data_dir = os.path.join(base_dir, 'json_dxy')
        
        self.stdout.write(self.style.SUCCESS(f'开始导入数据，数据目录: {data_dir}'))
        
        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR(f'目录不存在: {data_dir}'))
            return
        
        results = import_all_data(data_dir)
        
        self.stdout.write(self.style.SUCCESS(
            f"导入完成: 成功 {results['success']} 个文件, 失败 {results['error']} 个文件, 共 {results['total']} 个文件"
        )) 