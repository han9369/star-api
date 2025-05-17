from flatlib import const
import math

# 星宿映射表 - 将黄道度数映射到对应的27星宿
NAKSHATRA_MAPPING = {
    1: "Ashwini",     # 0° - 13°20'
    2: "Bharani",     # 13°20' - 26°40'
    3: "Krittika",    # 26°40' - 40°
    4: "Rohini",      # 40° - 53°20'
    5: "Mrigashira",  # 53°20' - 66°40'
    6: "Ardra",       # 66°40' - 80°
    7: "Punarvasu",   # 80° - 93°20'
    8: "Pushya",      # 93°20' - 106°40'
    9: "Ashlesha",    # 106°40' - 120°
    10: "Magha",      # 120° - 133°20'
    11: "Purva Phalguni", # 133°20' - 146°40'
    12: "Uttara Phalguni", # 146°40' - 160°
    13: "Hasta",      # 160° - 173°20'
    14: "Chitra",     # 173°20' - 186°40'
    15: "Swati",      # 186°40' - 200°
    16: "Vishakha",   # 200° - 213°20'
    17: "Anuradha",   # 213°20' - 226°40'
    18: "Jyestha",    # 226°40' - 240°
    19: "Mula",       # 240° - 253°20'
    20: "Purva Ashadha", # 253°20' - 266°40'
    21: "Uttara Ashadha", # 266°40' - 280°
    22: "Shravana",   # 280° - 293°20'
    23: "Dhanishta",  # 293°20' - 306°40'
    24: "Shatabhisha", # 306°40' - 320°
    25: "Purva Bhadrapada", # 320° - 333°20'
    26: "Uttara Bhadrapada", # 333°20' - 346°40'
    27: "Revati"      # 346°40' - 360°
}

# 星宿特性分类 - 根据Ashtakoot Milan系统
NAKSHATRA_PROPERTIES = {
    # Gana (气质类型): Deva(神性), Manushya(人性), Rakshasa(罗刹)
    "GANA": {
        "DEVA": [1, 5, 7, 8, 13, 15, 17, 22, 27],   # 神性: 忠诚、开放、奉献
        "MANUSHYA": [2, 4, 6, 11, 12, 20, 21, 25, 26], # 人性: 实用、进步
        "RAKSHASA": [3, 9, 10, 14, 16, 18, 19, 23, 24]  # 罗刹: 独立、超然、打破常规
    },
    # Nadi (能量通道): Vata(风), Pitta(火), Kapha(水)
    "NADI": {
        "VATA": [1, 6, 7, 12, 13, 18, 19, 24, 25], # 风: 轻盈、变化、干燥
        "PITTA": [2, 5, 8, 11, 14, 17, 20, 23, 26], # 火: 热情、转化、强度
        "KAPHA": [3, 4, 9, 10, 15, 16, 21, 22, 27]  # 水: 冷静、稳定、滋养
    },
    # Yoni (动物属性): 动物对应星宿的本能性质
    "YONI": {
        "HORSE_MALE": [1],
        "ELEPHANT_MALE": [2],
        "SHEEP_FEMALE": [3],
        "SNAKE_MALE": [4], 
        "SNAKE_FEMALE": [5],
        "DOG_FEMALE": [6],
        "CAT_FEMALE": [7],
        "SHEEP_MALE": [8],
        "CAT_MALE": [9],
        "RAT_MALE": [10],
        "RAT_FEMALE": [11],
        "COW_MALE": [12],
        "BUFFALO_FEMALE": [13],
        "TIGER_FEMALE": [14],
        "BUFFALO_MALE": [15],
        "TIGER_MALE": [16],
        "HARE_FEMALE": [17],
        "HARE_MALE": [18],
        "DOG_MALE": [19],
        "MONKEY_MALE": [20],
        "MONGOOSE_MALE": [21],
        "MONKEY_FEMALE": [22],
        "LION_FEMALE": [23],
        "HORSE_FEMALE": [24],
        "LION_MALE": [25],
        "COW_FEMALE": [26],
        "ELEPHANT_FEMALE": [27]
    },
    # Rajju (身体部位): 用于检测Rajju Dosha
    "RAJJU": {
        "FEET": [1, 9, 10, 18, 19, 27], # 脚
        "HIP": [2, 8, 11, 17, 20, 26],  # 臀部
        "NECK": [3, 7, 12, 16, 21, 25], # 颈部
        "NAVEL": [4, 6, 13, 15, 22, 24], # 肚脐
        "HEAD": [5, 14, 23]  # 头部
    },
    # Vedha (障碍): 互相阻碍的星宿对
    "VEDHA": {
        1: [18],  # Ashwini & Jyeshtha
        2: [17],  # Bharani & Anuradha
        3: [16],  # Krittika & Vishakha
        4: [15],  # Rohini & Swati
        5: [14, 23],  # Mrigashira & Chitra & Dhanishta
        6: [22],  # Ardra & Shravana
        7: [21],  # Punarvasu & Uttarashada
        8: [20],  # Pushya & Purvashada
        9: [19],  # Ashlesha & Mula
        10: [27],  # Magha & Revati
        11: [26],  # Purva Phalguni & Uttarabhadrapada
        12: [25],  # Uttara Phalguni & Purvabhadrapada
        13: [24],  # Hasta & Shatabhisha
        14: [5, 23],  # Chitra & Mrigashira & Dhanishta
        15: [4],  # Swati & Rohini
        16: [3],  # Vishakha & Krittika
        17: [2],  # Anuradha & Bharani
        18: [1],  # Jyeshtha & Ashwini
        19: [9],  # Mula & Ashlesha
        20: [8],  # Purva Ashadha & Pushya
        21: [7],  # Uttara Ashadha & Punarvasu
        22: [6],  # Shravana & Ardra
        23: [5, 14],  # Dhanishta & Mrigashira & Chitra 
        24: [13],  # Shatabhisha & Hasta
        25: [12],  # Purva Bhadrapada & Uttara Phalguni
        26: [11],  # Uttara Bhadrapada & Purva Phalguni
        27: [10]   # Revati & Magha
    }
}

