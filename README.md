# 星座占星API

这是一个基于Flask和flatlib的占星学API，提供星盘计算和合盘分析功能。API支持中英文双语输出，方便集成到各类应用中。

## 主要功能

### 1. 个人星盘分析
- 计算太阳、月亮、上升、金星、火星、水星、北交点、木星、土星等行星位置
- 计算行星之间的相位关系（合相、六分相、刑相、三分相、对分相）
- 支持自定义出生时间和地点
- 生成星盘SVG图表可视化
- 双语支持（英文/中文）

### 2. 合盘分析（关系占星）
- 两个星盘之间的行星相位分析
- 综合关系兼容性评分及分析
- 基于星宿（Nakshatra）的关系类型分析
- 提供关系维度评分（和谐度、亲密度、激情度、成长性、业力连结）
- 行星落宫分析
- 角色分配（如"发展催化剂"和"成长体验者"）

## 安装与配置

1. 克隆仓库
2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```
3. 安装依赖：
```bash
pip install -r requirements.txt
```

## API端点详解

### 个人星盘分析相关端点

#### 1. 主页 `GET /`
- 返回API基本信息和使用方法

#### 2. 计算星盘基本信息 `POST /api/calculate`
- 根据出生信息计算星盘中行星位置和相位
- 请求体格式：
```json
{
    "date": "YYYY-MM-DD",
    "time": "HH:MM:SS",
    "latitude": 纬度,
    "longitude": 经度,
    "language": "en"  // 可选，默认为"en"，可以设为"zh"获取中文
}
```
- 响应包含行星位置和相位信息

#### 3. 生成星盘图表 `POST /api/chart_svg`
- 生成星盘SVG图形
- 请求体格式与`/api/calculate`相同
- 返回SVG格式的星盘图

#### 4. 中文接口别名 `POST /api/calculate_zh`
- 与`/api/calculate`功能相同，默认返回中文结果

#### 5. 综合数据 `POST /api/combined`
- 同时返回星盘数据和SVG图表
- 请求体格式与`/api/calculate`相同
- 响应包含行星位置、相位信息和星盘SVG图表

### 合盘分析相关端点

#### 1. 合盘分析 `POST /api/compare`
- 分析两个星盘之间的关系
- 请求体格式：
```json
{
    "user1_date": "YYYY-MM-DD",
    "user1_time": "HH:MM:SS",
    "user1_lat": 纬度,
    "user1_lon": 经度,
    "user1_name": "Person A",  // 可选
    "user2_date": "YYYY-MM-DD",
    "user2_time": "HH:MM:SS",
    "user2_lat": 纬度,
    "user2_lon": 经度,
    "user2_name": "Person B",  // 可选
    "language": "en"  // 可选，默认为"en"，可以设为"zh"获取中文
}
```
- 响应内容：
  - 合盘相位列表
  - 总体兼容性评分与等级
  - 各维度评分（和谐度、亲密度、激情度、成长性、业力连结）
  - 关系类型与描述
  - 双方行星落宫情况
  - 双方在关系中的角色

## 响应示例

### 个人星盘分析响应示例
```json
{
    "success": true,
    "date": "1990-01-01",
    "time": "12:00:00",
    "latitude": 39.9042,
    "longitude": 116.4074,
    "planets": [
        {
            "sign": "Capricorn",
            "sign_cn": "摩羯座",
            "longitude": 280.81,
            "name": "Sun",
            "name_cn": "太阳"
        },
        // ... 其他行星信息
    ],
    "aspects": [
        {
            "planet1": "Sun",
            "planet2": "Moon",
            "type": 60,
            "type_name": "Sextile",
            "type_name_cn": "六分相",
            "orb": 7.55
        }
        // ... 其他相位信息
    ]
}
```

### 合盘分析响应示例
```json
{
    "aspects": [
        {
            "name": "sun conjunction moon",
            "orb": 3.25,
            "summary": "strong connection, merging energies"
        },
        // ... 其他相位信息
    ],
    "compatibility_level": "excellent",
    "compatibility_score": 85,
    "growth_level": "good",
    "growth_score": 75,
    "harmony_level": "excellent",
    "harmony_score": 90,
    "intimacy_level": "very good",
    "intimacy_score": 82,
    "karmic_level": "good",
    "karmic_score": 60,
    "p1p2_influence": "developmental catalyst",
    "p1p2_influence_sum": "Person A serves as the Developmental Catalyst.",
    "p1p2house": ["sun in 7th house", "moon in 3rd house", "..."],
    "p2p1_influence": "growth experiencer",
    "p2p1_influence_sum": "Person B serves as the Growth Experiencer.",
    "p2p1house": ["sun in 5th house", "moon in 11th house", "..."],
    "passion_level": "good",
    "passion_score": 65,
    "relationship_summary": "This is a strong connection with excellent harmony...",
    "relationship_type": "mutual growth",
    "relationship_type_score": 78,
    "status": "success"
}
```

## 客户端使用示例

### JavaScript/Fetch API
```javascript
// 获取个人星盘数据
async function fetchChart(birthData) {
  const response = await fetch('https://your-api-url/api/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(birthData)
  });
  return await response.json();
}

// 获取合盘分析
async function fetchSynastry(person1, person2) {
  const response = await fetch('https://your-api-url/api/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user1_date: person1.date,
      user1_time: person1.time,
      user1_lat: person1.latitude,
      user1_lon: person1.longitude,
      user1_name: person1.name,
      user2_date: person2.date,
      user2_time: person2.time,
      user2_lat: person2.latitude,
      user2_lon: person2.longitude,
      user2_name: person2.name
    })
  });
  return await response.json();
}
```

## 部署

### 部署到服务器
1. 确保安装了所有依赖
2. 使用gunicorn或uwsgi作为WSGI服务器
```bash
gunicorn app:app -b 0.0.0.0:5002
```

### 部署到云平台
#### Render
1. 在Render创建Web Service
2. 连接GitHub仓库
3. 设置构建命令：`pip install -r requirements.txt`
4. 设置启动命令：`gunicorn app:app`

## 注意事项
- 时间格式必须是24小时制 (HH:MM:SS)
- 日期格式必须是YYYY-MM-DD
- 经纬度必须是有效的数值
- 默认API返回英文，可通过language参数设置语言
- 服务默认运行在5002端口 