# Star API - 星座占星API服务

A comprehensive astrology API service providing daily horoscope calculations, synastry analysis, and astrological chart calculations.

一个综合性的占星学API服务，提供每日运势计算、合盘分析和星盘计算功能。

## 🌟 主要功能 / Main Features

### 新功能 / New Features
- **🔮 每日运势分析 / Daily Fortune Analysis**: 基于出生信息的个性化每日运势
- **📊 百分制评分 / Percentage Scoring**: 1-100整数评分系统
- **🎯 生活领域预测 / Life Area Forecasts**: 事业、爱情、健康、成长四大领域
- **🌙 详细月相信息 / Detailed Lunar Information**: 月相名称、照明度、能量类型
- **🍀 幸运元素 / Lucky Elements**: 幸运数字、颜色、方位、宝石
- **📋 扁平化JSON结构 / Flat JSON Structure**: 30个字段的单层JSON结构

### 原有功能 / Existing Features
- **⭐ 个人星盘分析 / Personal Chart Analysis**: 行星位置、相位关系计算
- **💕 合盘分析 / Synastry Analysis**: 两人关系兼容性分析
- **📈 综合兼容性评分 / Compatibility Scoring**: 多维度关系评估
- **🎨 星盘图表生成 / Chart Visualization**: SVG格式星盘图
- **🌍 中英双语支持 / Bilingual Support**: 中文/英文双语输出

## 🚀 API接口 / API Endpoints

### 1. 每日运势分析 / Daily Fortune Analysis
```
POST /api/daily
```

根据出生信息计算个性化每日运势 / Calculate personalized daily fortune based on birth information.

#### 请求格式 / Request Body
```json
{
    "birth_date": "1990-06-15",
    "birth_time": "10:30:00",
    "birth_latitude": 40.7128,
    "birth_longitude": -74.0060,
    "target_date": "2025-06-13"
}
```

#### 响应结构 (30个字段) / Response Structure (30 Fields)
```json
{
    "success": true,
    "date": "2025-06-13",
    
    // 运势概览 / Fortune Overview
    "fortune_score": 92,
    "fortune_level": "Exceptionally Favorable",
    "fortune_summary": "今日星象配置特别有利，为您的生活带来持久的积极影响...",
    "wisdom_for_today": "相信你的直觉，它是指引你走向最高善的内在指南针",
    
    // 幸运元素 / Lucky Elements
    "lucky_numbers": [1, 3, 29],
    "lucky_colors": ["Navy Blue", "Ivory"],
    "lucky_direction": "Southeast",
    "lucky_stone": "Moonstone",
    
    // 生活领域预测 / Life Area Forecasts
    "career_rating": 4,
    "career_forecast": "火星的影响今天激发了你的职业雄心...",
    "career_tip": "专注于解决问题而不是发现问题...",
    
    "love_rating": 3,
    "love_forecast": "月亮的影响增强了你对他人需求的直觉理解...",
    "love_tip": "在关系中练习脆弱性，真实的分享比试图表现完美更能加深联系",
    
    "health_rating": 5,
    "health_forecast": "你的体力从火星的激励影响中得到提升...",
    "health_tip": "如果可能的话，花时间在大自然中...",
    
    "growth_rating": 5,
    "growth_forecast": "海王星的直觉影响增强了你与内在智慧的连接...",
    "growth_tip": "留出时间进行头脑风暴或创意项目...",
    
    // 每日指导 / Daily Guidance
    "focus_today": "今日的天体影响为有意义的关系建设创造了强大背景...",
    "challenges_today": "火星的影响今天可能表现为对过程的不耐烦...",
    
    // 月相信息 / Lunar Phase Information
    "lunar_phase_name": "Waning Gibbous",
    "lunar_illumination_percent": 84.9,
    "lunar_energy_type": "Gratitude & Sharing",
    "days_to_next_lunar_phase": 5.1,
    "lunar_phase_description": "月亮开始减弱，鼓励分享智慧并对最近的成就表达感激...",
    
    // 吉时建议 / Auspicious Hours
    "auspicious_hours": [
        {"time_range": "7:00-9:00", "activity": "Meditation & Planning"},
        {"time_range": "13:00-15:00", "activity": "Business Meetings"}
    ]
}
```

### 2. 个人星盘分析 / Personal Chart Analysis