# 关系类型定义
RELATIONSHIP_TYPES = {
    "MAITRI": "Soul Connection",   # 命之星 - 同一星宿
    "KARMA": "Karmic Bond",        # 业胎 - 业力关系
    "SAHAJ": "Mutual Growth",      # 荣亲 - 成长关系
    "MITRA": "Friendly Bonds",     # 友衰 - 友谊关系
    "ADHI": "Binding Forces",      # 安坏 - 约束关系
    "VAIRI": "Dynamic Tension"     # 危成 - 挑战关系
}

def get_nakshatra_number(moon_longitude):
    """
    根据月亮黄道经度计算星宿编号(1-27)
    每个星宿占据13°20'的黄道
    """
    # 标准化黄道经度到0-360范围
    moon_longitude = moon_longitude % 360
    
    # 计算星宿编号 (0-26)
    nakshatra_index = int(moon_longitude / (360/27))
    
    # 转换为1-27的范围
    nakshatra_num = nakshatra_index + 1
    
    # 确保星宿编号在有效范围内(1-27)
    if nakshatra_num < 1:
        nakshatra_num = 1
    elif nakshatra_num > 27:
        nakshatra_num = 27
    
    return nakshatra_num

def calculate_nakshatra_interval(nakshatra1, nakshatra2):
    """
    计算两个星宿之间的间隔
    """
    # 确保输入是1-27范围内
    nakshatra1 = (nakshatra1 - 1) % 27 + 1
    nakshatra2 = (nakshatra2 - 1) % 27 + 1
    
    # 计算星宿间隔(正向)
    forward = (nakshatra2 - nakshatra1) % 27
    if forward == 0:
        forward = 27
    
    return forward

def determine_relationship_type(interval):
    """
    根据星宿间隔确定关系类型
    关系类型基于印度占星传统，且按照特定间隔值分类:
    - MAITRI (命之星): 同一星宿 (间隔=0或27)
    - KARMA (业胎): 间隔=1、10、19
    - ADHI (安坏): 间隔=3、12、21或6、15、24
    - VAIRI (危成): 间隔=8、17、26或5、14、23
    - MITRA (友衰): 间隔=1、10、19或4、13、22
    - SAHAJ (荣亲): 间隔=2、11、20或9、18、27
    """
    # 标准关系类型及其对应的间隔值
    standard_intervals = {
        "MAITRI": [0, 27],                     # 命之星(同一星宿)
        "KARMA": [1, 10, 19],                  # 业胎
        "ADHI": [3, 12, 21, 6, 15, 24],        # 安坏
        "VAIRI": [8, 17, 26, 5, 14, 23],       # 危成
        "MITRA": [1, 10, 19, 4, 13, 22],       # 友衰
        "SAHAJ": [2, 11, 20, 9, 18, 27]        # 荣亲
    }
    
    # 直接检查间隔是否在各关系类型的标准间隔中
    for rel_type, intervals in standard_intervals.items():
        if interval in intervals:
            return rel_type
    
    # 如果不是标准间隔，计算与各标准间隔的差距，选择最接近的
    min_diff = float('inf')
    closest_type = "MAITRI"  # 默认值
    
    for rel_type, intervals in standard_intervals.items():
        for std_interval in intervals:
            diff = abs(interval - std_interval)
            if diff < min_diff:
                min_diff = diff
                closest_type = rel_type
    
    return closest_type

