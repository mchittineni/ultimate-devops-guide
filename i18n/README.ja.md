<div align="center">

# ⚙️ クラウド・DevOps・プラットフォームエンジニアリング・SRE ガイド

**面接官が本当に期待する深さで答えた面接質問集。**

職種別トラック: **DevOps** （ジュニア → シニア） · **DevSecOps** · **SecOps** · **SRE** · **SLO** · **SLA** · **AWS** · **Azure** · **GCP** · **Cloud** · **Platform Engineering**

すべての回答に、そのまま口に出せる短い回答、その背景にある詳細とトレードオフ、実行できる例、そして想定される追加質問が含まれています。

<!-- LANGS:START -->

🌐 **あなたの言語で読む:** [English](../README.md) · [Español](./README.es.md) · [Français](./README.fr.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [Italiano](./README.it.md) · [简体中文](./README.zh-CN.md) · **日本語** · [한국어](./README.ko.md) · [हिन्दी](./README.hi.md) · [العربية](./README.ar.md) · [Русский](./README.ru.md) · [Türkçe](./README.tr.md)

<!-- LANGS:END -->

[![Validate](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml)
[![Deploy Knowledge Graph](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml)

<!-- BADGES:START -->

![Questions](https://img.shields.io/badge/questions-787-blue)
![Topics](https://img.shields.io/badge/topics-40-blueviolet)
![Difficulty](https://img.shields.io/badge/difficulty-🟢%20177%20·%20🟡%20394%20·%20🔴%20216-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

<!-- BADGES:END -->

[🌐 3D ナレッジグラフ](https://mchittineni.github.io/ultimate-devops-guide/) · [📖 翻訳済みレッスン](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/ja) · [📋 全質問インデックス（英語）](../README.md#-all-questions) · [🤝 コントリビュート](../CONTRIBUTING.md)

⭐ 希望の職に就く助けになったら、ぜひスターをお願いします。

</div>

> [!NOTE]
> **正式版は英語です。** このトップページは人手で翻訳し、リポジトリにコミットしています。レッスンページは [`translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n) ブランチで機械翻訳されています：[日本語で読む](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/ja)。翻訳と英語の原文が食い違う場合は、英語の原文が正しい内容です。

---

## 🌐 3D ナレッジグラフ

すべての質問とトピックを視覚的に探索できます。相互の関係、トピックをまたぐ概念、難易度・分野・キーワードによるリアルタイムの絞り込みに対応しています。

👉 **[インタラクティブな 3D ナレッジグラフを開く](https://mchittineni.github.io/ultimate-devops-guide/)**

---

## 🚀 職種を選ぶ

13 のトラックがあり、それぞれがリンクの寄せ集めではなく読む順番を示しています。左から右へ順に進めてください。

> **面接まであと 2 週間？** まずは [Interview Experience](../interview-experience/README.md) から。面接ラウンドの構成、自分のプロジェクトの説明の仕方、シナリオ質問への対応、実際によく聞かれる内容のチェックリストをまとめています。

| 🎯 目標の職種                      | この順番で読む                                                                                                                                                                                                                                                                                |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **面接中の方**                     | [Interview Experience](../interview-experience/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Docker](../docker/README.md) → [Kubernetes](../kubernetes/README.md) → [IaC](../infrastructure-as-code/README.md)                 |
| **ジュニア / アソシエイト DevOps** | [Core Concepts](../core-devops-concepts/README.md) → [Docker](../docker/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Scripting](../scripting-and-automation/README.md) → [CI/CD](../cicd/README.md)                           |
| **DevSecOps エンジニア**           | [DevSecOps](../devsecops/README.md) → [Security & Compliance](../security-and-compliance/README.md) → [Network Security](../network-security/README.md) → [CI/CD](../cicd/README.md)                                                                                                          |
| **SecOps エンジニア**              | [SecOps](../secops/README.md) → [Network Security](../network-security/README.md) → [Incident Management](../incident-management/README.md) → [Security & Compliance](../security-and-compliance/README.md)                                                                                   |
| **SRE エンジニア**                 | [SRE](../site-reliability-engineering/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Incident Management](../incident-management/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Metrics](../devops-metrics-and-kpis/README.md)          |
| **SLO エンジニア**                 | [SLO Engineering](../slo-engineering/README.md) → [SRE](../site-reliability-engineering/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Monitoring & Logging](../monitoring-and-logging/README.md)                                                        |
| **SLA エンジニア**                 | [SLA Management](../sla-management/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md) → [Backup & DR](../backup-and-disaster-recovery/README.md)                                                               |
| **AWS エンジニア**                 | [AWS Engineering](../aws-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Azure エンジニア**               | [Azure Engineering](../azure-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                 |
| **GCP エンジニア**                 | [GCP Engineering](../gcp-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **クラウドエンジニア**             | [Cloud Engineering](../cloud-engineering/README.md) → [Cloud Platforms](../cloud-platforms/README.md) → [IaC](../infrastructure-as-code/README.md) → [Cloud Migration](../cloud-migration/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md)                     |
| **プラットフォームエンジニア**     | [Platform Engineering](../platform-engineering/README.md) → [Kubernetes](../kubernetes/README.md) → [Orchestration Advanced](../container-orchestration-advanced/README.md) → [Tools & Automation](../devops-tools-and-automation/README.md) → [Advanced](../advanced-devops-cloud/README.md) |
| **シニア / リード**                | [Cloud Native](../cloud-native-architecture/README.md) → [Platform Engineering](../platform-engineering/README.md) → [Cost](../cloud-cost-optimization/README.md) → [Culture](../devops-culture-and-practices/README.md) → [Advanced](../advanced-devops-cloud/README.md)                     |

---

## 📚 トピックと質問を探す

完全なインデックス（各トピックの質問数と、トピックごとにまとめた全質問）は [英語の README](../README.md#-all-questions) にあります。各トピックのインデックスとレッスンの機械翻訳版は [`translations` ブランチ](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/ja) にあります。

---

## 🧠 回答の構成

すべての回答は同じ 4 つのパートで構成されているので、1 つのパートを深く読むことも、4 つすべてを読むこともできます。

| パート                            | 得られるもの                                                                       |
| --------------------------------- | ---------------------------------------------------------------------------------- |
| **短い回答** (_Short answer_)     | そのまま口に出せる 2〜3 文。まずはここから。                                       |
| **詳細** (_Detail_)               | 本質部分：仕組み、トレードオフ、経験を感じさせる用語。                             |
| **例** (_Example_)                | 実行して応用できる実際のコマンド、YAML、コード。                                   |
| **面接のコツ** (_Interview tips_) | 追加質問、よくある落とし穴、そして暗記した回答と説得力のある回答を分けるポイント。 |

難易度は 🟢 初級 · 🟡 中級 · 🔴 上級 で表示しています。

**3 つの使い方：**

- **特定の職種に向けて準備する**：上の表のトラックに沿って読み、各トピックの質問に入る前に、その README の「What interviewers probe here」を読んでください。
- **幅広く復習する**：トピック内の短い回答を通読し、自信がないところだけ深掘りします。
- **Obsidian / ノート保管庫**：各ファイルには YAML フロントマター（`title`、`id`、`category`、`difficulty`、`tags`）が付いているので、リポジトリ全体を保管庫として開き、タグで閲覧できます。

---

## 🌍 翻訳について

- **このページ** は人手で翻訳し、ほかの変更と同じようにレビューしています。修正は `i18n/README.ja.md` への pull request で歓迎します。
- **レッスンページ** は英語のコンテンツが変更されるたびに GitHub Actions のワークフローで機械翻訳され、`translations` ブランチに公開されます。コード、コマンド、設定は翻訳しません。
- **レッスンを修正したい場合** は英語の原文を改善してください。翻訳はそこから自動的に再生成されます。`translations` ブランチを直接編集しても上書きされます。
- **あなたの言語がない？** [issue を作成](https://github.com/mchittineni/ultimate-devops-guide/issues/new) してリクエストしてください。

---

## 🤝 コントリビュート

新しい質問、より良い回答、修正を歓迎します。英語が正式なソースなので、英語で投稿してください。[CONTRIBUTING.md](../CONTRIBUTING.md) にファイル形式、命名規則、pull request 前にローカルで実行するチェックをまとめています。[行動規範](../CODE_OF_CONDUCT.md) と [セキュリティポリシー](../SECURITY.md) が基本ルールです。

## 📄 ライセンス

[MIT ライセンス](../LICENSE) の下で公開しています。
