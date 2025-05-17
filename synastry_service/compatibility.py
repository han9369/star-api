from flatlib import const
from .nakshatra import get_nakshatra_number, calculate_nakshatra_interval, determine_relationship_type
from .nakshatra import get_relationship_level, get_relationship_description, get_relationship_base_score
from .nakshatra import get_consistent_roles, calculate_d9_position, get_comprehensive_compatibility
from .nakshatra import NAKSHATRA_MAPPING

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

def calculate_planetary_energy(chart1, chart2, relationship_type):
    """
    计算两个星盘之间的行星能量互动
    根据关系类型匹配相应的行星组合
    """
    # 定义与各种关系类型关联的行星
    relationship_planets = {
        "MAITRI": ["MOON", "SUN"],              # Soul Connection - 月亮和太阳
        "KARMA": ["SATURN", "MOON", "SUN"],     # Karmic Bond - 土星与月亮/太阳
        "SAHAJ": ["JUPITER", "VENUS"],          # Mutual Growth - 木星与金星
        "MITRA": ["VENUS", "MERCURY"],          # Friendly Bonds - 金星与水星
        "ADHI": ["SATURN", "MARS"],             # Binding Forces - 土星与火星
        "VAIRI": ["MARS", "URANUS"]             # Dynamic Tension - 火星与天王星
    }
    
    # 关系类型相关的主要行星
    primary_planets = relationship_planets.get(relationship_type, ["SUN", "MOON"])
    
    # 行星ID映射
    planet_ids = {
        "SUN": const.SUN,
        "MOON": const.MOON,
        "MERCURY": const.MERCURY,
        "VENUS": const.VENUS,
        "MARS": const.MARS,
        "JUPITER": const.JUPITER,
        "SATURN": const.SATURN,
        "URANUS": const.URANUS,
        "NEPTUNE": const.NEPTUNE,
        "PLUTO": const.PLUTO
    }
    
    # 计算行星能量互动得分
    energy_score = 0
    involved_planets = []
    
    # 检查两个星盘中的关键行星相位
    for planet_name in primary_planets:
        planet_id = planet_ids.get(planet_name)
        if not planet_id:
            continue
            
        try:
            # 获取第一个人的行星位置
            p1_position = safe_get_planet_position(chart1, planet_id)
            
            # 获取第二个人的行星位置
            p2_position = safe_get_planet_position(chart2, planet_id)
            
            # 计算行星间角度差
            angle_diff = abs(p1_position - p2_position) % 360
            if angle_diff > 180:
                angle_diff = 360 - angle_diff
            
            # 根据角度差评估能量互动
            if angle_diff < 10:  # 合相(0°) - 非常强
                energy_score += 8
                involved_planets.append(planet_name)
            elif abs(angle_diff - 60) < 6:  # 六分相(60°) - 和谐
                energy_score += 5
                involved_planets.append(planet_name)
            elif abs(angle_diff - 90) < 8:  # 刑相(90°) - 紧张但有活力
                energy_score += 3
                involved_planets.append(planet_name)
            elif abs(angle_diff - 120) < 8:  # 拱相(120°) - 非常和谐
                energy_score += 7
                involved_planets.append(planet_name)
            elif abs(angle_diff - 180) < 10:  # 冲相(180°) - 强但有挑战
                energy_score += 4
                involved_planets.append(planet_name)
        except Exception:
            pass
    
    # 根据关系类型调整能量强度
    energy_modifier = {
        "MAITRI": 1.2,   # Soul Connection - 能量加成20%
        "KARMA": 1.0,    # Karmic Bond - 标准能量
        "SAHAJ": 1.1,    # Mutual Growth - 能量加成10%
        "MITRA": 0.9,    # Friendly Bonds - 能量减少10%
        "ADHI": 0.8,     # Binding Forces - 能量减少20%
        "VAIRI": 1.1     # Dynamic Tension - 能量加成10%
    }
    
    # 应用修正系数
    modifier = energy_modifier.get(relationship_type, 1.0)
    final_energy_score = int(energy_score * modifier)
    
    # 能量强度描述
    energy_description = ""
    if final_energy_score >= 15:
        energy_description = "Extremely strong planetary energy between you enhances your relationship."
    elif final_energy_score >= 10:
        energy_description = "Strong planetary energy supports your connection."
    elif final_energy_score >= 5:
        energy_description = "Moderate planetary energy exists between you."
    else:
        energy_description = "The planetary energy between you is subtle and may require attention to develop."
    
    # 返回能量互动结果
    return {
        "strength": final_energy_score,
        "planets_involved": involved_planets,
        "description": energy_description
    }

