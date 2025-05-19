from flatlib import const
from flatlib import aspects
import math

from .nakshatra import (
    NAKSHATRA_MAPPING, 
    get_nakshatra_number,
    get_comprehensive_compatibility
)
from .compatibility import (
    calculate_nakshatra_relationships,
    calculate_relationship_aspects_scores
)

# 辅助函数，安全获取行星位置
def safe_get_planet_position(chart, planet_id):
    """安全获取行星位置，处理可能的元组嵌套问题"""
    try:
        planet = chart.getObject(planet_id)
        
        # 检查planet.lon是否为元组
        if isinstance(planet.lon, tuple):
            if len(planet.lon) > 0:
                if isinstance(planet.lon[0], tuple):
                    return planet.lon[0][0]
                return planet.lon[0]
            return 0.0
        
        # 正常情况，直接返回值
        return planet.lon
    except Exception:
        return 0.0

# 检查行星是否存在于星盘中
def planet_exists(chart, planet_id):
    """检查行星是否存在于星盘中"""
    try:
        chart.objects.get(planet_id)
        return True
    except (KeyError, AttributeError):
        return False

# 相位影响类型
ASPECT_INFLUENCES = {
    const.CONJUNCTION: "Strong connection, merging energies",
    const.SEXTILE: "Harmonious opportunity, ease of expression",
    const.SQUARE: "Tension, challenge, potential for growth",
    const.TRINE: "Flow, harmony, ease",
    const.OPPOSITION: "Polarity, balance, awareness of the other",
}

# 相位名称映射
ASPECTS = {
    const.CONJUNCTION: "conjunction",
    const.SEXTILE: "sextile",
    const.SQUARE: "square",
    const.TRINE: "trine",
    const.OPPOSITION: "opposition",
}

# 相位属性（友好、敌对等）
ASPECT_QUALITIES = {
    const.CONJUNCTION: "Strong",
    const.SEXTILE: "Friendly",
    const.SQUARE: "Challenging",
    const.TRINE: "Harmonious",
    const.OPPOSITION: "Polarizing",
}

# 相位容许度
ORBS = {
    const.CONJUNCTION: 8,
    const.SEXTILE: 5,
    const.SQUARE: 7, 
    const.TRINE: 7,
    const.OPPOSITION: 8,
}