def get_relationship_level(interval, relationship_type):
    """
    获取关系强度级别
    NEAR: 强关系
    MODERATE: 中等关系
    FAR: 弱关系
    Soul Connection和Karmic Bond没有强度级别
    """
    # Soul Connection和Karmic Bond不考虑强度级别
    if relationship_type in ["MAITRI", "KARMA"]:
        return "FIXED"  # 固定强度，无级别
    
    # 根据间隔计算强度级别
    if interval <= 5:
        return "NEAR"
    elif interval <= 14:
        return "MODERATE"
    else:
        return "FAR"

def get_relationship_description(relationship_type, distance_level):
    """
    获取关系类型和强度描述，并返回组合关系名称
    """
    # 获取关系类型英文名称
    en_relationship_names = {
        "MAITRI": "Soul Connection",
        "KARMA": "Karmic Bond",
        "SAHAJ": "Mutual Growth",
        "MITRA": "Friendly Bonds",
        "ADHI": "Binding Forces",
        "VAIRI": "Dynamic Tension"
    }
    
    en_level_names = {
        "NEAR": "NEAR ",
        "MODERATE": "MODERATE ",
        "FAR": "FAR ",
        "FIXED": ""  # Soul Connection和Karmic Bond没有距离前缀
    }
    
    # 获取英文关系名称
    en_type = en_relationship_names.get(relationship_type, "Unknown Relationship")
    en_level = en_level_names.get(distance_level, "")
    
    # 组合为单个字段
    combined_relationship_name = f"{en_level}{en_type}"
    
    # 生成关系描述
    if relationship_type == "MAITRI":
        description = "You share a profound soul connection, with deep intuitive understanding and recognition of each other."
    elif relationship_type == "KARMA":
        description = "You share significant karmic ties from past lives, with important lessons to learn together."
    elif relationship_type == "SAHAJ":
        if distance_level == "NEAR":
            description = "Your relationship promotes strong mutual growth and development, with natural harmony."
        elif distance_level == "MODERATE":
            description = "Your relationship supports moderate mutual growth, with generally harmonious interactions."
        else:
            description = "Your relationship has potential for growth, though you may need to work at understanding each other."
    elif relationship_type == "MITRA":
        if distance_level == "NEAR":
            description = "You share strong friendly bonds with natural support and easy communication."
        elif distance_level == "MODERATE":
            description = "You share moderately friendly bonds, generally supporting each other's endeavors."
        else:
            description = "Your friendly bonds require cultivation to fully support each other."
    elif relationship_type == "ADHI":
        if distance_level == "NEAR":
            description = "Your relationship has strong binding forces that create structure but can feel constraining."
        elif distance_level == "MODERATE":
            description = "Your relationship has moderate binding forces, creating some structure and occasional constraints."
        else:
            description = "Your relationship has mild binding forces, with subtle structural patterns."
    elif relationship_type == "VAIRI":
        if distance_level == "NEAR":
            description = "Your relationship has strong dynamic tension, creating intense growth opportunities through challenges."
        elif distance_level == "MODERATE":
            description = "Your relationship has moderate dynamic tension, with periodic challenges that promote growth."
        else:
            description = "Your relationship has mild dynamic tension, with occasional challenges."
    else:
        description = "Your relationship has unique qualities that may require deeper analysis to fully understand."
    
    return combined_relationship_name, description

def check_vedha_dosha(nakshatra1, nakshatra2):
    """检查是否有Vedha Dosha（星宿互阻）"""
    # 获取可能与第一个星宿有阻碍的星宿列表
    vedha_list1 = NAKSHATRA_PROPERTIES["VEDHA"].get(nakshatra1, [])
    vedha_list2 = NAKSHATRA_PROPERTIES["VEDHA"].get(nakshatra2, [])
    
    # 检查第二个星宿是否在第一个星宿的阻碍列表中，或者反之
    return nakshatra2 in vedha_list1 or nakshatra1 in vedha_list2

def check_rajju_dosha(nakshatra1, nakshatra2):
    """检查是否有Rajju Dosha（身体部位冲突）"""
    # 获取每个星宿对应的身体部位
    rajju1 = None
    rajju2 = None
    
    for body_part, nakshatras in NAKSHATRA_PROPERTIES["RAJJU"].items():
        if nakshatra1 in nakshatras:
            rajju1 = body_part
        if nakshatra2 in nakshatras:
            rajju2 = body_part
    
    # 如果两个星宿对应相同的身体部位，则有Rajju Dosha
    return rajju1 == rajju2

def check_nadi_kuta(nakshatra1, nakshatra2):
    """检查Nadi Kuta（能量通道和谐度）"""
    # 获取每个星宿的Nadi类型
    nadi1 = None
    nadi2 = None
    
    for nadi_type, nakshatras in NAKSHATRA_PROPERTIES["NADI"].items():
        if nakshatra1 in nakshatras:
            nadi1 = nadi_type
        if nakshatra2 in nakshatras:
            nadi2 = nadi_type
    
    # 如果Nadi类型不同，则获得8分（满分），否则0分
    return 8 if nadi1 != nadi2 else 0

