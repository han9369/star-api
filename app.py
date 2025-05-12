from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.object import Object
from flatlib import aspects
import json
from datetime import datetime
import pytz
import svgwrite
import math

app = Flask(__name__)
CORS(app)

# 星座名称映射
SIGN_NAMES = {
    'Aries': '白羊座',
    'Taurus': '金牛座',
    'Gemini': '双子座',
    'Cancer': '巨蟹座',
    'Leo': '狮子座',
    'Virgo': '处女座',
    'Libra': '天秤座',
    'Scorpio': '天蝎座',
    'Sagittarius': '射手座',
    'Capricorn': '摩羯座',
    'Aquarius': '水瓶座',
    'Pisces': '双鱼座'
}

# 行星名称映射
PLANET_NAMES = {
    const.SUN: '太阳',
    const.MOON: '月亮',
    const.MERCURY: '水星',
    const.VENUS: '金星',
    const.MARS: '火星',
    const.JUPITER: '木星',
    const.SATURN: '土星',
    const.URANUS: '天王星',
    const.NEPTUNE: '海王星',
    const.PLUTO: '冥王星',
    const.NORTH_NODE: '北交点',
    const.SOUTH_NODE: '南交点',
    const.ASC: '上升点'
}

# 相位类型映射
ASPECT_TYPES = {
    0: 'Conjunction',
    60: 'Sextile',
    90: 'Square',
    120: 'Trine',
    180: 'Opposition',
    -1: 'None'  # 添加-1表示没有相位
}

# 相位类型中文映射
ASPECT_TYPES_CN = {
    0: '合相',
    60: '六分相',
    90: '刑相',
    120: '三分相',
    180: '对分相',
    -1: '无相位'  # 添加-1表示没有相位
}

# 行星符号映射（SVG中显示用）
PLANET_SYMBOLS = {
    const.SUN: "☉",
    const.MOON: "☽",
    const.MERCURY: "☿",
    const.VENUS: "♀",
    const.MARS: "♂",
    const.JUPITER: "♃",
    const.SATURN: "♄",
    const.URANUS: "♅",
    const.NEPTUNE: "♆",
    const.PLUTO: "♇",
    const.NORTH_NODE: "☊",
    const.SOUTH_NODE: "☋",
    const.ASC: "ASC"
}

# 相位颜色映射
ASPECT_COLORS = {
    0: "#0000FF",    # 合相 - 蓝色
    60: "#00FF00",   # 六分相 - 绿色
    90: "#FF0000",   # 刑相 - 红色
    120: "#00FF00",  # 三分相 - 绿色
    180: "#FF0000",  # 对分相 - 红色
    -1: "#CCCCCC"    # 无相位 - 灰色
}

def calculate_chart(date, time, lat, lon):
    try:
        # 按照flatlib文档要求的格式: Datetime('2015/03/13', '17:00', '+00:00')
        # 将日期从 YYYY-MM-DD 转换为 YYYY/MM/DD
        date_str = date.replace('-', '/')
        time_str = time
        
        # 创建日期时间对象
        date_obj = Datetime(date_str, time_str)
        
        # 创建地理位置对象
        pos = GeoPos(lat, lon)
        
        # 创建星盘，使用所有支持的行星
        chart = Chart(date_obj, pos, IDs=const.LIST_OBJECTS)
        return chart
    except Exception as e:
        print(f"Debug - Error details: {str(e)}")  # 调试信息
        raise Exception(f"Date time format error: {str(e)}")

def get_planet_sign(planet, lang='en'):
    # 返回行星的基本信息，根据语言选择
    if lang == 'zh':
        # 中文版
        result = {
            '星座': SIGN_NAMES.get(planet.sign, planet.sign),
            '经度': round(planet.lon, 2)
        }
        
        # 如果有其他属性，安全地添加
        if hasattr(planet, 'lat'):
            result['纬度'] = round(planet.lat, 2)
    else:
        # 英文版
        result = {
            'sign': planet.sign,
            'longitude': round(planet.lon, 2)
        }
        
        # 如果有其他属性，安全地添加
        if hasattr(planet, 'lat'):
            result['latitude'] = round(planet.lat, 2)
        
    return result

