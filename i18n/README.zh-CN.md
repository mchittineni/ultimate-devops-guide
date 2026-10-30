<div align="center">

# ⚙️ 云计算、DevOps、平台工程与 SRE 指南

**面试题的解答深度，正是面试官真正期望的深度。**

岗位路线: **DevOps** （初级 → 高级） · **DevSecOps** · **SecOps** · **SRE** · **SLO** · **SLA** · **AWS** · **Azure** · **GCP** · **Cloud** · **Platform Engineering**

每道题都提供：一段可以直接说出口的简短回答、背后的细节与权衡、一个可运行的示例，以及面试官可能追问的问题。

<!-- LANGS:START -->

🌐 **用你的语言阅读:** [English](../README.md) · [Español](./README.es.md) · [Français](./README.fr.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [Italiano](./README.it.md) · **简体中文** · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [हिन्दी](./README.hi.md) · [العربية](./README.ar.md) · [Русский](./README.ru.md) · [Türkçe](./README.tr.md)

<!-- LANGS:END -->

[![Validate](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml)
[![Deploy Knowledge Graph](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml)

<!-- BADGES:START -->

![Questions](https://img.shields.io/badge/questions-787-blue)
![Topics](https://img.shields.io/badge/topics-40-blueviolet)
![Difficulty](https://img.shields.io/badge/difficulty-🟢%20177%20·%20🟡%20394%20·%20🔴%20216-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

<!-- BADGES:END -->

[🌐 3D 知识图谱](https://mchittineni.github.io/ultimate-devops-guide/) · [📖 已翻译的课程](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/zh-CN) · [📋 完整题目索引（英文）](../README.md#-all-questions) · [🤝 参与贡献](../CONTRIBUTING.md)

⭐ 如果这个项目帮你拿到了心仪的岗位，请给它点个 Star。

</div>

> [!NOTE]
> **以英文版为准。** 本首页为人工翻译并提交在仓库中。课程页面在 [`translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n) 分支上由机器自动翻译：[阅读简体中文版](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/zh-CN)。如果译文与英文原文不一致，请以英文原文为准。

---

## 🌐 3D 知识图谱

以可视化方式浏览所有题目和主题：它们之间的关联、跨主题的概念，并可按难度、领域或关键词实时筛选。

👉 **[打开交互式 3D 知识图谱](https://mchittineni.github.io/ultimate-devops-guide/)**

---

## 🚀 选择你的岗位

十三条路线，每条都是一个阅读顺序，而不是一堆链接。从左往右依次阅读。

> **两周后就要面试？** 先读 [Interview Experience](../interview-experience/README.md)：它涵盖面试轮次结构、如何讲清你的项目、如何应对场景题，以及一份真实高频问题清单。

| 🎯 目标岗位            | 阅读顺序                                                                                                                                                                                                                                                                                      |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **正在面试**           | [Interview Experience](../interview-experience/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Docker](../docker/README.md) → [Kubernetes](../kubernetes/README.md) → [IaC](../infrastructure-as-code/README.md)                 |
| **初级 / 助理 DevOps** | [Core Concepts](../core-devops-concepts/README.md) → [Docker](../docker/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Scripting](../scripting-and-automation/README.md) → [CI/CD](../cicd/README.md)                           |
| **DevSecOps 工程师**   | [DevSecOps](../devsecops/README.md) → [Security & Compliance](../security-and-compliance/README.md) → [Network Security](../network-security/README.md) → [CI/CD](../cicd/README.md)                                                                                                          |
| **SecOps 工程师**      | [SecOps](../secops/README.md) → [Network Security](../network-security/README.md) → [Incident Management](../incident-management/README.md) → [Security & Compliance](../security-and-compliance/README.md)                                                                                   |
| **SRE 工程师**         | [SRE](../site-reliability-engineering/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Incident Management](../incident-management/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Metrics](../devops-metrics-and-kpis/README.md)          |
| **SLO 工程师**         | [SLO Engineering](../slo-engineering/README.md) → [SRE](../site-reliability-engineering/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Monitoring & Logging](../monitoring-and-logging/README.md)                                                        |
| **SLA 工程师**         | [SLA Management](../sla-management/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md) → [Backup & DR](../backup-and-disaster-recovery/README.md)                                                               |
| **AWS 工程师**         | [AWS Engineering](../aws-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Azure 工程师**       | [Azure Engineering](../azure-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                 |
| **GCP 工程师**         | [GCP Engineering](../gcp-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **云工程师**           | [Cloud Engineering](../cloud-engineering/README.md) → [Cloud Platforms](../cloud-platforms/README.md) → [IaC](../infrastructure-as-code/README.md) → [Cloud Migration](../cloud-migration/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md)                     |
| **平台工程师**         | [Platform Engineering](../platform-engineering/README.md) → [Kubernetes](../kubernetes/README.md) → [Orchestration Advanced](../container-orchestration-advanced/README.md) → [Tools & Automation](../devops-tools-and-automation/README.md) → [Advanced](../advanced-devops-cloud/README.md) |
| **高级 / 技术负责人**  | [Cloud Native](../cloud-native-architecture/README.md) → [Platform Engineering](../platform-engineering/README.md) → [Cost](../cloud-cost-optimization/README.md) → [Culture](../devops-culture-and-practices/README.md) → [Advanced](../advanced-devops-cloud/README.md)                     |

---

## 📚 浏览主题与题目

完整索引（每个主题的题目数量，以及按主题分组的全部题目）位于 [英文 README](../README.md#-all-questions)。每个主题索引和每节课程的机器翻译版本位于 [`translations` 分支](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/zh-CN)。

---

## 🧠 答案的结构

每个答案都遵循相同的四个部分，你可以只深入读一部分，也可以四部分全读：

| 部分                            | 提供的内容                                               |
| ------------------------------- | -------------------------------------------------------- |
| **简短回答** (_Short answer_)   | 两三句可以直接说出口的话。从这里开始。                   |
| **详细说明** (_Detail_)         | 核心内容：机制、权衡，以及体现经验的专业术语。           |
| **示例** (_Example_)            | 可运行、可改编的真实命令、YAML 或代码。                  |
| **面试技巧** (_Interview tips_) | 可能的追问、常见陷阱，以及区分扎实回答与死记硬背的要点。 |

难度标记：🟢 入门 · 🟡 中级 · 🔴 高级。

**三种使用方式：**

- **为特定岗位做准备**：按上表中的路线阅读，并在看每个主题的题目之前先读其 README 中的 “What interviewers probe here” 部分。
- **全面复习**：先通读一个主题下的简短回答，只在不确定的地方深入阅读。
- **Obsidian / 笔记库**：每个文件都带有 YAML frontmatter（`title`、`id`、`category`、`difficulty`、`tags`），因此整个仓库可以直接作为笔记库打开，并按标签浏览。

---

## 🌍 关于翻译

- **本页面** 为人工翻译，并像其他改动一样经过审阅。欢迎通过 pull request 修改 `i18n/README.zh-CN.md` 来提交更正。
- **课程页面** 在英文内容每次变更时由 GitHub Actions 工作流自动机器翻译，并发布到 `translations` 分支。代码、命令和配置永远不会被翻译。
- **要修正某节课程**，请改进英文原文：译文会据此自动重新生成。直接在 `translations` 分支上做的修改会被覆盖。
- **没有你的语言？** [提交 issue](https://github.com/mchittineni/ultimate-devops-guide/issues/new) 提出需求。

---

## 🤝 参与贡献

欢迎提交新题目、更好的答案和更正，请使用英文，因为英文是权威来源。[CONTRIBUTING.md](../CONTRIBUTING.md) 介绍了文件格式、命名规则以及提交 pull request 前需要在本地运行的检查。[行为准则](../CODE_OF_CONDUCT.md) 和 [安全策略](../SECURITY.md) 规定了基本规则。

## 📄 许可证

以 [MIT 许可证](../LICENSE) 发布。
