import json
import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, F, Max
from pyecharts.charts import Map, Line, Bar, Pie
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from .models import Province, City, DailyStatistics

def index(request):
    """首页展示四个看板"""
    # 获取最新数据日期
    latest_date = Province.objects.aggregate(Max('data_date'))['data_date__max']
    
    # 今日全国统计
    today_stats = DailyStatistics.objects.filter(date=latest_date).first()
    
    # 如果没有统计数据，计算一个
    if not today_stats:
        province_stats = Province.objects.filter(data_date=latest_date).aggregate(
            confirmed=Sum('confirmed_count'),
            suspected=Sum('suspected_count'),
            cured=Sum('cured_count'),
            dead=Sum('dead_count')
        )
        today_stats = {
            'confirmed_count': province_stats['confirmed'] or 0,
            'suspected_count': province_stats['suspected'] or 0,
            'cured_count': province_stats['cured'] or 0,
            'dead_count': province_stats['dead'] or 0,
            'date': latest_date
        }
    
    context = {
        'latest_date': latest_date,
        'today_stats': today_stats,
    }
    
    return render(request, 'index.html', context)

def china_map_data(request):
    """中国疫情地图数据API"""
    date_str = request.GET.get('date')
    
    if date_str:
        try:
            query_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            query_date = Province.objects.aggregate(Max('data_date'))['data_date__max']
    else:
        query_date = Province.objects.aggregate(Max('data_date'))['data_date__max']
    
    provinces = Province.objects.filter(data_date=query_date)
    
    # 构建地图数据
    map_data = []
    for province in provinces:
        map_data.append((province.short_name, province.confirmed_count))
    
    # 创建地图
    china_map = (
        Map(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
        .add(
            "确诊病例",
            map_data,
            "china",
            is_map_symbol_show=False,
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"全国疫情分布图 - {query_date}"),
            visualmap_opts=opts.VisualMapOpts(
                max_=max([d[1] for d in map_data]) if map_data else 100,
                is_piecewise=True,
                pieces=[
                    {"min": 1000, "label": "≥1000", "color": "#731919"},
                    {"min": 500, "max": 999, "label": "500-999", "color": "#9c1414"},
                    {"min": 100, "max": 499, "label": "100-499", "color": "#c92727"},
                    {"min": 10, "max": 99, "label": "10-99", "color": "#e55a4e"},
                    {"min": 1, "max": 9, "label": "1-9", "color": "#f8b2a3"},
                    {"min": 0, "max": 0, "label": "0", "color": "#f5f5f5"},
                ],
            ),
            legend_opts=opts.LegendOpts(is_show=False),
            tooltip_opts=opts.TooltipOpts(
                trigger="item", 
                formatter="{b}: {c}"
            ),
        )
    )
    
    return JsonResponse({
        "map_options": china_map.dump_options(),
        "date": query_date.strftime('%Y-%m-%d'),
    })