# 获取合盘分析数据
def get_synastry_analysis(chart1, chart2, lang='en', user1_name='Person 1', user2_name='Person 2'):
    """
    获取两个人的合盘分析数据
    返回格式为Bubble.io友好的单层JSON
    """
    try:
        # 获取相位
        aspects_data = get_synastry_aspects(chart1, chart2)
        
        # 计算宫位摆放
        house_positions = get_house_positions(chart1, chart2)
        person2_planets_in_person1_houses = house_positions[0]
        person1_planets_in_person2_houses = house_positions[1]
        
        # 计算星宿关系 (新增功能)
        constellation_relationships = calculate_nakshatra_relationships(chart1, chart2)
        
        # 获取月亮黄道位置
        moon1_lon = safe_get_planet_position(chart1, const.MOON)
        moon2_lon = safe_get_planet_position(chart2, const.MOON)
        
        # 计算星宿编号
        nakshatra1 = get_nakshatra_number(moon1_lon)
        nakshatra2 = get_nakshatra_number(moon2_lon)
        
        # 使用兼容性数据
        nakshatra_compatibility = get_comprehensive_compatibility(nakshatra1, nakshatra2)
        
        # 获取关系类型得分 - 直接使用作为主要兼容性分数
        relationship_score = constellation_relationships.get("relationship", {}).get("score", 0)
        relationship_type = constellation_relationships.get("relationship", {}).get("type", "")
        
        # 获取兼容性等级
        compatibility_level = get_compatibility_level(relationship_score)
        
        # 计算相位基础评分 (但不用于最终得分)
        calculate_compatibility_score(aspects_data)
        
        # 生成摘要
        summary = generate_summary(aspects_data, relationship_score)
        
        # 添加星宿关系描述
        relationship_description = constellation_relationships.get("relationship", {}).get("description", "")
        if relationship_description:
            combined_name = constellation_relationships.get("relationship", {}).get("combined_name", "")
            summary += f" Nakshatra analysis shows your relationship is a {combined_name}. {relationship_description}"
        
        # 计算关系维度评分
        relationship_dimensions = calculate_relationship_aspects_scores(aspects_data, constellation_relationships, nakshatra_compatibility)
        
        # 获取角色信息
        person1_role = constellation_relationships.get("person1", {}).get("role", "Energy Projector")
        person2_role = constellation_relationships.get("person2", {}).get("role", "Energy Receptor")
        
        # 构建角色描述
        relationship_combined_name = constellation_relationships.get('relationship', {}).get('combined_name', 'Soul Connection')
        person1_influence_sum = f"In this {relationship_combined_name}, {user1_name} serves as the {person1_role}."
        person2_influence_sum = f"In this {relationship_combined_name}, {user2_name} serves as the {person2_role}."
        
        # 创建响应数据
        response = {
            "status": "success",
            "compatibility_score": round(relationship_score),
            "compatibility_level": compatibility_level.lower(),
            "relationship_summary": summary,
            
            # 细分维度评分
            "harmony_score": round(relationship_dimensions.get("harmony", {}).get("score", 0)),
            "harmony_level": relationship_dimensions.get("harmony", {}).get("label", "Unknown").lower(),
            "harmony_summary": relationship_dimensions.get("harmony", {}).get("description", ""),
            
            "intimacy_score": round(relationship_dimensions.get("intimacy", {}).get("score", 0)),
            "intimacy_level": relationship_dimensions.get("intimacy", {}).get("label", "Unknown").lower(),
            "intimacy_summary": relationship_dimensions.get("intimacy", {}).get("description", ""),
            
            "passion_score": round(relationship_dimensions.get("passion", {}).get("score", 0)),
            "passion_level": relationship_dimensions.get("passion", {}).get("label", "Unknown").lower(),
            "passion_summary": relationship_dimensions.get("passion", {}).get("description", ""),
            
            "growth_score": round(relationship_dimensions.get("growth", {}).get("score", 0)),
            "growth_level": relationship_dimensions.get("growth", {}).get("label", "Unknown").lower(),
            "growth_summary": relationship_dimensions.get("growth", {}).get("description", ""),
            
            "karmic_score": round(relationship_dimensions.get("karmic_bond", {}).get("score", 0)),
            "karmic_level": relationship_dimensions.get("karmic_bond", {}).get("label", "Unknown").lower(),
            "karmic_summary": relationship_dimensions.get("karmic_bond", {}).get("description", ""),
            
            # 关系类型信息
            "relationship_type": constellation_relationships.get("relationship", {}).get("combined_name", "Soul Connection").lower(),
            "relationship_type_score": round(relationship_score),
            
            # 互相影响角色信息
            "p1p2_influence": person1_role.lower(),
            "p1p2_influence_sum": person1_influence_sum,
            "p2p1_influence": person2_role.lower(),
            "p2p1_influence_sum": person2_influence_sum,
        }
        
        # 将相位信息改为列表结构
        aspects_list = []
        for aspect in aspects_data:
            aspects_list.append({
                "name": f"{aspect['planet1']} {aspect['aspect']} {aspect['planet2']}".lower(),
                "orb": round(aspect['orb'], 2),
                "summary": aspect['influence'].lower()
            })
        response["aspects"] = aspects_list
        
        # 将宫位摆放信息改为简单字符串列表
        p2p1_house_list = []
        for house_placement in person2_planets_in_person1_houses:
            p2p1_house_list.append(house_placement['description'].lower())
            
        p1p2_house_list = []
        for house_placement in person1_planets_in_person2_houses:
            p1p2_house_list.append(house_placement['description'].lower())
        
        response["p2p1house"] = p2p1_house_list
        response["p1p2house"] = p1p2_house_list
        
        return response
    except Exception as e:
        return {"status": "error", "error": str(e)}

def is_valid_aspect(planet1_name, planet2_name, aspect_name):
    """
    检查相位组合是否有效，排除几乎不可能的相位和同行星相位
    返回True表示有效，False表示无效
    """
    # 排除同行星相位（如太阳-太阳，月亮-月亮等）
    if planet1_name == planet2_name:
        return False
        
    # 定义各种行星组
    inner_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars"]
    social_planets = ["Jupiter", "Saturn"]
    outer_planets = ["Uranus", "Neptune", "Pluto"]
    all_outer = social_planets + outer_planets
    
    # 太阳-水星和太阳-金星的特殊相位处理
    if ((planet1_name == "Sun" and planet2_name == "Mercury") or
        (planet2_name == "Sun" and planet1_name == "Mercury") or
        (planet1_name == "Sun" and planet2_name == "Venus") or
        (planet2_name == "Sun" and planet1_name == "Venus")):
        # 内行星与太阳的距离有限，排除大相位
        if aspect_name in ["square", "trine", "opposition"]:
            return False
    
    # 对于不太可能的相位组合的其他规则
    return True