def safe_get_planet(chart, planet_id, planet_name, lang='en'):
    try:
        planet = chart.get(planet_id)
        info = get_planet_sign(planet, lang)
        
        # 根据语言添加行星名称
        if lang == 'zh':
            info['名称'] = PLANET_NAMES.get(planet_id, planet_name)
        else:
            info['name'] = planet_name
            
        return info
    except Exception as e:
        error_msg = f"Cannot get planet {planet_id}: {str(e)}"
        print(error_msg)
        if lang == 'zh':
            return {'错误': error_msg}
        else:
            return {'error': error_msg}

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        date = data.get('date')
        time = data.get('time')
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        lang = data.get('language', 'en')  # 默认使用英文
        
        # 添加调试信息，检查原始语言参数
        print(f"Debug - Original language parameter: {lang}")
        
        # 如果语言是中文，使用'zh'
        if lang.lower() in ['zh', 'cn', 'chinese', 'zh-cn', 'zhcn']:
            lang = 'zh'
            print("Debug - Language set to 'zh'")
        else:
            lang = 'en'  # 其他情况默认使用英文
            print("Debug - Language set to 'en'")

        print(f"Debug - Input data: date={date}, time={time}, lat={lat}, lon={lon}, lang={lang}")

        # 计算星盘
        chart = calculate_chart(date, time, lat, lon)

        # 定义要获取的行星
        planet_definitions = [
            (const.SUN, 'Sun' if lang == 'en' else '太阳'),
            (const.MOON, 'Moon' if lang == 'en' else '月亮'),
            (const.ASC, 'Ascendant' if lang == 'en' else '上升点'),
            (const.VENUS, 'Venus' if lang == 'en' else '金星'),
            (const.MARS, 'Mars' if lang == 'en' else '火星'),
            (const.MERCURY, 'Mercury' if lang == 'en' else '水星'),
            (const.NORTH_NODE, 'North Node' if lang == 'en' else '北交点'),
            (const.JUPITER, 'Jupiter' if lang == 'en' else '木星'),
            (const.SATURN, 'Saturn' if lang == 'en' else '土星')
        ]
        
        # 获取行星信息
        planets = []
        for planet_id, planet_name in planet_definitions:
            planet_info = safe_get_planet(chart, planet_id, planet_name, lang)
            planets.append(planet_info)

        # 计算相位
        aspects_list = []
        try:
            planet_ids = [item[0] for item in planet_definitions]
            
            for i, p1_id in enumerate(planet_ids):
                for j, p2_id in enumerate(planet_ids):
                    if i < j:  # 避免重复计算
                        try:
                            aspect = aspects.getAspect(chart.get(p1_id), chart.get(p2_id), const.MAJOR_ASPECTS)
                            aspect_type = aspect.type if aspect else -1  # 如果没有相位，设为-1
                            orb = aspect.orb if aspect else 0
                            
                            if lang == 'zh':
                                # 中文版
                                aspect_info = {
                                    '行星1': planet_definitions[i][1],
                                    '行星2': planet_definitions[j][1],
                                    '类型': aspect_type,
                                    '相位名称': ASPECT_TYPES_CN.get(aspect_type, f"{aspect_type}°"),
                                    '误差': round(orb, 2)
                                }
                            else:
                                # 英文版
                                aspect_info = {
                                    'planet1': planet_definitions[i][1],
                                    'planet2': planet_definitions[j][1],
                                    'type': aspect_type,
                                    'type_name': ASPECT_TYPES.get(aspect_type, f"{aspect_type}°"),
                                    'orb': round(orb, 2)
                                }
                            aspects_list.append(aspect_info)
                        except Exception as e:
                            error_msg = f"Aspect calculation error ({p1_id}-{p2_id}): {str(e)}"
                            print(error_msg)
        except Exception as e:
            error_msg = f"Main aspect loop error: {str(e)}"
            print(error_msg)

        # 添加调试信息，检查最终语言设置
        print(f"Debug - Final language before response: {lang}")
        
        # 根据语言返回结果
        if lang == 'zh':
            print("Debug - Returning Chinese response")
            response = {
                '成功': True,
                '日期': date,
                '时间': time,
                '纬度': lat,
                '经度': lon,
                '行星': planets,
                '相位': aspects_list
            }
            return jsonify(response)
        else:
            print("Debug - Returning English response")
            response = {
                'success': True,
                'date': date,
                'time': time,
                'latitude': lat,
                'longitude': lon,
                'planets': planets,
                'aspects': aspects_list
            }
            return jsonify(response)

    except Exception as e:
        error_msg = str(e)
        print(f"Debug - API error: {error_msg}")
        
        if lang == 'zh':
            return jsonify({
                '成功': False,
                '错误': error_msg
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400

@app.route('/api/calculate_zh', methods=['POST'])
def calculate_zh():
    """中文版API接口"""
    try:
        data = request.get_json()
        date = data.get('date')
        time = data.get('time')
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        print(f"Debug - 中文API: date={date}, time={time}, lat={lat}, lon={lon}")

        # 计算星盘
        chart = calculate_chart(date, time, lat, lon)

        # 定义要获取的行星
        planet_definitions = [
            (const.SUN, '太阳'),
            (const.MOON, '月亮'),
            (const.ASC, '上升点'),
            (const.VENUS, '金星'),
            (const.MARS, '火星'),
            (const.MERCURY, '水星'),
            (const.NORTH_NODE, '北交点'),
            (const.JUPITER, '木星'),
            (const.SATURN, '土星')
        ]
        
        # 获取行星信息
        planets = []
        for planet_id, planet_name in planet_definitions:
            planet_info = safe_get_planet(chart, planet_id, planet_name, 'zh')
            planets.append(planet_info)

        # 计算相位
        aspects_list = []
        try:
            planet_ids = [item[0] for item in planet_definitions]
            
            for i, p1_id in enumerate(planet_ids):
                for j, p2_id in enumerate(planet_ids):
                    if i < j:  # 避免重复计算
                        try:
                            aspect = aspects.getAspect(chart.get(p1_id), chart.get(p2_id), const.MAJOR_ASPECTS)
                            aspect_type = aspect.type if aspect else -1  # 如果没有相位，设为-1
                            orb = aspect.orb if aspect else 0
                            
                            # 中文版
                            aspect_info = {
                                '行星1': planet_definitions[i][1],
                                '行星2': planet_definitions[j][1],
                                '类型': aspect_type,
                                '相位名称': ASPECT_TYPES_CN.get(aspect_type, f"{aspect_type}°"),
                                '误差': round(orb, 2)
                            }
                            aspects_list.append(aspect_info)
                        except Exception as e:
                            error_msg = f"相位计算错误 ({p1_id}-{p2_id}): {str(e)}"
                            print(error_msg)
        except Exception as e:
            error_msg = f"相位主循环错误: {str(e)}"
            print(error_msg)

        # 返回中文结果
        print("Debug - 返回中文响应")
        response = {
            '成功': True,
            '日期': date,
            '时间': time,
            '纬度': lat,
            '经度': lon,
            '行星': planets,
            '相位': aspects_list
        }
        return jsonify(response)

    except Exception as e:
        error_msg = str(e)
        print(f"Debug - API错误: {error_msg}")
        
        return jsonify({
            '成功': False,
            '错误': error_msg
        }), 400

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'name': 'Astrology API',
        'version': '1.0.0',
        'endpoints': {
            '/api/calculate': 'POST - Calculate natal chart based on date, time and location',
            '/api/calculate_zh': 'POST - 中文版API，根据日期、时间和位置计算星盘',
            '/api/chart_svg': 'POST - Generate SVG chart image',
            '/api/chart': 'POST - Generate SVG chart image (alias of /api/chart_svg)',
            '/api/combined': 'POST - Get both chart data and SVG image in one response'
        },
        'usage': {
            'method': 'POST',
            'url': '/api/calculate',
            'body': {
                'date': 'YYYY-MM-DD',
                'time': 'HH:MM:SS',
                'latitude': 'latitude',
                'longitude': 'longitude',
                'language': 'en (default) or zh'
            }
        },
        '使用说明': {
            '方法': 'POST',
            '地址': '/api/calculate_zh',
            '请求体': {
                'date': 'YYYY-MM-DD 日期',
                'time': 'HH:MM:SS 时间',
                'latitude': '纬度',
                'longitude': '经度'
            }
        },
        'SVG图表': {
            '方法': 'POST',
            '地址': '/api/chart_svg 或 /api/chart',
            '请求体': {
                'date': 'YYYY-MM-DD',
                'time': 'HH:MM:SS',
                'latitude': 'latitude',
                'longitude': 'longitude',
                'language': 'en (default) or zh'
            },
            '返回': 'SVG格式的星盘图'
        },
        '组合数据': {
            '方法': 'POST',
            '地址': '/api/combined',
            '请求体': {
                'date': 'YYYY-MM-DD',
                'time': 'HH:MM:SS',
                'latitude': 'latitude',
                'longitude': 'longitude',
                'language': 'en (default) or zh'
            },
            '返回': 'JSON格式的星盘数据和SVG格式的星盘图'
        }
    })