def trend_chart_data(request):
    """全国疫情趋势图数据API"""
    days = int(request.GET.get('days', 30))
    
    # 获取最新日期
    latest_date = Province.objects.aggregate(Max('data_date'))['data_date__max']
    
    # 计算起始日期
    start_date = latest_date - datetime.timedelta(days=days-1)
    
    # 获取每日数据
    daily_data = DailyStatistics.objects.filter(
        date__gte=start_date,
        date__lte=latest_date
    ).order_by('date')
    
    # 如果没有足够的每日统计，从省份数据计算
    if daily_data.count() < days:
        dates = []
        date = start_date
        while date <= latest_date:
            dates.append(date)
            date += datetime.timedelta(days=1)
        
        daily_data = []
        for date in dates:
            province_stats = Province.objects.filter(data_date=date).aggregate(
                confirmed=Sum('confirmed_count'),
                suspected=Sum('suspected_count'),
                cured=Sum('cured_count'),
                dead=Sum('dead_count')
            )
            
            daily_data.append({
                'date': date.strftime('%m-%d'),
                'confirmed_count': province_stats['confirmed'] or 0,
                'suspected_count': province_stats['suspected'] or 0,
                'cured_count': province_stats['cured'] or 0,
                'dead_count': province_stats['dead'] or 0
            })
    else:
        daily_data = [
            {
                'date': item.date.strftime('%m-%d'),
                'confirmed_count': item.confirmed_count,
                'suspected_count': item.suspected_count,
                'cured_count': item.cured_count,
                'dead_count': item.dead_count,
                'confirmed_incr': item.confirmed_incr,
                'cured_incr': item.cured_incr,
                'dead_incr': item.dead_incr
            }
            for item in daily_data
        ]
    
    # 生成趋势图
    x_data = [item['date'] for item in daily_data]
    confirmed_data = [item['confirmed_count'] for item in daily_data]
    cured_data = [item['cured_count'] for item in daily_data]
    dead_data = [item['dead_count'] for item in daily_data]
    
    # 构建确诊/治愈/死亡趋势线
    line_chart = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
        .add_xaxis(x_data)
        .add_yaxis("确诊", confirmed_data, is_smooth=True, 
                  linestyle_opts=opts.LineStyleOpts(width=3, color="#c92727"),
                  label_opts=opts.LabelOpts(is_show=False))
        .add_yaxis("治愈", cured_data, is_smooth=True, 
                  linestyle_opts=opts.LineStyleOpts(width=3, color="#28a745"),
                  label_opts=opts.LabelOpts(is_show=False))
        .add_yaxis("死亡", dead_data, is_smooth=True, 
                  linestyle_opts=opts.LineStyleOpts(width=3, color="#5d7092"),
                  label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="全国疫情趋势"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
        )
    )
    
    # 如果有增量数据，增加每日新增柱状图
    if 'confirmed_incr' in daily_data[0]:
        confirmed_incr = [item['confirmed_incr'] for item in daily_data]
        cured_incr = [item['cured_incr'] for item in daily_data]
        dead_incr = [item['dead_incr'] for item in daily_data]
        
        bar_chart = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
            .add_xaxis(x_data)
            .add_yaxis("新增确诊", confirmed_incr, 
                      category_gap="50%", color="#c92727",
                      label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("新增治愈", cured_incr, 
                      category_gap="50%", color="#28a745",
                      label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("新增死亡", dead_incr, 
                      category_gap="50%", color="#5d7092",
                      label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="每日新增趋势"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=True),
            )
        )
        
        return JsonResponse({
            "line_options": line_chart.dump_options(),
            "bar_options": bar_chart.dump_options()
        })
    
    return JsonResponse({
        "line_options": line_chart.dump_options(),
    })

def province_rank_data(request):
    """省份排行榜数据API"""
    date_str = request.GET.get('date')
    limit = int(request.GET.get('limit', 10))
    
    if date_str:
        try:
            query_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            query_date = Province.objects.aggregate(Max('data_date'))['data_date__max']
    else:
        query_date = Province.objects.aggregate(Max('data_date'))['data_date__max']
    
    # 获取确诊数量前N的省份
    top_provinces = Province.objects.filter(
        data_date=query_date
    ).order_by('-confirmed_count')[:limit]
    
    provinces = []
    for province in top_provinces:
        provinces.append({
            'name': province.short_name,
            'confirmed': province.confirmed_count,
            'cured': province.cured_count,
            'dead': province.dead_count
        })
    
    # 生成柱状图
    provinces_data = sorted(provinces, key=lambda x: x['confirmed'])
    y_data = [p['name'] for p in provinces_data]
    confirmed_data = [p['confirmed'] for p in provinces_data]
    cured_data = [p['cured'] for p in provinces_data]
    dead_data = [p['dead'] for p in provinces_data]
    
    bar_chart = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
        .add_yaxis("确诊", confirmed_data, color="#c92727")
        .add_yaxis("治愈", cured_data, color="#28a745")
        .add_yaxis("死亡", dead_data, color="#5d7092")
        .add_xaxis(y_data)
        .reversal_axis()
        .set_series_opts(label_opts=opts.LabelOpts(position="right"))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"省份疫情排行 - {query_date}"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
            xaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            yaxis_opts=opts.AxisOpts(type_="category"),
        )
    )
    
    return JsonResponse({
        "bar_options": bar_chart.dump_options(),
        "date": query_date.strftime('%Y-%m-%d'),
    })