def calculate_nakshatra_relationships(chart1, chart2):
    """使用改进的星宿关系计算方法，包含D9盘修正和行星能量互动"""
    try:
        # 获取两个人的月亮位置
        moon1_lon = safe_get_planet_position(chart1, const.MOON)
        moon2_lon = safe_get_planet_position(chart2, const.MOON)
        
        # 获取月亮所在的星宿编号(1-27)
        nakshatra1 = get_nakshatra_number(moon1_lon)
        nakshatra2 = get_nakshatra_number(moon2_lon)
        
        # 计算星宿间隔 - 双向计算，取更有利的结果
        interval_1_to_2 = calculate_nakshatra_interval(nakshatra1, nakshatra2)
        interval_2_to_1 = calculate_nakshatra_interval(nakshatra2, nakshatra1)
        
        # 确定两个方向的关系类型
        relationship_type_1_to_2 = determine_relationship_type(interval_1_to_2)
        relationship_type_2_to_1 = determine_relationship_type(interval_2_to_1)
        
        # 计算两个方向的关系分数
        relationship_score_1_to_2 = get_relationship_base_score(relationship_type_1_to_2)
        relationship_score_2_to_1 = get_relationship_base_score(relationship_type_2_to_1)
        
        # 选择分数更高的方向作为主要关系
        if relationship_score_1_to_2 >= relationship_score_2_to_1:
            relationship_type = relationship_type_1_to_2
            interval = interval_1_to_2
        else:
            relationship_type = relationship_type_2_to_1
            interval = interval_2_to_1
        
        # 确保关系类型不为空
        if not relationship_type:
            relationship_type = "MAITRI"  # 默认为最高关系
            interval = 27
        
        # 计算D9盘位置
        d9_position1 = calculate_d9_position(moon1_lon)
        d9_position2 = calculate_d9_position(moon2_lon)
        
        # 检查D9盘主星是否相同（可减轻安坏、危成等关系的冲突）
        d9_harmony = False
        d9_adjustment = 0
        
        if d9_position1["ruler"] == d9_position2["ruler"]:
            d9_harmony = True
            d9_adjustment = 10  # D9盘主星相同，增加和谐度
        
        # 计算行星能量互动
        energy_interaction = calculate_planetary_energy(chart1, chart2, relationship_type)
        
        # 获取关系强度
        base_distance_level = get_relationship_level(interval, relationship_type)
        
        # 如果是不和谐关系（安坏、危成）且D9盘和谐，提升一级
        distance_level = base_distance_level
        if relationship_type in ["ADHI", "VAIRI"] and d9_harmony and distance_level != "FIXED":
            if distance_level == "FAR":
                distance_level = "MODERATE"
            elif distance_level == "MODERATE":
                distance_level = "NEAR"
        
        # 获取关系描述
        combined_name, relationship_description = get_relationship_description(relationship_type, distance_level)
        
        # 如果D9盘和谐，添加额外描述
        if d9_harmony:
            relationship_description += " The matching Moon rulers in your D9 charts enhance the harmony of your relationship."
            
        # 如果有行星能量互动，添加描述
        if energy_interaction["description"]:
            relationship_description += " " + energy_interaction["description"]
        
        # 计算关系分数 - 使用前面确定的分数作为基础，再加上其他调整
        relationship_score = relationship_score_1_to_2 if relationship_type == relationship_type_1_to_2 else relationship_score_2_to_1
        
        # 根据距离调整得分
        if distance_level == "NEAR":
            relationship_score = min(100, relationship_score + 10)
        elif distance_level == "FAR" and distance_level != "FIXED":
            relationship_score = max(0, relationship_score - 10)
            
        # D9盘和谐度修正
        relationship_score += d9_adjustment
        
        # 行星能量互动修正
        relationship_score += energy_interaction["strength"]
        
        # 确保分数在0-100范围内
        relationship_score = max(0, min(100, relationship_score))
        
        # 为每个人分配角色，但确保相同的关系类型下角色分配一致
        person1_role, person2_role = get_consistent_roles(relationship_type)
            
        # 构造结果
        result = {
            "person1": {
                "nakshatra_number": nakshatra1,
                "nakshatra_name": NAKSHATRA_MAPPING.get(nakshatra1, "Unknown"),
                "d9_position": d9_position1,
                "role": person1_role
            },
            "person2": {
                "nakshatra_number": nakshatra2,
                "nakshatra_name": NAKSHATRA_MAPPING.get(nakshatra2, "Unknown"),
                "d9_position": d9_position2,
                "role": person2_role
            },
            "relationship": {
                "type": relationship_type,
                "combined_name": combined_name,
                "score": relationship_score,
                "description": relationship_description
            },
            "distance": {
                "value": interval,
                "level": distance_level,
                "base_level": base_distance_level,
                "description": f"Nakshatra interval is {interval}, relationship intensity: {distance_level}"
            },
            "d9_harmony": {
                "is_harmonious": d9_harmony,
                "adjustment": d9_adjustment,
                "description": "D9 chart main stars match, enhancing harmony" if d9_harmony else "D9 chart main stars differ"
            },
            "planetary_energy": energy_interaction
        }
        
        return result
    except Exception as e:
        # 出错时返回默认值
        default_role1, default_role2 = get_consistent_roles("MAITRI")
        return {
            "person1": {
                "nakshatra_number": 1,
                "nakshatra_name": "Default",
                "d9_position": {"sign": 1, "sign_name": "Aries", "ruler": "Mars"},
                "role": default_role1
            },
            "person2": {
                "nakshatra_number": 1,
                "nakshatra_name": "Default",
                "d9_position": {"sign": 1, "sign_name": "Aries", "ruler": "Mars"},
                "role": default_role2
            },
            "relationship": {
                "type": "MAITRI",
                "combined_name": "Soul Connection",
                "score": 80,
                "description": "Error calculating nakshatra relationship: " + str(e)
            },
            "distance": {
                "value": 0,
                "level": "FIXED",
                "base_level": "FIXED",
                "description": "Default distance calculation"
            },
            "d9_harmony": {
                "is_harmonious": True,
                "adjustment": 0,
                "description": "Default D9 harmony"
            },
            "planetary_energy": {
                "strength": 5,
                "planets_involved": ["SUN", "MOON"],
                "description": "Default planetary energy"
            }
        }

