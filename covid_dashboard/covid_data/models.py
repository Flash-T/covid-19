from django.db import models

class Province(models.Model):
    """省份疫情数据模型"""
    name = models.CharField('省份名称', max_length=50)
    short_name = models.CharField('省份简称', max_length=20)
    confirmed_count = models.IntegerField('确诊人数', default=0)
    suspected_count = models.IntegerField('疑似病例', default=0)
    cured_count = models.IntegerField('治愈人数', default=0)
    dead_count = models.IntegerField('死亡人数', default=0)
    comment = models.TextField('备注', blank=True, null=True)
    data_date = models.DateField('数据日期')
    
    class Meta:
        verbose_name = '省份疫情数据'
        verbose_name_plural = verbose_name
        unique_together = ('name', 'data_date')
    
    def __str__(self):
        return f"{self.name}({self.data_date})"

class City(models.Model):
    """城市疫情数据模型"""
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities', verbose_name='所属省份')
    name = models.CharField('城市名称', max_length=50)
    confirmed_count = models.IntegerField('确诊人数', default=0)
    suspected_count = models.IntegerField('疑似病例', default=0)
    cured_count = models.IntegerField('治愈人数', default=0)
    dead_count = models.IntegerField('死亡人数', default=0)
    data_date = models.DateField('数据日期')
    
    class Meta:
        verbose_name = '城市疫情数据'
        verbose_name_plural = verbose_name
        unique_together = ('province', 'name', 'data_date')
    
    def __str__(self):
        return f"{self.name}({self.data_date})"

class DailyStatistics(models.Model):
    """全国每日统计数据"""
    date = models.DateField('日期', unique=True)
    confirmed_count = models.IntegerField('确诊总数', default=0)
    suspected_count = models.IntegerField('疑似总数', default=0)
    cured_count = models.IntegerField('治愈总数', default=0)
    dead_count = models.IntegerField('死亡总数', default=0)
    confirmed_incr = models.IntegerField('新增确诊', default=0)
    suspected_incr = models.IntegerField('新增疑似', default=0)
    cured_incr = models.IntegerField('新增治愈', default=0)
    dead_incr = models.IntegerField('新增死亡', default=0)
    
    class Meta:
        verbose_name = '每日全国统计'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"全国统计({self.date})" 