def get_aspect_orb(planet1_name, planet2_name, aspect_type):
    """
    根据行星组合和相位类型返回适当的容许度
    """
    # 基础容许度
    base_orb = ORBS.get(aspect_type, 5)
    
    # 根据行星组合调整容许度
    if "Sun" in [planet1_name, planet2_name] or "Moon" in [planet1_name, planet2_name]:
        return base_orb  # 太阳或月亮参与的相位
    
    # 其他情况返回稍小的容许度
    return base_orb - 1

def is_important_aspect(planet1_name, planet2_name, aspect_name, orb):
    """
    评估一个相位的重要性，返回True表示重要，False表示不重要。
    这将根据行星的重要性、相位类型和紧密度（orb）来确定。
    目标是将相位数量减少到约10个最重要的相位。
    """
    # 定义关键行星组 - 重要程度依次递减
    primary_planets = ["Sun", "Moon"]  # 最重要的行星（太阳和月亮）
    personal_planets = ["Mercury", "Venus", "Mars"]  # 个人行星
    social_planets = ["Jupiter", "Saturn"]  # 社会行星
    outer_planets = ["Uranus", "Neptune", "Pluto"]  # 外行星
    
    # 定义相位重要性（主要相位比次要相位更重要）
    major_aspects = ["conjunction", "opposition", "trine", "square"]  # 主要相位
    minor_aspects = ["sextile"]  # 次要相位
    
    # 1. 如果是太阳或月亮与任何行星的主要相位，且容差小于6度，保留
    if ((planet1_name in primary_planets or planet2_name in primary_planets) and 
            aspect_name in major_aspects and abs(orb) <= 6):
        return True
    
    # 2. 如果是太阳和月亮之间的任何相位，不管容差多大都保留
    if ((planet1_name == "Sun" and planet2_name == "Moon") or 
            (planet1_name == "Moon" and planet2_name == "Sun")):
        return True
    
    # 3. 如果是个人行星之间的主要相位，且容差小于5度，保留
    if (planet1_name in personal_planets and planet2_name in personal_planets and 
            aspect_name in major_aspects and abs(orb) <= 5):
        return True
    
    # 4. 如果是个人行星与社会行星之间的合相或对分相，且容差小于4度，保留
    if (((planet1_name in personal_planets and planet2_name in social_planets) or
         (planet1_name in social_planets and planet2_name in personal_planets)) and
            aspect_name in ["conjunction", "opposition"] and abs(orb) <= 4):
        return True
    
    # 5. 其他情况下，只保留非常紧密（容差小于2度）的主要相位
    if aspect_name in major_aspects and abs(orb) <= 2:
        return True
    
    # 6. 特别处理一些著名的强力相位组合
    special_combinations = [
        # 金星-火星相位：关系中的激情
        ("Venus", "Mars", ["conjunction", "trine", "sextile"]),
        # 太阳-木星相位：关系中的乐观和成长
        ("Sun", "Jupiter", ["conjunction", "trine"]),
        # 月亮-金星相位：情感和爱的连接
        ("Moon", "Venus", ["conjunction", "trine"]),
        # 月亮-土星相位：情感责任和稳定性
        ("Moon", "Saturn", ["conjunction", "trine"]),
    ]
    
    for p1, p2, aspect_types in special_combinations:
        if ((planet1_name == p1 and planet2_name == p2) or 
                (planet1_name == p2 and planet2_name == p1)) and aspect_name in aspect_types:
            return abs(orb) <= 5  # 对于特殊组合，容差可以适当放宽
    
    # 默认情况下，认为相位不够重要
    return False