def calculate_relationship_aspects_scores(aspects, constellation_relationships, nakshatra_compatibility):
    """
    计算关系各方面的分数
    
    返回包含以下内容的字典:
    - 和谐度: 日常互动中的自然同步性
    - 亲密度: 情感和身体上的亲近感
    - 激情: 吸引力和兴奋感
    - 成长: 个人发展和挑战
    - 业力连结: 灵魂连接和宿命
    """
    # 初始化各方面的分数
    aspect_scores = {
        "harmony": 50,
        "intimacy": 50,
        "passion": 50,
        "growth": 50,
        "karmic_bond": 50
    }
    
    # 提取星宿关系数据
    relationship_type = constellation_relationships.get("relationship", {}).get("type", "")
    distance_level = constellation_relationships.get("distance", {}).get("level", "")
    d9_harmony = constellation_relationships.get("d9_harmony", {}).get("is_harmonious", False)
    planetary_energy = constellation_relationships.get("planetary_energy", {})
    
    # 1. 处理相位数据，计算和谐度、亲密度和激情分数
    for aspect in aspects:
        aspect_type = aspect["aspect"]
        planet1 = aspect["planet1"]
        planet2 = aspect["planet2"]
        
        # 和谐度分数 - 主要受和谐相位影响
        if aspect_type in ["trine", "sextile"]:
            aspect_scores["harmony"] += 3
        elif aspect_type == "opposition":
            aspect_scores["harmony"] -= 2
        elif aspect_type == "square":
            aspect_scores["harmony"] -= 3
            
        # 月亮相位强烈影响和谐度
        if (planet1 == "Moon" or planet2 == "Moon") and aspect_type in ["trine", "sextile", "conjunction"]:
            aspect_scores["harmony"] += 4
            
        # 水星和木星相位影响沟通和谐度
        if ((planet1 == "Mercury" and planet2 == "Jupiter") or 
            (planet1 == "Jupiter" and planet2 == "Mercury")) and aspect_type in ["trine", "sextile", "conjunction"]:
            aspect_scores["harmony"] += 5
            
        # 亲密度分数 - 受月亮、金星和个人行星影响
        if (planet1 == "Moon" or planet2 == "Moon") or (planet1 == "Venus" or planet2 == "Venus"):
            if aspect_type in ["trine", "sextile", "conjunction"]:
                aspect_scores["intimacy"] += 4
            elif aspect_type == "square":
                aspect_scores["intimacy"] -= 2
        
        # 太阳-月亮相位强烈影响亲密度
        if ((planet1 == "Sun" and planet2 == "Moon") or 
            (planet1 == "Moon" and planet2 == "Sun")):
            if aspect_type in ["trine", "sextile", "conjunction"]:
                aspect_scores["intimacy"] += 6
                
        # 激情分数 - 受火星和金星相位的强烈影响
        if ((planet1 == "Mars" and planet2 == "Venus") or 
            (planet1 == "Venus" and planet2 == "Mars")):
            if aspect_type in ["conjunction", "trine", "sextile"]:
                aspect_scores["passion"] += 8
            elif aspect_type == "square":
                aspect_scores["passion"] += 5  # 刑相可以创造紧张但也产生激情
            elif aspect_type == "opposition":
                aspect_scores["passion"] += 4  # 冲相可以创造强烈的吸引力
                
        # 火星和冥王星相位也影响激情
        if ((planet1 == "Mars" and planet2 == "Pluto") or 
            (planet1 == "Pluto" and planet2 == "Mars")):
            aspect_scores["passion"] += 6
            
        # 成长分数 - 受挑战相位和土星影响
        if aspect_type in ["square", "opposition"]:
            aspect_scores["growth"] += 3  # 挑战相位促进成长
            
        if (planet1 == "Saturn" or planet2 == "Saturn"):
            if aspect_type in ["trine", "sextile"]:
                aspect_scores["growth"] += 4  # 支持性土星相位
            else:
                aspect_scores["growth"] += 2  # 即使是具挑战性的土星相位也能带来成长
                
        # 木星相位有助于成长
        if (planet1 == "Jupiter" or planet2 == "Jupiter") and aspect_type in ["trine", "sextile", "conjunction"]:
            aspect_scores["growth"] += 3
    
    # 2. 应用星宿关系影响
    
    # 关系类型调整
    if relationship_type == "MAITRI":  # Soul Connection
        aspect_scores["harmony"] += 10
        aspect_scores["intimacy"] += 8
        aspect_scores["karmic_bond"] += 15
    elif relationship_type == "SAHAJ":  # Mutual Growth
        aspect_scores["harmony"] += 8
        aspect_scores["growth"] += 12
        aspect_scores["karmic_bond"] += 5
    elif relationship_type == "MITRA":  # Friendly Bonds
        aspect_scores["harmony"] += 7
        aspect_scores["intimacy"] += 4
        aspect_scores["growth"] += 6
    elif relationship_type == "KARMA":  # Karmic Bond
        aspect_scores["karmic_bond"] += 20
        aspect_scores["growth"] += 8
        aspect_scores["passion"] += 3
    elif relationship_type == "ADHI":  # Binding Forces
        aspect_scores["growth"] += 10
        aspect_scores["karmic_bond"] += 8
        aspect_scores["passion"] += 5
        aspect_scores["harmony"] -= 5
    elif relationship_type == "VAIRI":  # Dynamic Tension
        aspect_scores["passion"] += 10
        aspect_scores["growth"] += 7
        aspect_scores["harmony"] -= 8
        aspect_scores["karmic_bond"] += 6
    
    # 距离级别调整
    if distance_level == "NEAR":
        # 近距离增强所有方面
        for key in aspect_scores:
            aspect_scores[key] += 5
    elif distance_level == "FAR":
        # 远距离降低强度
        for key in aspect_scores:
            aspect_scores[key] -= 3
    
    # D9盘和谐度
    if d9_harmony:
        aspect_scores["harmony"] += 8
        aspect_scores["intimacy"] += 6
        aspect_scores["karmic_bond"] += 7
    
    # 行星能量影响
    energy_strength = planetary_energy.get("strength", 0)
    planets_involved = planetary_energy.get("planets_involved", [])
    
    if "SATURN" in planets_involved and "JUPITER" in planets_involved:
        # 土星-木星互动影响成长和业力连结
        aspect_scores["growth"] += energy_strength * 0.8
        aspect_scores["karmic_bond"] += energy_strength * 0.5
        
    if "MARS" in planets_involved and "VENUS" in planets_involved:
        # 火星-金星互动强烈影响激情和亲密度
        aspect_scores["passion"] += energy_strength * 1.2
        aspect_scores["intimacy"] += energy_strength * 0.7
        
    if "MOON" in planets_involved and "SUN" in planets_involved:
        # 月亮-太阳互动影响和谐度和亲密度
        aspect_scores["harmony"] += energy_strength * 1.0
        aspect_scores["intimacy"] += energy_strength * 1.0
        
    if "MERCURY" in planets_involved and "MARS" in planets_involved:
        # 水星-火星互动影响成长和激情
        aspect_scores["growth"] += energy_strength * 0.8
        aspect_scores["passion"] += energy_strength * 0.6
    
    # 3. 应用Ashtakoot兼容性影响
    ashtakoot_points = nakshatra_compatibility.get('ashtakoot_points', 0)
    
    # 较高的Ashtakoot点数通常提高和谐度
    if ashtakoot_points >= 20:
        aspect_scores["harmony"] += 8
        aspect_scores["intimacy"] += 6
    elif ashtakoot_points >= 16:
        aspect_scores["harmony"] += 4
        aspect_scores["intimacy"] += 3
    
    # Vedha和Rajju doshas
    if nakshatra_compatibility.get('vedha_dosha', False):
        aspect_scores["harmony"] -= 6
        aspect_scores["karmic_bond"] += 3  # 可能表示重要的业力课题
        
    if nakshatra_compatibility.get('rajju_dosha', False):
        aspect_scores["intimacy"] -= 5
        aspect_scores["growth"] += 4  # 促进成长的挑战
    
    # Mahendra对业力连结是正面的
    if nakshatra_compatibility.get('mahendra', False):
        aspect_scores["karmic_bond"] += 8
        aspect_scores["harmony"] += 4
    
    # 确保所有分数在0-100范围内
    for key in aspect_scores:
        aspect_scores[key] = max(0, min(100, aspect_scores[key]))
    
    # 给每个分数添加级别描述
    dimension_results = {}
    for dimension, score in aspect_scores.items():
        dimension_results[dimension] = {
            "score": score,
            "label": get_score_label(score),
            "description": get_dimension_description(dimension, score)
        }
    
    return dimension_results