def calculate_d9_position(moon_longitude):
    """
    计算月亮的D9九分图位置
    返回星座和主宰行星
    """
    # 每个星座占据30度
    moon_sign = int(moon_longitude / 30) + 1
    
    # D9细分 - 每个星座被分为9个部分，每部分3度20分
    d9_division = int((moon_longitude % 30) / (30/9)) + 1
    
    # 计算最终D9位置 (1-12)
    final_d9 = ((d9_division - 1) + (moon_sign - 1)) % 12 + 1
    
    # 星座名称映射
    sign_names = {
        1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer", 
        5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
        9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces"
    }
    
    # 星座主宰行星映射
    sign_rulers = {
        1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 
        5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars/Pluto",
        9: "Jupiter", 10: "Saturn", 11: "Saturn/Uranus", 12: "Jupiter/Neptune"
    }
    
    return {
        "sign": final_d9,
        "sign_name": sign_names.get(final_d9, "Unknown"),
        "ruler": sign_rulers.get(final_d9, "Unknown")
    }

def get_relationship_base_score(relationship_type):
    """获取关系类型的基础分数"""
    base_scores = {
        "MAITRI": 90,  # Soul Connection - 最高基础分
        "SAHAJ": 80,   # Mutual Growth - 第二高
        "MITRA": 70,   # Friendly Bonds - 第三高
        "KARMA": 60,   # Karmic Bond - 中等
        "ADHI": 50,    # Binding Forces - 略低
        "VAIRI": 40    # Dynamic Tension - 最低基础分
    }
    
    return base_scores.get(relationship_type, 50)  # 默认为50

def get_consistent_roles(relationship_type):
    """获取关系类型的一致角色分配"""
    if relationship_type == "MAITRI":  # 命之星 - 对等关系
        return "Soul Resonator", "Soul Resonator"
    elif relationship_type == "KARMA":  # 业胎 - 业力关系
        return "Karmic Initiator", "Karmic Recipient"
    elif relationship_type == "VAIRI":  # 危成 - 挑战关系
        return "Dynamic Catalyst", "Transformation Subject"
    elif relationship_type == "ADHI":  # 安坏 - 约束关系
        return "Structural Influence", "Boundary Experiencer"
    elif relationship_type == "SAHAJ":  # 荣亲 - 成长关系
        return "Developmental Catalyst", "Growth Experiencer"
    elif relationship_type == "MITRA":  # 友衰 - 友谊关系
        return "Supportive Influence", "Energy Beneficiary"
    else:
        return "Energy Projector", "Energy Receptor"  # 默认角色

def check_mahendra(nakshatra_man, nakshatra_woman):
    """
    检查是否有Mahendra吉祥组合
    男性星宿距离女性星宿应为4, 7, 10, 13, 16, 19, 22, 或25个星宿
    """
    # 计算男性星宿距离女性星宿的位置
    diff = (nakshatra_man - nakshatra_woman) % 27
    if diff == 0:
        diff = 27
    
    # 检查是否为吉祥数字
    auspicious_differences = [4, 7, 10, 13, 16, 19, 22, 25]
    
    return diff in auspicious_differences

def get_comprehensive_compatibility(nakshatra1, nakshatra2):
    """
    获取全面的星宿兼容性评估，包括所有的doshas和gunas
    """
    # 检查各种星宿问题
    vedha_dosha = check_vedha_dosha(nakshatra1, nakshatra2)
    rajju_dosha = check_rajju_dosha(nakshatra1, nakshatra2)
    
    # 检查积极因素
    mahendra = check_mahendra(nakshatra1, nakshatra2)
    
    # 计算Ashtakoot分数
    # 简化版本，实际实现需要更多的配对计算
    ashtakoot_points = 25  # 假设默认值
    
    # 获取兼容性等级
    compatibility_level = "Good"
    if ashtakoot_points >= 30:
        compatibility_level = "Excellent"
    elif ashtakoot_points >= 24:
        compatibility_level = "Very Good"
    elif ashtakoot_points >= 18:
        compatibility_level = "Good"
    else:
        compatibility_level = "Average"
    
    # 构建结果
    result = {
        "vedha_dosha": vedha_dosha,
        "rajju_dosha": rajju_dosha,
        "mahendra": mahendra,
        "ashtakoot_points": ashtakoot_points,
        "compatibility_level": compatibility_level,
        "explanation": f"Ashtakoot score: {ashtakoot_points}/36. " +
                      ("Vedha Dosha is present. " if vedha_dosha else "") +
                      ("Rajju Dosha is present. " if rajju_dosha else "") +
                      ("Beneficial Mahendra is present. " if mahendra else "")
    }
    
    return result 