#### 基本星盘计算 / Basic Chart Calculation
```
POST /api/calculate
```

#### 中文接口 / Chinese Interface
```
POST /api/calculate_zh
```

#### 请求格式 / Request Body
```json
{
    "date": "1990-01-01",
    "time": "12:00:00",
    "latitude": 39.9042,
    "longitude": 116.4074,
    "language": "zh"
}
```

#### 星盘图表生成 / Chart Visualization
```
POST /api/chart_svg
```

#### 综合数据 / Combined Data
```
POST /api/combined
```

### 3. 合盘分析 / Synastry Analysis
```
POST /api/synastry
POST /api/compare
```

计算两人关系兼容性 / Calculate relationship compatibility between two people.

#### 请求格式 / Request Body
```json
{
    "user1_date": "1990-05-15",
    "user1_time": "14:30:00",
    "user1_lat": 40.7128,
    "user1_lon": -74.0060,
    "user1_name": "Person A",
    "user2_date": "1992-08-22",
    "user2_time": "09:15:00",
    "user2_lat": 34.0522,
    "user2_lon": -118.2437,
    "user2_name": "Person B",
    "language": "zh"
}
```

#### 响应示例 / Response Example
```json
{
    "status": "success",
    "compatibility_score": 85,
    "compatibility_level": "excellent",
    "relationship_type": "mutual growth",
    "relationship_summary": "这是一个具有出色和谐度的强大连接...",
    "aspects": [
        {
            "name": "sun conjunction moon",
            "orb": 3.25,
            "summary": "强烈的连接，能量融合"
        }
    ],
    "harmony_score": 90,
    "intimacy_score": 82,
    "passion_score": 65,
    "growth_score": 75,
    "karmic_score": 60,
    "p1p2_influence": "developmental catalyst",
    "p2p1_influence": "growth experiencer"
}
```

## 📊 字段参考 / Field Reference

### 每日运势字段 / Daily Fortune Fields

| 字段名 / Field | 类型 / Type | 说明 / Description |
|----------------|-------------|-------------------|
| `fortune_score` | integer (1-100) | 每日运势百分比评分 / Daily fortune percentage |
| `fortune_level` | string | 运势等级分类 / Fortune level classification |
| `fortune_summary` | string | 详细运势分析 (2-3句话) / Extended analysis |
| `career_rating` | integer (1-5) | 事业运势评分 / Career prospects rating |
| `love_rating` | integer (1-5) | 爱情运势评分 / Love prospects rating |
| `health_rating` | integer (1-5) | 健康运势评分 / Health prospects rating |
| `growth_rating` | integer (1-5) | 成长运势评分 / Growth prospects rating |
| `lunar_phase_name` | string | 当前月相名称 / Current moon phase |
| `lunar_illumination_percent` | float | 月亮照明百分比 / Moon illumination percentage |
| `lunar_energy_type` | string | 月相能量类型 / Phase energy classification |

### 星盘分析字段 / Chart Analysis Fields

| 字段名 / Field | 类型 / Type | 说明 / Description |
|----------------|-------------|-------------------|
| `planets` | array | 行星位置信息 / Planetary positions |
| `aspects` | array | 行星相位关系 / Planetary aspects |
| `houses` | array | 宫位信息 / House positions |

### 合盘分析字段 / Synastry Fields

| 字段名 / Field | 类型 / Type | 说明 / Description |
|----------------|-------------|-------------------|
| `compatibility_score` | integer (0-100) | 总体兼容性评分 / Overall compatibility |
| `harmony_score` | integer (0-100) | 和谐度评分 / Harmony score |
| `intimacy_score` | integer (0-100) | 亲密度评分 / Intimacy score |
| `passion_score` | integer (0-100) | 激情度评分 / Passion score |
| `growth_score` | integer (0-100) | 成长性评分 / Growth score |

## 🛠️ 安装与部署 / Installation & Deployment

### 本地开发 / Local Development
```bash
# 安装依赖 / Install dependencies
pip install -r requirements.txt

# 本地运行 / Run locally
python app.py
```

### Render部署 / Render Deployment
1. 连接GitHub仓库到Render / Connect GitHub repository to Render
2. 创建新的Web服务 / Create new Web Service
3. 配置设置 / Configure settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

### 环境要求 / Requirements
- Python 3.8+
- Flask 3.0.0
- flatlib 0.4.1
- pytz 2023.3