def get_score_label(score):
    """根据分数获取评级标签"""
    if score >= 80:
        return "Excellent"
    elif score >= 65:
        return "Very Good"
    elif score >= 50:
        return "Good"
    elif score >= 35:
        return "Average"
    elif score >= 20:
        return "Challenging"
    else:
        return "Difficult"

def get_dimension_description(dimension, score):
    """获取特定维度的描述"""
    if dimension == "harmony":
        return get_harmony_description(score)
    elif dimension == "intimacy":
        return get_intimacy_description(score)
    elif dimension == "passion":
        return get_passion_description(score)
    elif dimension == "growth":
        return get_growth_description(score)
    elif dimension == "karmic_bond":
        return get_karmic_bond_description(score)
    else:
        return "No description available."

def get_harmony_description(score):
    """根据和谐度分数获取描述"""
    if score >= 80:
        return "Your relationship flows with exceptional ease. Communication is natural and you understand each other without effort."
    elif score >= 65:
        return "Your relationship has a harmonious quality with good flow in daily interactions and shared activities."
    elif score >= 50:
        return "Your relationship has moderate harmony with a balance of smooth and challenging interactions."
    elif score >= 35:
        return "Your relationship may face communication challenges that require conscious attention to overcome."
    else:
        return "Your relationship has significant harmony challenges that can lead to frequent misunderstandings."