def generate_chart_svg(chart, lang='en'):
    # 创建SVG画布 - 修改为透明背景
    dwg = svgwrite.Drawing(profile='tiny', size=('720px', '720px'))
    
    # 定义中心点和半径
    center_x, center_y = 360, 360  # 将中心点调整为画布中心
    inner_circle_radius = 216  # 内圈半径
    zodiac_inner_radius = 216  # 星座圈内半径
    zodiac_outer_radius = 261  # 星座圈外半径
    house_inner_radius = 261   # 宫位圈内半径
    house_outer_radius = 288   # 宫位圈外半径
    
    # 获取上升点的度数
    asc = chart.get(const.ASC)
    asc_longitude = asc.lon
    
    # 收集行星数据
    planets_data = []
    planet_definitions = [
        (const.SUN, "Sun" if lang == 'en' else '太阳'),
        (const.MOON, "Moon" if lang == 'en' else '月亮'),
        (const.ASC, "Ascendant" if lang == 'en' else '上升点'),
        (const.VENUS, "Venus" if lang == 'en' else '金星'),
        (const.MARS, "Mars" if lang == 'en' else '火星'),
        (const.MERCURY, "Mercury" if lang == 'en' else '水星'),
        (const.NORTH_NODE, "N.Node" if lang == 'en' else '北交点'),  # 缩短名称以避免文字拥挤
        (const.JUPITER, "Jupiter" if lang == 'en' else '木星'),
        (const.SATURN, "Saturn" if lang == 'en' else '土星')
    ]
    
    # 收集所有行星的位置和数据
    for planet_id, planet_name in planet_definitions:
        try:
            planet = chart.get(planet_id)
            longitude = planet.lon
            
            # 转换为SVG坐标 - 使用动态半径来避免行星重叠
            planet_rad = math.radians(90 - longitude)
            planet_x = center_x + inner_circle_radius * 0.7 * math.cos(planet_rad)
            planet_y = center_y - inner_circle_radius * 0.7 * math.sin(planet_rad)
            
            planets_data.append({
                'id': planet_id,
                'name': planet_name,
                'longitude': longitude,
                'x': planet_x,
                'y': planet_y,
                'rad': planet_rad
            })
        except Exception as e:
            print(f"Error collecting planet {planet_id}: {e}")
    
    # 检测并调整重叠的行星
    def distance(p1, p2):
        return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)
    
    # 调整行星位置以避免重叠
    min_distance = 25  # 最小行星间距
    for i, p1 in enumerate(planets_data):
        for j, p2 in enumerate(planets_data):
            if i < j:  # 避免重复比较
                dist = distance(p1, p2)
                if dist < min_distance:
                    # 计算需要调整的距离
                    adjust = (min_distance - dist) / 2
                    
                    # 计算方向向量
                    dx = p2['x'] - p1['x']
                    dy = p2['y'] - p1['y']
                    mag = math.sqrt(dx*dx + dy*dy)
                    
                    if mag > 0:  # 防止除以零
                        # 标准化
                        dx /= mag
                        dy /= mag
                        
                        # 调整行星1向中心移动
                        radius_p1 = math.sqrt((p1['x'] - center_x)**2 + (p1['y'] - center_y)**2)
                        angle_p1 = math.atan2(center_y - p1['y'], p1['x'] - center_x)
                        new_radius_p1 = radius_p1 - adjust
                        p1['x'] = center_x + new_radius_p1 * math.cos(angle_p1)
                        p1['y'] = center_y - new_radius_p1 * math.sin(angle_p1)
                        
                        # 调整行星2向外移动
                        radius_p2 = math.sqrt((p2['x'] - center_x)**2 + (p2['y'] - center_y)**2)
                        angle_p2 = math.atan2(center_y - p2['y'], p2['x'] - center_x)
                        new_radius_p2 = radius_p2 + adjust
                        p2['x'] = center_x + new_radius_p2 * math.cos(angle_p2)
                        p2['y'] = center_y - new_radius_p2 * math.sin(angle_p2)
    
    # 绘制相位线（只显示重要相位且忽略太弱的相位）
    aspect_lines = []  # 保存相位线信息以便稍后绘制
    for i, p1 in enumerate(planets_data):
        for j, p2 in enumerate(planets_data):
            if i < j:  # 避免重复
                try:
                    # 获取行星对象
                    planet1 = chart.get(p1['id'])
                    planet2 = chart.get(p2['id'])
                    
                    # 计算相位
                    aspect = aspects.getAspect(planet1, planet2, const.MAJOR_ASPECTS)
                    
                    # 增加容错度至10度，以显示更多的相位线
                    if aspect and aspect.type in [0, 60, 90, 120, 180] and abs(aspect.orb) < 10:
                        aspect_type = aspect.type
                        
                        # 设置相位线样式
                        if aspect_type == 0:  # 合相
                            color = "#0000FF"  # 蓝色
                            dash = None
                        elif aspect_type == 60 or aspect_type == 120:  # 六分相或三分相
                            color = "#00AA00"  # 绿色
                            dash = None
                        elif aspect_type == 90 or aspect_type == 180:  # 四分相或对分相
                            color = "#FF0000"  # 红色
                            dash = "5,5"
                        else:
                            color = "#777777"  # 灰色
                            dash = None
                            
                        aspect_lines.append({
                            'start': (p1['x'], p1['y']),
                            'end': (p2['x'], p2['y']),
                            'color': color,
                            'dash': dash
                        })
                    
                    # 为了增加更多线条，添加次要相位计算
                    # 尝试计算次要相位：30°(半六分相), 45°(半刑相), 135°(盔甲), 150°(似六分相)
                    minor_aspects = [45, 135]  # 只保留半刑相和盔甲相(红色系)，移除30°和150°(绿色系)
                    
                    for minor_type in minor_aspects:
                        # 计算两个行星之间的角度差
                        angle_diff = abs(planet1.lon - planet2.lon) % 360
                        if angle_diff > 180:
                            angle_diff = 360 - angle_diff
                            
                        # 检查是否接近次要相位
                        orb = abs(angle_diff - minor_type)
                        if orb <= 3:  # 较小的容错度，避免太多线条
                            # 只保留半刑相和盔甲相(红色系)
                            color = "#CC4444"  # 更亮的红色
                            dash = "3,3"
                            
                            aspect_lines.append({
                                'start': (p1['x'], p1['y']),
                                'end': (p2['x'], p2['y']),
                                'color': color,
                                'dash': dash
                            })
                except Exception as e:
                    print(f"Error calculating aspect between {p1['name']} and {p2['name']}: {e}")
    
    # 星座背景颜色
    # 元素顺序：火、土、风、水
    ELEMENT_COLORS = {
        "fire": "#ffccaa",  # 火象星座 - 浅橙色 (白羊、狮子、射手)
        "earth": "#d2b48c", # 土象星座 - 棕褐色 (金牛、处女、摩羯)
        "air": "#bbddff",   # 风象星座 - 浅蓝色 (双子、天秤、水瓶)
        "water": "#aadddd"  # 水象星座 - 青绿色 (巨蟹、天蝎、双鱼)
    }
    
    # 星座元素对应关系
    SIGN_ELEMENTS = {
        'Aries': 'fire', 'Leo': 'fire', 'Sagittarius': 'fire',
        'Taurus': 'earth', 'Virgo': 'earth', 'Capricorn': 'earth',
        'Gemini': 'air', 'Libra': 'air', 'Aquarius': 'air',
        'Cancer': 'water', 'Scorpio': 'water', 'Pisces': 'water'
    }
    
    # 绘制主要圆环
    # 最外层宫位圈外圆
    dwg.add(dwg.circle(center=(center_x, center_y), r=house_outer_radius, 
                       fill='none', stroke='black', stroke_width=2))
    
    # 宫位圈内圆/星座圈外圆
    dwg.add(dwg.circle(center=(center_x, center_y), r=house_inner_radius, 
                       fill='none', stroke='black', stroke_width=1))
    
    # 内圈 - 行星相位圈 (去掉了星座圈内圆，因为现在与内圈重叠)
    dwg.add(dwg.circle(center=(center_x, center_y), r=inner_circle_radius, 
                       fill='white', stroke='black', stroke_width=1))
    
    # 计算宫位位置（基于上升点的位置）
    # 宫位1从上升点(ASC)开始
    houses_positions = []
    for i in range(12):
        house_start = (asc_longitude + i * 30) % 360
        houses_positions.append(house_start)
    
    # 先绘制宫位分隔线
    for house_start in houses_positions:
        angle_rad = math.radians(90 - house_start)
        
        # 从内圈到宫位外圈的线
        x1 = center_x + zodiac_inner_radius * math.cos(angle_rad)
        y1 = center_y - zodiac_inner_radius * math.sin(angle_rad)
        x2 = center_x + house_outer_radius * math.cos(angle_rad)
        y2 = center_y - house_outer_radius * math.sin(angle_rad)
        
        dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), 
                        stroke='black', stroke_width=0.7))
    
    # 绘制宫位数字
    for i, house_start in enumerate(houses_positions):
        house_number = i + 1  # 宫位编号从1开始
        house_end = (house_start + 30) % 360
        house_mid = (house_start + 15) % 360
        
        # 宫位数字位置
        mid_angle_rad = math.radians(90 - house_mid)
        label_radius = (house_inner_radius + house_outer_radius) / 2
        
        label_x = center_x + label_radius * math.cos(mid_angle_rad)
        label_y = center_y - label_radius * math.sin(mid_angle_rad)
        
        # 根据宫位类型选择颜色
        house_color = '#333333'  # 默认灰色
        if house_number in [1, 5, 9]:  # 火相宫
            house_color = '#FF3333'  # 红色
        elif house_number in [2, 6, 10]:  # 土相宫
            house_color = '#AA6622'  # 土黄色
        elif house_number in [3, 7, 11]:  # 风相宫
            house_color = '#3366FF'  # 蓝色
        elif house_number in [4, 8, 12]:  # 水相宫
            house_color = '#33AAAA'  # 青色
            
        dwg.add(dwg.text(str(house_number), 
                        insert=(label_x, label_y),
                        fill=house_color, font_size='11px', font_weight='bold',
                        text_anchor='middle'))
    
    # 计算星座和宫位位置
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    # 绘制星座分隔线
    for i in range(12):
        angle = i * 30
        angle_rad = math.radians(90 - angle)
        
        # 从星座内圈到星座外圈的线
        x1 = center_x + zodiac_inner_radius * math.cos(angle_rad)
        y1 = center_y - zodiac_inner_radius * math.sin(angle_rad)
        x2 = center_x + zodiac_outer_radius * math.cos(angle_rad)
        y2 = center_y - zodiac_outer_radius * math.sin(angle_rad)
        
        dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), 
                        stroke='black', stroke_width=0.5))
    
    # 绘制星座区域（完全填充扇形）
    for i in range(12):
        # 星座起始角度 (0° 是白羊座起点)
        start_angle = i * 30
        end_angle = (i + 1) * 30
        
        # 获取星座元素
        sign = signs[i]
        element = SIGN_ELEMENTS[sign]
        fill_color = ELEMENT_COLORS[element]
        
        # 创建星座区域路径
        start_rad = math.radians(90 - start_angle)
        end_rad = math.radians(90 - end_angle)
        
        # 创建扇区路径
        path_data = f"M {center_x + zodiac_inner_radius * math.cos(start_rad)},{center_y - zodiac_inner_radius * math.sin(start_rad)} "
        path_data += f"L {center_x + zodiac_outer_radius * math.cos(start_rad)},{center_y - zodiac_outer_radius * math.sin(start_rad)} "
        path_data += f"A {zodiac_outer_radius},{zodiac_outer_radius} 0 0,1 {center_x + zodiac_outer_radius * math.cos(end_rad)},{center_y - zodiac_outer_radius * math.sin(end_rad)} "
        path_data += f"L {center_x + zodiac_inner_radius * math.cos(end_rad)},{center_y - zodiac_inner_radius * math.sin(end_rad)} "
        path_data += f"A {zodiac_inner_radius},{zodiac_inner_radius} 0 0,0 {center_x + zodiac_inner_radius * math.cos(start_rad)},{center_y - zodiac_inner_radius * math.sin(start_rad)} Z"
        
        # 添加星座区域，带颜色填充
        dwg.add(dwg.path(d=path_data, fill=fill_color, stroke='black', stroke_width=0.5))
        
        # 添加星座名称
        mid_angle = (start_angle + end_angle) / 2
        mid_angle_rad = math.radians(90 - mid_angle)
        
        # 计算星座名称位置 - 在星座区域中心点
        sign_radius = (zodiac_inner_radius + zodiac_outer_radius) / 2
        sign_x = center_x + sign_radius * math.cos(mid_angle_rad)
        sign_y = center_y - sign_radius * math.sin(mid_angle_rad)
        
        # 对于长名称星座，使用较小字体
        font_size = '9px'
        if sign in ['Sagittarius', 'Capricorn']:
            font_size = '7px'
            
        dwg.add(dwg.text(sign, 
                        insert=(sign_x, sign_y),
                        fill='black', font_size=font_size,
                        text_anchor='middle'))
    
    # 绘制内圈的径向线和同心圆
    # 首先绘制内圈的同心圆 (3个同心圆，分别在内圈的1/3和2/3处)
    inner_circle_1 = inner_circle_radius * 0.25  # 从0.33减小到0.25
    inner_circle_2 = inner_circle_radius * 0.5   # 从0.67减小到0.5
    
    # 绘制内圈环上的度数标记和径向线
    for i in range(0, 360, 30):
        rad = math.radians(90 - i)
        
        # 绘制径向线 (从中心到内圈边界)
        dwg.add(dwg.line(
            start=(center_x, center_y),
            end=(center_x + inner_circle_radius * math.cos(rad), center_y - inner_circle_radius * math.sin(rad)),
            stroke='#777777',
            stroke_width='0.5'
        ))
        
        # 角度标记放在图中，与截图相同的位置
        degree_label_radius = inner_circle_radius * 0.85
        x1 = center_x + degree_label_radius * math.cos(rad)
        y1 = center_y - degree_label_radius * math.sin(rad)
        
        # 添加度数标记
        dwg.add(dwg.text(f"{i}°", 
                        insert=(x1, y1),
                        fill='#777777', font_size='8px',
                        text_anchor='middle'))
    
    # 现在绘制所有相位线
    for line in aspect_lines:
        if line['dash']:
            dwg.add(dwg.line(
                start=line['start'],
                end=line['end'],
                stroke=line['color'],
                stroke_width=1.2,  # 加粗虚线
                stroke_dasharray=line['dash']
            ))
        else:
            dwg.add(dwg.line(
                start=line['start'],
                end=line['end'],
                stroke=line['color'],
                stroke_width=1.2  # 加粗实线
            ))
    
    # 绘制行星符号
    for planet in planets_data:
        try:
            planet_x = planet['x']
            planet_y = planet['y']
            
            # 添加行星背景圆圈
            circle_radius = 9
            # ASC用稍小一点的圆圈，避免超出边框
            if planet['id'] == const.ASC:
                circle_radius = 9  # 从7增加到8，扩大ASC圆圈
                
            dwg.add(dwg.circle(center=(planet_x, planet_y), r=circle_radius,
                             fill='white', stroke='black', stroke_width=1))
            
            # 添加行星符号
            symbol = PLANET_SYMBOLS.get(planet['id'], planet['name'][0])
            
            # 根据行星类型选择颜色
            color = "#000000"  # 默认黑色
            if planet['id'] in [const.SUN, const.MARS]:
                color = "#FF0000"  # 红色系
            elif planet['id'] in [const.MOON, const.VENUS]:
                color = "#009900"  # 绿色系
            elif planet['id'] in [const.MERCURY, const.JUPITER]:
                color = "#0000FF"  # 蓝色系
            
            # ASC用较小的字体
            font_size = '12px'
            y_offset = 4
            if planet['id'] == const.ASC:
                font_size = '8px'  # 从9px减小到8px
                y_offset = 3
                
            dwg.add(dwg.text(symbol, insert=(planet_x, planet_y+y_offset),
                          fill=color, font_size=font_size,
                          text_anchor='middle', font_weight='bold'))
        except Exception as e:
            print(f"Error plotting planet {planet['name']}: {e}")
    
    # 修改行星度数标签显示方式
    # 创建标签组以检测和避免重叠
    planet_labels = []
    
    for planet in planets_data:
        try:
            # 简化行星名称
            simple_name = planet['name']
            if simple_name == "Ascendant":
                simple_name = "Asc"
            elif simple_name == "Jupiter":
                simple_name = "Jup"
            elif simple_name == "Mercury":
                simple_name = "Mer"
            elif simple_name == "Saturn":
                simple_name = "Sat"
            elif simple_name == "North_Node":
                simple_name = "N.Node"
            
            # 在图表外围显示行星信息
            angle_deg = planet['longitude']
            # 格式化显示度数
            degree_text = f"{simple_name}: {int(round(angle_deg))}°"
            
            # 计算标签位置，放在最外圈，调整距离防止文字超出图表边界
            label_rad = math.radians(90 - angle_deg)
            label_distance = house_outer_radius + 15  # 从25减小到15，使文字更靠近星盘
            
            # 处理标签间距和位置
            text_anchor = 'middle'
            label_y_offset = 0
            
            # 根据角度调整文本对齐方式和位置，使其更好地适应图表范围
            if angle_deg >= 0 and angle_deg < 90:  # 右上象限
                if angle_deg < 45:
                    text_anchor = 'start'
                    label_y_offset = -5
                else:
                    text_anchor = 'start'
                    label_y_offset = 0
            elif angle_deg >= 90 and angle_deg < 180:  # 右下象限
                if angle_deg < 135:
                    text_anchor = 'start'
                    label_y_offset = 5
                else:
                    text_anchor = 'start'
                    label_y_offset = 10
            elif angle_deg >= 180 and angle_deg < 270:  # 左下象限
                if angle_deg < 225:
                    text_anchor = 'end'
                    label_y_offset = 5
                else:
                    text_anchor = 'end'
                    label_y_offset = 0
            else:  # 左上象限
                if angle_deg < 315:
                    text_anchor = 'end'
                    label_y_offset = -5
                else:
                    text_anchor = 'end'
                    label_y_offset = -10
            
            label_x = center_x + label_distance * math.cos(label_rad)
            label_y = center_y - label_distance * math.sin(label_rad) + label_y_offset
            
            # 保存标签数据以检测重叠
            planet_labels.append({
                'text': degree_text,
                'x': label_x,
                'y': label_y,
                'anchor': text_anchor,
                'angle': angle_deg
            })
        except Exception as e:
            print(f"Error preparing planet label {planet['name']}: {e}")
    
    # 调整标签位置以避免重叠
    def label_overlaps(l1, l2):
        # 计算两个标签之间的距离
        dx = l1['x'] - l2['x']
        dy = l1['y'] - l2['y']
        distance = math.sqrt(dx*dx + dy*dy)
        
        # 根据文本长度估计标签宽度
        l1_width = len(l1['text']) * 5  # 每个字符约5像素宽
        l2_width = len(l2['text']) * 5
        
        # 水平对齐的标签需要更多空间
        if l1['anchor'] == l2['anchor']:
            min_distance = 15  # 垂直最小间距
        else:
            min_distance = 10
            
        return distance < min_distance
    
    # 遍历所有标签对，调整重叠标签
    for i, l1 in enumerate(planet_labels):
        for j, l2 in enumerate(planet_labels):
            if i < j and label_overlaps(l1, l2):
                # 如果角度相近，垂直错开
                angle_diff = abs(l1['angle'] - l2['angle'])
                if angle_diff < 15 or angle_diff > 345:
                    # 角度相近的标签，垂直错开
                    l1['y'] -= 12
                    l2['y'] += 12
                else:
                    # 角度不同的标签，调整距离
                    if l1['angle'] > l2['angle']:
                        # 稍微调整两个标签的位置
                        l1_rad = math.radians(90 - (l1['angle'] + 5))
                        l2_rad = math.radians(90 - (l2['angle'] - 5))
                        
                        label_distance = house_outer_radius + 15
                        l1['x'] = center_x + label_distance * math.cos(l1_rad)
                        l1['y'] = center_y - label_distance * math.sin(l1_rad) + l1.get('label_y_offset', 0)
                        
                        l2['x'] = center_x + label_distance * math.cos(l2_rad)
                        l2['y'] = center_y - label_distance * math.sin(l2_rad) + l2.get('label_y_offset', 0)
    
    # 添加调整后的标签
    for label in planet_labels:
        dwg.add(dwg.text(label['text'], insert=(label['x'], label['y']),
                    fill='black', font_size='8px',
                    text_anchor=label['anchor']))
    
    # 返回SVG字符串
    return dwg.tostring()