def get_synastry_aspects(chart1, chart2):
    """获取两个星盘之间的相位，只考虑最重要的行星组合"""
    aspects_list = []
    
    # 减少要获取的行星，移除部分外行星
    main_planets = {
        const.SUN: "Sun",
        const.MOON: "Moon",
        const.MERCURY: "Mercury",
        const.VENUS: "Venus", 
        const.MARS: "Mars",
        const.JUPITER: "Jupiter",
        const.SATURN: "Saturn"
    }
    
    # 可选的外行星 - 只在特定组合中使用
    outer_planets = {
        const.URANUS: "Uranus",
        const.NEPTUNE: "Neptune",
        const.PLUTO: "Pluto"
    }
    
    # 定义关键相位组合，指定哪些行星对和相位类型需要考虑
    # 格式: (行星1, 行星2, [允许的相位类型列表])
    key_combinations = [
        # 太阳和月亮的组合 - 最关键的关系指标
        (const.SUN, const.MOON, [const.CONJUNCTION, const.SEXTILE, const.SQUARE, const.TRINE, const.OPPOSITION]),
        
        # 太阳与个人行星的组合
        (const.SUN, const.MERCURY, [const.CONJUNCTION, const.SEXTILE]),  # 限制太阳-水星相位
        (const.SUN, const.VENUS, [const.CONJUNCTION, const.SEXTILE]),    # 限制太阳-金星相位
        (const.SUN, const.MARS, [const.CONJUNCTION, const.SEXTILE, const.SQUARE, const.TRINE, const.OPPOSITION]),
        (const.SUN, const.JUPITER, [const.CONJUNCTION, const.TRINE, const.OPPOSITION]),
        (const.SUN, const.SATURN, [const.CONJUNCTION, const.SQUARE, const.OPPOSITION]),
        
        # 月亮与个人行星的组合
        (const.MOON, const.MERCURY, [const.CONJUNCTION, const.TRINE, const.SQUARE]),
        (const.MOON, const.VENUS, [const.CONJUNCTION, const.TRINE, const.SQUARE, const.OPPOSITION]),
        (const.MOON, const.MARS, [const.CONJUNCTION, const.TRINE, const.SQUARE, const.OPPOSITION]),
        (const.MOON, const.JUPITER, [const.CONJUNCTION, const.TRINE]),
        (const.MOON, const.SATURN, [const.CONJUNCTION, const.TRINE, const.SQUARE, const.OPPOSITION]),
        
        # 爱情和吸引力相关的关键组合
        (const.VENUS, const.MARS, [const.CONJUNCTION, const.TRINE, const.SQUARE, const.OPPOSITION]),
        (const.VENUS, const.JUPITER, [const.CONJUNCTION, const.TRINE]),
        (const.VENUS, const.SATURN, [const.CONJUNCTION, const.OPPOSITION]),
        
        # 激情和冲突相关的组合
        (const.MARS, const.JUPITER, [const.CONJUNCTION, const.TRINE, const.OPPOSITION]),
        (const.MARS, const.SATURN, [const.CONJUNCTION, const.SQUARE, const.OPPOSITION]),
        
        # 成长和责任的组合
        (const.JUPITER, const.SATURN, [const.CONJUNCTION, const.SQUARE, const.OPPOSITION]),
        
        # 少量外行星的特殊组合
        (const.SUN, const.URANUS, [const.TRINE, const.SQUARE]),
        (const.MOON, const.NEPTUNE, [const.OPPOSITION]),
        (const.VENUS, const.PLUTO, [const.OPPOSITION, const.CONJUNCTION])
    ]
    
    # 处理每一个关键组合
    for planet1_id, planet2_id, allowed_aspects in key_combinations:
        # 获取行星名称
        planet1_name = main_planets.get(planet1_id) or outer_planets.get(planet1_id)
        planet2_name = main_planets.get(planet2_id) or outer_planets.get(planet2_id)
        
        # 检查行星是否存在
        if not planet1_name or not planet2_name:
            continue
        
        # 检查行星是否存在于星盘中
        if not planet_exists(chart1, planet1_id) or not planet_exists(chart2, planet2_id):
            continue
            
        try:
            planet1 = chart1.getObject(planet1_id)
            planet2 = chart2.getObject(planet2_id)
            
            # 安全获取行星位置
            planet1_lon = safe_get_planet_position(chart1, planet1_id)
            planet2_lon = safe_get_planet_position(chart2, planet2_id)
            
            # 临时修改planet对象的lon属性用于计算相位
            original_lon1 = planet1.lon
            original_lon2 = planet2.lon
            
            planet1.lon = planet1_lon
            planet2.lon = planet2_lon
            
            # 只检查允许的相位类型
            aspect_obj = aspects.getAspect(planet1, planet2, allowed_aspects)
            
            # 恢复原始lon值
            planet1.lon = original_lon1
            planet2.lon = original_lon2
            
            # 如果存在相位
            if aspect_obj:
                aspect_id = aspect_obj.type
                aspect_name = ASPECTS.get(aspect_id, "unknown")
                orb = aspect_obj.orb
                
                # 获取针对这个行星组合的适当容许度
                adjusted_orb = get_aspect_orb(planet1_name, planet2_name, aspect_id)
                
                # 只考虑在允许的容许度范围内的相位且不是"unknown"相位
                if aspect_name != "unknown" and abs(orb) <= adjusted_orb:
                    # 检查是否是有效的相位组合
                    if is_valid_aspect(planet1_name, planet2_name, aspect_name):
                        # 添加相位
                        aspects_list.append({
                            "planet1": planet1_name,
                            "planet2": planet2_name,
                            "aspect": aspect_name,
                            "orb": round(orb, 2),
                            "quality": ASPECT_QUALITIES.get(aspect_id, "Neutral"),
                            "influence": ASPECT_INFLUENCES.get(aspect_id, "Unknown influence"),
                            "description": f"{planet1_name} {aspect_name} {planet2_name}"
                        })
            
            # 检查另一方向的相位 (chart2 -> chart1)
            # 这部分保持相同的逻辑，只是交换了行星顺序
            planet1 = chart2.getObject(planet1_id)
            planet2 = chart1.getObject(planet2_id)
            
            # 安全获取行星位置
            planet1_lon = safe_get_planet_position(chart2, planet1_id)
            planet2_lon = safe_get_planet_position(chart1, planet2_id)
            
            # 临时修改planet对象的lon属性用于计算相位
            original_lon1 = planet1.lon
            original_lon2 = planet2.lon
            
            planet1.lon = planet1_lon
            planet2.lon = planet2_lon
            
            # 只检查允许的相位类型
            aspect_obj = aspects.getAspect(planet1, planet2, allowed_aspects)
            
            # 恢复原始lon值
            planet1.lon = original_lon1
            planet2.lon = original_lon2
            
            # 如果存在相位
            if aspect_obj:
                aspect_id = aspect_obj.type
                aspect_name = ASPECTS.get(aspect_id, "unknown")
                orb = aspect_obj.orb
                
                # 获取针对这个行星组合的适当容许度
                adjusted_orb = get_aspect_orb(planet2_name, planet1_name, aspect_id)  # 注意这里行星顺序已交换
                
                # 只考虑在允许的容许度范围内的相位且不是"unknown"相位
                if aspect_name != "unknown" and abs(orb) <= adjusted_orb:
                    # 检查是否是有效的相位组合
                    if is_valid_aspect(planet2_name, planet1_name, aspect_name):
                        # 添加相位
                        aspects_list.append({
                            "planet1": planet2_name,
                            "planet2": planet1_name,
                            "aspect": aspect_name,
                            "orb": round(orb, 2),
                            "quality": ASPECT_QUALITIES.get(aspect_id, "Neutral"),
                            "influence": ASPECT_INFLUENCES.get(aspect_id, "Unknown influence"),
                            "description": f"{planet2_name} {aspect_name} {planet1_name}"
                        })
        except Exception as e:
            print(f"Debug - Error in aspect calculation: {str(e)}")
            pass  # 跳过出错的相位
    
    return aspects_list

