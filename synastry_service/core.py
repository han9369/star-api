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
        
        # 计算兼容性评分 (基础得分)
        compatibility_score = calculate_compatibility_score(aspects_data)
        
        # 获取关系类型得分
        relationship_score = constellation_relationships.get("relationship", {}).get("score", 0)
        relationship_type = constellation_relationships.get("relationship", {}).get("type", "")
        
        # 如果关系类型为空，使用默认类型
        if not relationship_type:
            relationship_type = "MAITRI"  # 默认使用命之星（Soul Connection）关系
            print(f"Warning: Empty relationship_type detected. Using default: {relationship_type}")
        
        # 应用星宿关系调整
        relationship_adjustment = 0
        if relationship_type == "MAITRI":  # 命之星
            relationship_adjustment = 10
        elif relationship_type == "SAHAJ":  # 荣亲
            relationship_adjustment = 7
        elif relationship_type == "MITRA":  # 友衰
            relationship_adjustment = 5
        elif relationship_type == "KARMA":  # 业胎
            relationship_adjustment = 0
        elif relationship_type == "ADHI":  # 安坏
            relationship_adjustment = -3
        elif relationship_type == "VAIRI":  # 危成
            relationship_adjustment = -5
        
        # D9盘和谐度调整
        d9_adjustment = 0
        if constellation_relationships.get("d9_harmony", {}).get("is_harmonious", False):
            d9_adjustment = 5
        
        # 行星能量互动调整
        energy_adjustment = constellation_relationships.get("planetary_energy", {}).get("strength", 0)
        
        # 星宿兼容性调整
        ashtakoot_adjustment = 0
        if 'ashtakoot_points' in nakshatra_compatibility:
            if nakshatra_compatibility['ashtakoot_points'] >= 20:
                ashtakoot_adjustment = 5
            elif nakshatra_compatibility['ashtakoot_points'] >= 16:
                ashtakoot_adjustment = 2
            else:
                ashtakoot_adjustment = -3
        
        if nakshatra_compatibility.get('vedha_dosha', False) or nakshatra_compatibility.get('rajju_dosha', False):
            ashtakoot_adjustment -= 3
        
        if nakshatra_compatibility.get('mahendra', False):
            ashtakoot_adjustment += 3
        
        # 总体调整
        total_adjustment = relationship_adjustment + d9_adjustment + energy_adjustment + ashtakoot_adjustment
        
        # 调整最终得分
        adjusted_compatibility_score = max(0, min(100, compatibility_score + total_adjustment))
        
        # 获取兼容性等级
        compatibility_level = get_compatibility_level(adjusted_compatibility_score)
        
        # 生成摘要
        summary = generate_summary(aspects_data, adjusted_compatibility_score)
        
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
            "compatibility_score": round(adjusted_compatibility_score),
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

def get_synastry_aspects(chart1, chart2):
    """获取两个星盘之间的相位"""
    aspects_list = []
    
    # 定义要获取的行星
    planets = {
        const.SUN: "Sun",
        const.MOON: "Moon",
        const.MERCURY: "Mercury",
        const.VENUS: "Venus", 
        const.MARS: "Mars",
        const.JUPITER: "Jupiter",
        const.SATURN: "Saturn",
        const.URANUS: "Uranus",
        const.NEPTUNE: "Neptune",
        const.PLUTO: "Pluto"
    }
    
    # 创建所有行星对的组合
    for planet1_id, planet1_name in planets.items():
        # 检查第一个行星是否存在于第一个星盘中
        if not planet_exists(chart1, planet1_id):
            continue
            
        for planet2_id, planet2_name in planets.items():
            # 检查第二个行星是否存在于第二个星盘中
            if not planet_exists(chart2, planet2_id):
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
                
                # 检查相位
                aspect_obj = aspects.getAspect(planet1, planet2, list(ASPECTS.keys()))
                
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
                            # 只添加有效相位
                            aspects_list.append({
                                "planet1": planet1_name,
                                "planet2": planet2_name,
                                "aspect": aspect_name,
                                "orb": round(orb, 2),
                                "quality": ASPECT_QUALITIES.get(aspect_id, "Neutral"),
                                "influence": ASPECT_INFLUENCES.get(aspect_id, "Unknown influence"),
                                "description": f"{planet1_name} {aspect_name} {planet2_name}"
                            })
            except Exception:
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
    score = 50  # 基础分数
    
    for aspect in aspects:
        aspect_type = aspect["aspect"]
        planet1 = aspect["planet1"]
        planet2 = aspect["planet2"]
        
        # 太阳和月亮的相位权重更高
        weight = 1.0
        if planet1 in ["Sun", "Moon"] or planet2 in ["Sun", "Moon"]:
            weight = 2.0
            
        # 根据相位类型加减分
        if aspect_type == "conjunction":
            score += 3 * weight
        elif aspect_type == "trine":
            score += 5 * weight
        elif aspect_type == "sextile":
            score += 3 * weight
        elif aspect_type == "square":
            score -= 2 * weight
        elif aspect_type == "opposition":
            score -= 1 * weight
    
    # 确保分数在0-100之间
    return max(0, min(100, score))

def get_compatibility_level(score):
    """根据兼容性分数获取兼容性级别"""
    if score >= 80:
        return "Excellent"
    elif score >= 70:
        return "Very Good"
    elif score >= 60:
        return "Good"
    elif score >= 50:
        return "Average"
    elif score >= 40:
        return "Challenging"
    else:
        return "Difficult"

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