def province_detail(request, province_name):
    """省份详情页面"""
    latest_date = Province.objects.aggregate(Max('data_date'))['data_date__max']
    
    # 获取省份数据
    province = Province.objects.filter(
        short_name=province_name,
        data_date=latest_date
    ).first()
    
    if not province:
        return JsonResponse({'error': f'未找到省份: {province_name}'}, status=404)
    
    # 获取该省的城市数据
    cities = City.objects.filter(
        province=province,
        data_date=latest_date
    ).order_by('-confirmed_count')
    
    # 城市数据
    city_data = []
    for city in cities:
        city_data.append({
            'name': city.name,
            'confirmed': city.confirmed_count,
            'cured': city.cured_count,
            'dead': city.dead_count
        })
    
    # 生成饼图
    pie_data = [
        ('确诊', province.confirmed_count),
        ('治愈', province.cured_count),
        ('死亡', province.dead_count),
        ('正在治疗', province.confirmed_count - province.cured_count - province.dead_count)
    ]
    
    pie_chart = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
        .add(
            "",
            pie_data,
            radius=["40%", "75%"],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{province.name}疫情统计"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"),
        )
    )
    
    # 生成城市柱状图
    if city_data:
        cities_sorted = sorted(city_data, key=lambda x: x['confirmed'])[-10:]  # 取确诊数最多的10个城市
        y_data = [c['name'] for c in cities_sorted]
        confirmed_data = [c['confirmed'] for c in cities_sorted]
        cured_data = [c['cured'] for c in cities_sorted]
        dead_data = [c['dead'] for c in cities_sorted]
        
        bar_chart = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
            .add_yaxis("确诊", confirmed_data, color="#c92727")
            .add_yaxis("治愈", cured_data, color="#28a745")
            .add_yaxis("死亡", dead_data, color="#5d7092")
            .add_xaxis(y_data)
            .reversal_axis()
            .set_series_opts(label_opts=opts.LabelOpts(position="right"))
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"{province.name}城市疫情"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
                xaxis_opts=opts.AxisOpts(
                    type_="value",
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                yaxis_opts=opts.AxisOpts(type_="category"),
            )
        )
        
        return JsonResponse({
            "province": {
                "name": province.name,
                "short_name": province.short_name,
                "confirmed": province.confirmed_count,
                "cured": province.cured_count,
                "dead": province.dead_count,
                "comment": province.comment
            },
            "pie_options": pie_chart.dump_options(),
            "bar_options": bar_chart.dump_options(),
            "cities": city_data,
            "date": latest_date.strftime('%Y-%m-%d'),
        })
    
    return JsonResponse({
        "province": {
            "name": province.name,
            "short_name": province.short_name,
            "confirmed": province.confirmed_count,
            "cured": province.cured_count,
            "dead": province.dead_count,
            "comment": province.comment
        },
        "pie_options": pie_chart.dump_options(),
        "cities": city_data,
        "date": latest_date.strftime('%Y-%m-%d'),
    })

def province_list(request):
    """获取所有省份列表"""
    latest_date = Province.objects.aggregate(Max('data_date'))['data_date__max']
    
    provinces = Province.objects.filter(
        data_date=latest_date
    ).order_by('-confirmed_count')
    
    data = [
        {
            'name': p.name,
            'short_name': p.short_name,
            'confirmed': p.confirmed_count,
            'cured': p.cured_count,
            'dead': p.dead_count
        }
        for p in provinces
    ]
    
    return JsonResponse({
        'provinces': data,
        'date': latest_date.strftime('%Y-%m-%d')
    })

def available_dates(request):
    """获取可用的数据日期列表"""
    dates = Province.objects.values('data_date').distinct().order_by('data_date')
    date_list = [d['data_date'].strftime('%Y-%m-%d') for d in dates]
    
    return JsonResponse({
        'dates': date_list
    }) 