def get_house_positions(chart1, chart2):
    """获取行星在对方星盘中的宫位位置"""
    positions1 = []  # 第二个人的行星在第一个人星盘中的宫位
    positions2 = []  # 第一个人的行星在第二个人星盘中的宫位
    
    # 定义要获取的行星
    planets = {
        const.SUN: "Sun",
        const.MOON: "Moon",
        const.MERCURY: "Mercury",
        const.VENUS: "Venus", 
        const.MARS: "Mars",
        const.JUPITER: "Jupiter",
        const.SATURN: "Saturn"
    }
    
    # 获取第二个人的行星在第一个人星盘中的宫位
    for planet_id, planet_name in planets.items():
        # 检查行星是否存在于第二个星盘中
        if not planet_exists(chart2, planet_id):
            continue
        try:
            planet2 = chart2.getObject(planet_id)
            
            # 安全获取行星位置
            planet2_lon = safe_get_planet_position(chart2, planet_id)
            
            # 临时修改planet对象的lon属性
            original_lon = planet2.lon
            planet2.lon = planet2_lon
            
            # 获取行星在第一个人星盘中的宫位
            house_obj = chart1.houses.getObjectHouse(planet2)
            
            # 恢复原始lon值
            planet2.lon = original_lon
            
            # 提取宫位数字
            house_num = 0
            
            # 从House对象中提取宫位号码
            if hasattr(house_obj, 'id'):
                house_id = house_obj.id
                # 提取数字部分，如"House6"提取为6
                import re
                numbers = re.findall(r'\d+', house_id)
                if numbers:
                    house_num = int(numbers[0])
            
            # 如果宫位有效，则添加到结果中
            if house_num > 0:
                # 获取宫位名称对应的序数后缀
                suffix = "th"
                if house_num == 1:
                    suffix = "st"
                elif house_num == 2:
                    suffix = "nd"
                elif house_num == 3:
                    suffix = "rd"
                
                positions1.append({
                    "planet": planet_name,
                    "house": house_num,
                    "description": f"{planet_name} in {house_num}{suffix} house"
                })
        except Exception:
            pass  # 跳过出错的行星
    
    # 获取第一个人的行星在第二个人星盘中的宫位
    for planet_id, planet_name in planets.items():
        # 检查行星是否存在于第一个星盘中
        if not planet_exists(chart1, planet_id):
            continue
        try:
            planet1 = chart1.getObject(planet_id)
            
            # 安全获取行星位置
            planet1_lon = safe_get_planet_position(chart1, planet_id)
            
            # 临时修改planet对象的lon属性
            original_lon = planet1.lon
            planet1.lon = planet1_lon
            
            # 获取行星在第二个人星盘中的宫位
            house_obj = chart2.houses.getObjectHouse(planet1)
            
            # 恢复原始lon值
            planet1.lon = original_lon
            
            # 提取宫位数字
            house_num = 0
            
            # 从House对象中提取宫位号码
            if hasattr(house_obj, 'id'):
                house_id = house_obj.id
                # 提取数字部分，如"House6"提取为6
                import re
                numbers = re.findall(r'\d+', house_id)
                if numbers:
                    house_num = int(numbers[0])
            
            # 如果宫位有效，则添加到结果中
            if house_num > 0:
                # 获取宫位名称对应的序数后缀
                suffix = "th"
                if house_num == 1:
                    suffix = "st"
                elif house_num == 2:
                    suffix = "nd"
                elif house_num == 3:
                    suffix = "rd"
                
                positions2.append({
                    "planet": planet_name,
                    "house": house_num,
                    "description": f"{planet_name} in {house_num}{suffix} house"
                })
        except Exception:
            pass  # 跳过出错的行星
    
    return [positions1, positions2]

