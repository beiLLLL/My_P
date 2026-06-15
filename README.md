# 🎓 IELTS Speaking Simulator — AI 雅思口语模拟

> 基于 Python Flask + DeepSeek AI 的雅思口语全真模拟平台，8 位风格迥异的 AI 考官任你选。

---

## 🚀 功能模块

### 🎙️ 全真模拟考试
- 完整 Part 1 / Part 2 / Part 3 流程
- 实时进度条显示当前考试阶段
- 难度分级：Easy / Medium / Hard
- 流式打字机效果（SSE）

### 👤 8 位 AI 考官
| 考官 | 风格 |
|------|------|
| 🏀 Kobe | 黑曼巴，句尾带 "man"，冷酷好胜 |
| ❄️ 东雪莲 | 毒舌虚拟主播，中日英混搭 |
| 🪵 滚木 | 全程沉默，一个字都不说 |
| 📋 考官 | 严格专业的英式雅思考官 |
| 🐉 奶龙 | 只会"哈哈哈哈" |
| 🎮 少羽 | 暴躁游戏主播，全中文考试 |
| 😈 孙笑川 | 带带大师兄，全日语考试 |
| 🐱 塔菲 | 158岁侦探少女VTuber，句尾带 "miao~" |

### 📊 智能评分反馈
- AI 估分（0-9 分）
- 流利度 / 词汇 / 语法 / 发音 四维评估
- 个性化改进建议
- 考试结束自动弹出

### 🌐 中英双语切换
- 全站 UI 支持中/英文切换
- 考试对话不受影响

---

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python 3 + Flask |
| **数据库** | SQLAlchemy + SQLite |
| **AI** | DeepSeek API（原生 http.client 调用） |
| **实时通信** | SSE（Server-Sent Events）流式输出 |
| **前端** | Bootstrap 5 + Jinja2 模板 |
| **图标** | 🎓 学士帽 Favicon |

---

## 📦 环境配置

### 1. 安装依赖

```bash
cd ielts-talk
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑 `config.py`，将 `DASHSCOPE_API_KEY` 改为你的 DeepSeek API Key：

```python
DASHSCOPE_API_KEY = '你的DeepSeek_API_Key'
```

> 获取 Key：[DeepSeek 开放平台](https://platform.deepseek.com/)

### 3. 启动项目

```bash
python app.py
```

浏览器访问：**http://127.0.0.1:5000**

---

## 📂 项目结构

```
ielts-talk/
├── app.py                  # Flask 应用入口
├── config.py               # 配置文件（API Key、数据库）
├── models.py               # 数据库 ORM 模型
├── routes/
│   ├── auth.py             # 用户注册/登录
│   └── exam.py             # 考试核心路由（SSE + 反馈）
├── services/
│   └── llm.py              # DeepSeek AI 服务 + 8 位考官风格
├── static/
│   ├── css/style.css       # 样式
│   └── examiners/          # 考官头像
├── templates/
│   ├── base.html           # 公共模板（语言切换）
│   ├── index.html          # 首页
│   ├── login.html          # 登录/注册
│   └── exam.html           # 考试页面
├── requirements.txt
└── README.md
```

---

## 🎯 项目特色

- ✅ 3 个完整功能模块（全真模拟 + 智能评分 + 多考官切换）
- ✅ AI 深度融合（8 位考官各有独特人格）
- ✅ Flask + Jinja2 全栈开发
- ✅ SQLAlchemy ORM + SQLite
- ✅ SSE 流式响应
- ✅ RESTful API 设计
- ✅ 响应式前端 + 中英双语