## 🔧 集成示例 / Integration Examples

### JavaScript/Fetch
```javascript
// 每日运势 / Daily Fortune
const dailyResponse = await fetch('/api/daily', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        birth_date: "1990-06-15",
        birth_time: "10:30:00",
        birth_latitude: 40.7128,
        birth_longitude: -74.0060
    })
});

const dailyData = await dailyResponse.json();
console.log(dailyData.fortune_score); // 92

// 合盘分析 / Synastry Analysis
const synastryResponse = await fetch('/api/synastry', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        user1_date: "1990-05-15",
        user1_time: "14:30:00",
        user1_lat: 40.7128,
        user1_lon: -74.0060,
        user2_date: "1992-08-22",
        user2_time: "09:15:00",
        user2_lat: 34.0522,
        user2_lon: -118.2437
    })
});

const synastryData = await synastryResponse.json();
console.log(synastryData.compatibility_score); // 85
```

### Bubble.io集成 / Bubble.io Integration
将API字段直接映射到数据库列 / Map API fields directly to database columns:
- `fortune_score` → 数字字段 / Number field
- `career_forecast` → 长文本字段 / Long text field
- `lucky_numbers` → 列表字段 / List field
- `compatibility_score` → 数字字段 / Number field

### Python示例 / Python Example
```python
import requests

# 每日运势 / Daily Fortune
response = requests.post('http://your-api-url/api/daily', json={
    "birth_date": "1990-06-15",
    "birth_time": "10:30:00",
    "birth_latitude": 40.7128,
    "birth_longitude": -74.0060
})

data = response.json()
print(f"运势评分 / Fortune Score: {data['fortune_score']}/100")

# 合盘分析 / Synastry Analysis
synastry_response = requests.post('http://your-api-url/api/synastry', json={
    "user1_date": "1990-05-15",
    "user1_time": "14:30:00",
    "user1_lat": 40.7128,
    "user1_lon": -74.0060,
    "user2_date": "1992-08-22",
    "user2_time": "09:15:00",
    "user2_lat": 34.0522,
    "user2_lon": -118.2437
})

synastry_data = synastry_response.json()
print(f"兼容性评分 / Compatibility: {synastry_data['compatibility_score']}/100")
```

## 📁 项目结构 / Project Structure

```
star-api-main/
├── app.py                      # Flask主应用 / Flask application
├── requirements.txt            # 依赖包 / Dependencies
├── Procfile                   # Render部署配置 / Render deployment config
├── README.md                  # 项目文档 / Project documentation
├── .gitignore                 # Git忽略配置 / Git ignore config
├── daily_fortune_service/     # 每日运势模块 / Daily fortune module
│   ├── __init__.py
│   ├── core.py               # 主要计算逻辑 / Main calculation logic
│   └── utils.py              # 辅助工具函数 / Helper functions
└── synastry_service/         # 合盘分析模块 / Synastry module
    └── ...
```

## 🌍 内容质量 / Content Quality

- **语言 / Language**: 地道的中英双语 / Natural Chinese and English
- **语调 / Tone**: 专业且易于理解 / Professional yet accessible
- **多样性 / Variety**: 多种内容变化避免重复 / Multiple variations to prevent repetition
- **文化 / Cultural**: 符合东西方占星传统 / Eastern and Western astrology traditions

## 📈 API状态 / API Status

- ✅ **生产就绪 / Production Ready**
- ✅ **Render部署优化 / Render Deployment Optimized**
- ✅ **Bubble.io兼容 / Bubble.io Compatible**
- ✅ **30个综合数据字段 / 30 Comprehensive Data Fields**
- ✅ **扁平化JSON结构 / Flat JSON Structure**
- ✅ **中英双语支持 / Bilingual Support**

## 🔒 CORS支持 / CORS Support

API支持跨域请求，适用于 / The API includes CORS headers for cross-origin requests, suitable for:
- 前端Web应用 / Frontend web applications
- 移动应用后端 / Mobile app backends
- 第三方集成 / Third-party integrations

## 📞 技术支持 / Technical Support

如需API访问权限或集成支持，请联系开发团队。
For API access and integration support, please contact the development team.

---

**版本 / Version**: 2.0  
**许可证 / License**: 专有 / Proprietary  
**最后更新 / Last Updated**: 2025-06