def get_intimacy_description(score):
    """根据亲密度分数获取描述"""
    if score >= 80:
        return "Your relationship has profound emotional closeness with deep understanding and trust."
    elif score >= 65:
        return "Your relationship fosters good emotional intimacy with strong bonds of affection."
    elif score >= 50:
        return "Your relationship has moderate emotional intimacy with some areas of deep connection."
    elif score >= 35:
        return "Your relationship may struggle with emotional intimacy at times, requiring effort to maintain closeness."
    else:
        return "Your relationship faces challenges in developing and maintaining emotional intimacy."

def get_passion_description(score):
    """根据激情分数获取描述"""
    if score >= 80:
        return "Your relationship has powerful magnetic attraction and intense chemistry."
    elif score >= 65:
        return "Your relationship has strong attraction and good chemistry that enlivens your connection."
    elif score >= 50:
        return "Your relationship has moderate passion with periods of stronger attraction and chemistry."
    elif score >= 35:
        return "Your relationship may experience fluctuating levels of attraction and chemistry."
    else:
        return "Your relationship may lack natural chemistry, requiring effort to maintain attraction."

def get_growth_description(score):
    """根据成长分数获取描述"""
    if score >= 80:
        return "Your relationship offers exceptional opportunities for personal development and transformation."
    elif score >= 65:
        return "Your relationship provides strong growth potential through supporting each other's evolution."
    elif score >= 50:
        return "Your relationship offers moderate growth opportunities through both support and challenges."
    elif score >= 35:
        return "Your relationship presents growth challenges that require conscious engagement to benefit from."
    else:
        return "Your relationship contains difficult growth lessons that may feel overwhelming at times."

def get_karmic_bond_description(score):
    """根据业力连结分数获取描述"""
    if score >= 80:
        return "Your relationship has profound soul recognition with a deep sense of familiarity and purpose."
    elif score >= 65:
        return "Your relationship has strong karmic ties that feel meaningful and significant."
    elif score >= 50:
        return "Your relationship has moderate karmic connections with some sense of familiarity."
    elif score >= 35:
        return "Your relationship may have karmic lessons to work through together."
    else:
        return "Your relationship may involve challenging karmic patterns that require conscious resolution." 