def calculate_compatibility_score(aspects):
    """基于相位计算兼容性分数"""
    score = 40  # 降低基础分数以允许更大的区分度
    
    # 保存相位计数，用于后续计算
    harmonious_aspects = 0
    challenging_aspects = 0
    neutral_aspects = 0
    
    # 太阳月亮连线的重要相位计数
    sun_moon_harmonious = 0
    sun_moon_challenging = 0
    
    # 金星火星连线的重要相位计数
    venus_mars_harmonious = 0
    venus_mars_challenging = 0
    
    for aspect in aspects:
        aspect_type = aspect["aspect"]
        planet1 = aspect["planet1"]
        planet2 = aspect["planet2"]
        orb = aspect.get("orb", 5)  # 默认容许度为5
        
        # 根据相位紧密度调整权重 - 容许度越小加分越多
        orb_factor = 1.0
        if orb < 1.0:
            orb_factor = 1.5  # 非常紧密的相位
        elif orb < 2.0:
            orb_factor = 1.2  # 紧密的相位
        
        # 太阳和月亮的相位权重更高
        weight = 1.0
        if "Sun" in [planet1, planet2] and "Moon" in [planet1, planet2]:
            weight = 2.5  # 太阳-月亮相位最重要
            if aspect_type in ["trine", "sextile", "conjunction"]:
                sun_moon_harmonious += 1
            elif aspect_type in ["square", "opposition"]:
                sun_moon_challenging += 1
        elif "Sun" in [planet1, planet2] or "Moon" in [planet1, planet2]:
            weight = 1.8  # 太阳或月亮与其他行星
        
        # 金星和火星的相位权重
        if "Venus" in [planet1, planet2] and "Mars" in [planet1, planet2]:
            weight = 2.0  # 金星-火星相位对激情和兼容性重要
            if aspect_type in ["trine", "sextile", "conjunction"]:
                venus_mars_harmonious += 1
            elif aspect_type in ["square", "opposition"]:
                venus_mars_challenging += 1
        
        # 根据相位类型加减分
        if aspect_type == "conjunction":
            neutral_aspects += 1
            if "Saturn" in [planet1, planet2] or "Pluto" in [planet1, planet2]:
                score += 2 * weight * orb_factor  # 土星/冥王星的合相更具挑战性但也有成长
            else:
                score += 3 * weight * orb_factor  # 其他合相通常更和谐
        elif aspect_type == "trine":
            harmonious_aspects += 1
            score += 5 * weight * orb_factor
        elif aspect_type == "sextile":
            harmonious_aspects += 1
            score += 3 * weight * orb_factor
        elif aspect_type == "square":
            challenging_aspects += 1
            if "Jupiter" in [planet1, planet2]:
                score -= 1 * weight * orb_factor  # 木星的刑相更容易管理
            else:
                score -= 2 * weight * orb_factor
        elif aspect_type == "opposition":
            challenging_aspects += 1
            if "Mercury" in [planet1, planet2]:
                score -= 1 * weight * orb_factor  # 水星的冲相可能是思想差异性
            else:
                score -= 1.5 * weight * orb_factor
    
    # 基于相位平衡额外调整
    total_aspects = harmonious_aspects + challenging_aspects + neutral_aspects
    if total_aspects > 0:
        # 和谐相位与挑战相位的比例
        harmony_ratio = harmonious_aspects / total_aspects
        
        # 如果和谐相位占比高，增加分数
        if harmony_ratio > 0.7:
            score += 8
        elif harmony_ratio > 0.5:
            score += 5
        
        # 重要行星组合的加分项
        if sun_moon_harmonious > 0:
            score += 7  # 太阳月亮和谐是最佳的指标之一
        if venus_mars_harmonious > 0:
            score += 5  # 金星火星和谐对吸引力很重要
            
        # 关键挑战相位的减分项
        if sun_moon_challenging > 1:
            score -= 6  # 多个太阳月亮挑战
        if venus_mars_challenging > 1:
            score -= 4  # 多个金星火星挑战相位
    
    # 确保分数在0-100之间
    return max(0, min(100, score))