@app.route('/api/chart_svg', methods=['POST'])
def chart_svg():
    # 在函数开始就设置默认值
    lang = 'en'  # 默认使用英文
    try:
        data = request.get_json()
        date = data.get('date')
        time = data.get('time')
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        # 如果请求中有language参数，则更新lang变量
        if 'language' in data:
            lang = data.get('language', 'en')
        
        # 如果语言是中文，使用'zh'
        if lang and lang.lower() in ['zh', 'cn', 'chinese', 'zh-cn', 'zhcn']:
            lang = 'zh'
        else:
            lang = 'en'  # 其他情况默认使用英文
        
        # 计算星盘
        chart = calculate_chart(date, time, lat, lon)
        
        # 生成SVG
        svg_content = generate_chart_svg(chart, lang)
        
        # 返回SVG响应
        return Response(svg_content, mimetype='image/svg+xml')
        
    except Exception as e:
        error_msg = str(e)
        print(f"Debug - API error: {error_msg}")
        
        if lang == 'zh':
            return jsonify({
                '成功': False,
                '错误': error_msg
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400

# 添加别名路由'/api/chart'，功能与'/api/chart_svg'相同
@app.route('/api/chart', methods=['POST'])
def chart():
    return chart_svg()

@app.route('/api/combined', methods=['POST'])
def combined_data():
    # 在函数开始就设置默认值
    lang = 'en'  # 默认使用英文
    try:
        data = request.get_json()
        date = data.get('date')
        time = data.get('time')
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        # 如果请求中有language参数，则更新lang变量
        if 'language' in data:
            lang = data.get('language', 'en')
        
        # 如果语言是中文，使用'zh'
        if lang and lang.lower() in ['zh', 'cn', 'chinese', 'zh-cn', 'zhcn']:
            lang = 'zh'
        else:
            lang = 'en'  # 其他情况默认使用英文
        
        # 计算星盘
        chart = calculate_chart(date, time, lat, lon)
        
        # 生成SVG
        svg_content = generate_chart_svg(chart, lang)
        
        # 获取行星和相位数据
        # 定义要获取的行星
        planet_definitions = [
            (const.SUN, 'Sun' if lang == 'en' else '太阳'),
            (const.MOON, 'Moon' if lang == 'en' else '月亮'),
            (const.ASC, 'Ascendant' if lang == 'en' else '上升点'),
            (const.VENUS, 'Venus' if lang == 'en' else '金星'),
            (const.MARS, 'Mars' if lang == 'en' else '火星'),
            (const.MERCURY, 'Mercury' if lang == 'en' else '水星'),
            (const.NORTH_NODE, 'North Node' if lang == 'en' else '北交点'),
            (const.JUPITER, 'Jupiter' if lang == 'en' else '木星'),
            (const.SATURN, 'Saturn' if lang == 'en' else '土星')
        ]
        
        # 获取行星信息
        planets = []
        for planet_id, planet_name in planet_definitions:
            planet_info = safe_get_planet(chart, planet_id, planet_name, lang)
            planets.append(planet_info)

        # 计算相位
        aspects_list = []
        try:
            planet_ids = [item[0] for item in planet_definitions]
            
            for i, p1_id in enumerate(planet_ids):
                for j, p2_id in enumerate(planet_ids):
                    if i < j:  # 避免重复计算
                        try:
                            aspect = aspects.getAspect(chart.get(p1_id), chart.get(p2_id), const.MAJOR_ASPECTS)
                            aspect_type = aspect.type if aspect else -1  # 如果没有相位，设为-1
                            orb = aspect.orb if aspect else 0
                            
                            if lang == 'zh':
                                # 中文版
                                aspect_info = {
                                    '行星1': planet_definitions[i][1],
                                    '行星2': planet_definitions[j][1],
                                    '类型': aspect_type,
                                    '相位名称': ASPECT_TYPES_CN.get(aspect_type, f"{aspect_type}°"),
                                    '误差': round(orb, 2)
                                }
                            else:
                                # 英文版
                                aspect_info = {
                                    'planet1': planet_definitions[i][1],
                                    'planet2': planet_definitions[j][1],
                                    'type': aspect_type,
                                    'type_name': ASPECT_TYPES.get(aspect_type, f"{aspect_type}°"),
                                    'orb': round(orb, 2)
                                }
                            aspects_list.append(aspect_info)
                        except Exception as e:
                            error_msg = f"Aspect calculation error ({p1_id}-{p2_id}): {str(e)}"
                            print(error_msg)
        except Exception as e:
            error_msg = f"Main aspect loop error: {str(e)}"
            print(error_msg)
        
        # 准备返回数据
        if lang == 'zh':
            response_data = {
                '成功': True,
                '日期': date,
                '时间': time,
                '纬度': lat,
                '经度': lon,
                '行星': planets,
                '相位': aspects_list,
                '星盘': svg_content
            }
        else:
            response_data = {
                'success': True,
                'date': date,
                'time': time,
                'latitude': lat,
                'longitude': lon,
                'planets': planets,
                'aspects': aspects_list,
                'chart': svg_content
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = str(e)
        print(f"Debug - API error: {error_msg}")
        
        if lang == 'zh':
            return jsonify({
                '成功': False,
                '错误': error_msg
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001) 
