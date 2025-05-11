# 星座计算 API

这是一个基于 Flask 和 flatlib 的星座计算 API，可以计算用户的太阳、月亮、上升等星盘信息。API主要使用英文输出，同时保留中文翻译，方便集成到英文网站。

## 功能特点

- 计算太阳、月亮、上升、金星、火星、水星、北交、木星、土星等行星位置
- 计算行星之间的相位关系（合相、六分相、刑相、三分相、对分相）
- 支持自定义出生时间和地点
- 双语支持（主要英文，带中文翻译）
- RESTful API 设计
- 支持 CORS，可用于前端应用

## 安装

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

## 使用方法

### API 端点

#### 主页 GET `/`

返回 API 基本信息和使用方法。

#### 计算星盘 POST `/api/calculate`

请求体格式：
```json
{
    "date": "YYYY-MM-DD",
    "time": "HH:MM:SS",
    "latitude": 纬度,
    "longitude": 经度,
    "language": "en"  // 可选，默认为"en"，可以设为"cn"获取中文
}
```

示例：
```json
{
    "date": "1990-01-01",
    "time": "12:00:00",
    "latitude": 39.9042,
    "longitude": 116.4074
}
```

响应格式：
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
            "latitude": 0.0,
            "name": "Sun",
            "name_cn": "太阳"
        },
        // ... 其他行星信息
    ],
    "aspects": [
        {
            "planet1": "Sun",
            "planet2": "Moon",
            "planet1_cn": "太阳",
            "planet2_cn": "月亮",
            "type": 60,
            "type_name": "Sextile",
            "type_name_cn": "六分相",
            "orb": 7.55
        }
        // ... 其他相位信息
    ]
}
```

## 测试 API

可以使用提供的 `test_api.py` 脚本进行测试：
```bash
python test_api.py
```

或者使用 curl 命令：
```bash
curl -X POST http://localhost:5001/api/calculate \
-H "Content-Type: application/json" \
-d '{"date":"1990-01-01","time":"12:00:00","latitude":39.9042,"longitude":116.4074}'
```

## 部署到 Render

1. 在 Render 上创建新的 Web Service
2. 连接你的 GitHub 仓库
3. 选择 Python 环境
4. 设置构建命令：`pip install -r requirements.txt`
5. 设置启动命令：`gunicorn app:app`

## 在 Bubble.io 中使用

1. 在 Bubble.io 中创建新的 API 连接
2. 输入部署在 Render 上的 API 地址
3. 使用 POST 方法调用 `/api/calculate` 端点
4. 处理返回的 JSON 数据

## 注意事项

- 时间格式必须是 24 小时制 (HH:MM:SS)
- 日期格式必须是 YYYY-MM-DD
- 经纬度必须是有效的数值
- API 返回的星座和行星名称同时包含英文和中文 