def get_compatibility_level(score):
    """根据兼容性分数获取兼容性级别"""
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Very Good"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Above Average"
    elif score >= 50:
        return "Average"
    elif score >= 40:
        return "Below Average"
    elif score >= 30:
        return "Challenging"
    elif score >= 20:
        return "Difficult"
    else:
        return "Very Difficult"

def generate_summary(aspects, score):
    """生成合盘总结"""
    # 计算和谐与紧张相位的数量
    harmonious = 0
    challenging = 0
    
    for aspect in aspects:
        if aspect["aspect"] in ["trine", "sextile"]:
            harmonious += 1
        elif aspect["aspect"] in ["square", "opposition"]:
            challenging += 1
    
    # 生成摘要
    if score >= 80:
        return "This is an extraordinary connection with strong harmony. You share many beneficial aspects that support mutual growth and understanding."
    elif score >= 70:
        return "You have a very good connection with more harmonious aspects than challenging ones. Your relationship has great potential for growth and happiness."
    elif score >= 60:
        return "Your connection shows a good balance of harmonious and challenging aspects. While there are some tensions, they can lead to growth."
    elif score >= 50:
        return "Your connection has an average mix of aspects. There are both areas of ease and challenge in your relationship."
    elif score >= 40:
        return "Your connection has more challenging aspects than harmonious ones. This relationship may require work but can lead to significant growth."
    else:
        return "This connection shows significant challenges. While difficult, these tensions can lead to profound personal development if addressed consciously." 
