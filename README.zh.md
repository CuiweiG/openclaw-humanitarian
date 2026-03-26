[English](README.md) | [فارسی](README.fa.md) | [العربية](README.ar.md) | **中文** | [Français](README.fr.md) | [Español](README.es.md) | [Русский](README.ru.md)

---

# 🌍 CrisisBridge 人道主义网络

**为受中东危机影响的平民提供 AI 驱动的多语言人道主义简报。**

[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://t.me/openclaw_aid_bot)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 问题背景

炸弹落下时，信息的重要性不亚于水。

目前，伊朗、黎巴嫩和叙利亚数百万人正深陷不断升级的军事冲突。OCHA、WFP 和 UNHCR 等国际组织每天发布情况报告，但这些报告：

- **以英文撰写** — 而最需要它们的人却说阿拉伯语、波斯语和达里语
- **发布于网站** — 许多流离失所者在低带宽移动连接下根本无法访问
- **充满专业术语** — 即便是英语流利的人也难以快速理解

结果：形成了一个**人道主义信息鸿沟**——救命数据就在那里，却无法抵达需要它的人。

### 数据统计

- **60万至100万**户家庭仅在伊朗就已流离失所（UNHCR，2026年3月）
- **33,000** 名阿富汗难民在伊朗接受 WFP 粮食援助
- **58,000+** 名叙利亚返回者和黎巴嫩入境者在边境口岸获得援助
- 黎巴嫩南部人道主义准入**受到严重限制**

这些数字来自大多数受影响平民永远不会读到的报告。

---

## 我们的工作

我们以三款产品弥合这一鸿沟：

### 📡 产品一：多语言人道主义信息机器人（Telegram）
**状态：已上线** ✅

一个 Telegram 机器人，以 **6 种语言** 每日发布人道主义简报：阿拉伯语、波斯语、达里语、英语、中文和土耳其语。

- 紧急电话号码
- 最新情况更新
- 捐款指引（向已建立的组织）
- 家庭寻亲资源

👉 **立即使用：** [@openclaw_aid_bot](https://t.me/openclaw_aid_bot)

### 🏠 产品二：实时庇护所查询（研发中）
**状态：开发中** 🔧

众包庇护所空位数据 → AI 聚合 → Telegram 即时查询。

- 参考：IOM DTM 数据 + 实地报告
- 需求：与黎巴嫩当地组织建立合作关系

### 🌐 产品三：人道主义数据翻译平台
**状态：运行中** ✅

自动化处理流程，可：
1. 扫描 ReliefWeb、OCHA 和 WHO 的最新报告
2. 提取关键信息
3. 翻译成波斯语、达里语和阿拉伯语简报（每篇不超过 200 词）
4. 当天在 Telegram 上发布

---

## 技术架构

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  数据来源         │     │  处理         │     │  分发            │
│                  │     │              │     │                 │
│  ReliefWeb  ─────┼────►│  Scout       │     │  Telegram Bot   │
│  OCHA       ─────┼────►│  （研究）     │────►│  (@openclaw_    │
│  WHO        ─────┼────►│      │       │     │   aid_bot)      │
│  UNHCR      ─────┘     │      ▼       │     │                 │
│                  │     │  Babel       │     │  【未来】        │
│                  │     │  （翻译）     │     │  Twitter/X      │
│                  │     │      │       │     │  WhatsApp       │
│                  │     │      ▼       │     │  广播            │
│                  │     │  Quill       │     └─────────────────┘
│                  │     │  （发布）     │
└──────────────────┘     └──────────────┘

语言：AR 🇱🇧 | FA 🇮🇷 | DAR 🇦🇫 | EN 🇬🇧 | ZH 🇨🇳 | TR 🇹🇷
```

**AI 智能体：**
- **Scout** — 研究并获取最新人道主义报告
- **Babel** — 使用场景感知的人道主义术语进行翻译
- **Quill** — 创建可发布的内容

---

## 快速开始

```bash
git clone https://github.com/CuiweiG/openclaw-humanitarian.git
cd openclaw-humanitarian
npm install
cp .env.example .env
# 在 .env 中配置环境变量
npm run dev
```

---

## 路线图

- [x] 支持 6 种语言的基础 Telegram 机器人
- [x] 自动化翻译流程
- [ ] 实时庇护所查询
- [ ] WhatsApp 集成
- [ ] LoRa 网状网络离线通信研究
- [ ] Web 控制面板

---

## 参与贡献

### 🌐 翻译者
- **优先：** 具有人道主义背景的达里语和波斯语母语者
- 欢迎阿拉伯语、土耳其语和普什图语翻译者
- 无最低参与要求——哪怕审阅一篇简报也有帮助

### 💻 开发者
- Telegram 机器人开发
- NLP 与翻译流程优化
- LoRa 网状网络 / 离线通信研究

完整说明请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 捐款

**我们不接受捐款。**

如果您希望在财务上提供帮助，请直接向已建立的人道主义组织捐款：

- 🔴 **ICRC（红十字国际委员会）** — [icrc.org/donate](https://www.icrc.org/en/donate)
- 🔵 **UNHCR（联合国难民署）** — [donate.unhcr.org](https://donate.unhcr.org)
- ⚪ **MSF / 无国界医生** — [msf.org/donate](https://www.msf.org/donate)

---

## 联系方式

- 📧 邮箱：aid@agentmail.to
- 🤖 Telegram 机器人：[@openclaw_aid_bot](https://t.me/openclaw_aid_bot)
- 🌐 网站：敬请期待

---

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

### 免责声明

- 本项目提供公开人道主义报告的**翻译摘要**
- 我们**不隶属于**任何联合国机构、政府或军事组织
- 翻译由 AI 辅助完成，可能存在不准确之处——对于重要决策，请务必参考原始来源

---

*以紧迫感构建，以用心维护。每一份简报都可能帮助某人找到安全。*
