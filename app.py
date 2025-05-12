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
    # 创建SVG画布
    dwg = svgwrite.Drawing(profile='tiny', size=('600px', '600px'))
    
    # 定义中心点和半径
    center_x, center_y = 300, 300
    radius = 250
    
    # 绘制外圈（黑底）
    dwg.add(dwg.circle(center=(center_x, center_y), r=radius, 
                     fill='black', stroke='white', stroke_width=2))
    
    # 绘制内圈（更小的圆）
    inner_radius = radius * 0.7
    dwg.add(dwg.circle(center=(center_x, center_y), r=inner_radius, 
                     fill='none', stroke='white', stroke_width=1))
    
    # 绘制内圈的径向线和同心圆
    # 首先绘制内圈的同心圆 (3个同心圆，分别在内圈的1/3和2/3处)
    inner_circle_radius = radius * 0.5
    inner_circle_1 = inner_circle_radius * 0.25
    inner_circle_2 = inner_circle_radius * 0.5
    
    # 绘制星座分割线和标签（12宫）
    for i in range(12):
        angle = i * 30
        rad = math.radians(angle)
        x1 = center_x + radius * math.sin(rad)
        y1 = center_y - radius * math.cos(rad)
        
        # 画线
        dwg.add(dwg.line(start=(center_x, center_y), end=(x1, y1),
                        stroke='white', stroke_width=1))
        
        # 添加星座标签
        label_angle = math.radians(angle + 15)  # 位于每个星座的中间
        label_x = center_x + (radius + 20) * math.sin(label_angle)
        label_y = center_y - (radius + 20) * math.cos(label_angle)
        
        # 获取星座名
        sign_index = (i + 10) % 12  # 调整起始点为白羊座(0°)
        signs = list(SIGN_NAMES.values())
        
        dwg.add(dwg.text(signs[sign_index], 
                        insert=(label_x, label_y),
                        fill='white', font_size='12px',
                        text_anchor='middle'))
        
        # 添加度数标记
        degree_text = f"{(i * 30)}°"
        degree_x = center_x + (radius - 15) * math.sin(rad)
        degree_y = center_y - (radius - 15) * math.cos(rad)
        dwg.add(dwg.text(degree_text,
                        insert=(degree_x, degree_y),
                        fill='#AAAAAA', font_size='10px',
                        text_anchor='middle'))
    
    # 收集行星数据
    planets_data = []
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
    
    # 首先绘制相位线（这样行星符号会在上面）
    for i, (p1_id, p1_name) in enumerate(planet_definitions):
        for j, (p2_id, p2_name) in enumerate(planet_definitions):
            if i < j:  # 避免重复
                try:
                    # 获取行星对象
                    planet1 = chart.get(p1_id)
                    planet2 = chart.get(p2_id)
                    
                    # 计算相位
                    aspect = aspects.getAspect(planet1, planet2, const.MAJOR_ASPECTS)
                    
                    if aspect:
                        aspect_type = aspect.type
                        
                        # 计算行星位置
                        p1_rad = math.radians(planet1.lon)
                        p2_rad = math.radians(planet2.lon)
                        
                        p1_x = center_x + radius * 0.8 * math.sin(p1_rad)
                        p1_y = center_y - radius * 0.8 * math.cos(p1_rad)
                        
                        p2_x = center_x + radius * 0.8 * math.sin(p2_rad)
                        p2_y = center_y - radius * 0.8 * math.cos(p2_rad)
                        
                        # 绘制相位线
                        color = ASPECT_COLORS.get(aspect_type, "#FFFFFF")
                        stroke_dasharray = "5,5" if aspect_type in [90, 180] else None
                        
                        if stroke_dasharray:
                            dwg.add(dwg.line(
                                start=(p1_x, p1_y),
                                end=(p2_x, p2_y),
                                stroke=color,
                                stroke_width=1,
                                stroke_dasharray=stroke_dasharray
                            ))
                        else:
                            dwg.add(dwg.line(
                                start=(p1_x, p1_y),
                                end=(p2_x, p2_y),
                                stroke=color,
                                stroke_width=1
                            ))
                        
                except Exception as e:
                    print(f"Error calculating aspect between {p1_name} and {p2_name}: {e}")
    
    # 绘制行星符号
    for planet_id, planet_name in planet_definitions:
        try:
            planet = chart.get(planet_id)
            longitude = planet.lon
            
            # 转换为SVG坐标
            planet_rad = math.radians(longitude)
            planet_x = center_x + radius * 0.8 * math.sin(planet_rad)
            planet_y = center_y - radius * 0.8 * math.cos(planet_rad)
            
            # 添加行星背景圆圈
            dwg.add(dwg.circle(center=(planet_x, planet_y), r=12,
                             fill='black', stroke='white', stroke_width=1))
            
            # 添加行星符号
            symbol = PLANET_SYMBOLS.get(planet_id, planet_name[0])
            
            # 根据行星类型选择颜色
            color = "#FFFFFF"  # 默认白色
            if planet_id in [const.SUN, const.MARS]:
                color = "#FF5555"  # 红色系
            elif planet_id in [const.MOON, const.VENUS]:
                color = "#55FF55"  # 绿色系
            elif planet_id in [const.MERCURY, const.JUPITER]:
                color = "#5555FF"  # 蓝色系
                
            dwg.add(dwg.text(symbol, insert=(planet_x, planet_y+5),
                          fill=color, font_size='16px',
                          text_anchor='middle', font_weight='bold'))
            
            # 添加行星度数标签
            degree_text = f"{planet_name}: {round(longitude, 1)}°"
            
            # 为了避免文字重叠，我们在外环围绕星盘放置标签
            label_distance = radius + 40
            label_x = center_x + label_distance * math.sin(planet_rad)
            label_y = center_y - label_distance * math.cos(planet_rad)
            
            dwg.add(dwg.text(degree_text, insert=(label_x, label_y),
                          fill='white', font_size='10px',
                          text_anchor='middle'))
            
            # 保存行星数据用于后续计算
            planets_data.append({
                'id': planet_id,
                'name': planet_name,
                'longitude': longitude,
                'x': planet_x,
                'y': planet_y
            })
            
        except Exception as e:
            print(f"Error plotting planet {planet_id}: {e}")
    
    # 添加标题
    title_text = "星盘图" if lang == 'zh' else "Natal Chart"
    dwg.add(dwg.text(title_text, insert=(center_x, 30),
                   fill='white', font_size='20px',
                   text_anchor='middle', font_weight='bold'))
    
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
