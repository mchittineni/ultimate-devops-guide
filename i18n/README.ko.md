<div align="center">

# ⚙️ 클라우드, DevOps, 플랫폼 엔지니어링, SRE 가이드

**면접관이 실제로 기대하는 깊이로 답한 면접 질문 모음.**

직무별 트랙: **DevOps** (주니어 → 시니어) · **DevSecOps** · **SecOps** · **SRE** · **SLO** · **SLA** · **AWS** · **Azure** · **GCP** · **Cloud** · **Platform Engineering**

모든 답변에는 소리 내어 말할 수 있는 짧은 답변, 그 뒤에 있는 세부 내용과 트레이드오프, 실행 가능한 예제, 그리고 예상되는 후속 질문이 담겨 있습니다.

<!-- LANGS:START -->

🌐 **당신의 언어로 읽기:** [English](../README.md) · [Español](./README.es.md) · [Français](./README.fr.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [Italiano](./README.it.md) · [简体中文](./README.zh-CN.md) · [日本語](./README.ja.md) · **한국어** · [हिन्दी](./README.hi.md) · [العربية](./README.ar.md) · [Русский](./README.ru.md) · [Türkçe](./README.tr.md)

<!-- LANGS:END -->

[![Validate](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml)
[![Deploy Knowledge Graph](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml)

<!-- BADGES:START -->

![Questions](https://img.shields.io/badge/questions-787-blue)
![Topics](https://img.shields.io/badge/topics-40-blueviolet)
![Difficulty](https://img.shields.io/badge/difficulty-🟢%20177%20·%20🟡%20394%20·%20🔴%20216-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

<!-- BADGES:END -->

[🌐 3D 지식 그래프](https://mchittineni.github.io/ultimate-devops-guide/) · [📖 번역된 레슨](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/ko) · [📋 전체 질문 색인(영어)](../README.md#-all-questions) · [🤝 기여하기](../CONTRIBUTING.md)

⭐ 원하는 직무를 얻는 데 도움이 되었다면 프로젝트에 스타를 눌러 주세요.

</div>

> [!NOTE]
> **영어판이 기준입니다.** 이 첫 페이지는 사람이 직접 번역해 저장소에 커밋했습니다. 레슨 페이지는 [`translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n) 브랜치에서 기계 번역됩니다: [한국어로 읽기](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/ko). 번역이 영어 원문과 다를 경우 영어 원문이 맞습니다.

---

## 🌐 3D 지식 그래프

모든 질문과 주제를 시각적으로 탐색하세요. 서로 간의 관계, 주제를 넘나드는 개념, 난이도·분야·키워드별 실시간 필터를 제공합니다.

👉 **[인터랙티브 3D 지식 그래프 열기](https://mchittineni.github.io/ultimate-devops-guide/)**

---

## 🚀 직무 선택

13개의 트랙이 있으며, 각 트랙은 링크 모음이 아니라 읽는 순서입니다. 왼쪽에서 시작해 오른쪽으로 진행하세요.

> **2주 뒤에 면접이 있나요?** [Interview Experience](../interview-experience/README.md)부터 시작하세요. 면접 라운드 구성, 프로젝트 설명 방법, 시나리오 질문 대응법, 실제로 자주 나오는 질문 체크리스트를 다룹니다.

| 🎯 목표 직무                     | 이 순서로 읽기                                                                                                                                                                                                                                                                                |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **지금 면접 중**                 | [Interview Experience](../interview-experience/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Docker](../docker/README.md) → [Kubernetes](../kubernetes/README.md) → [IaC](../infrastructure-as-code/README.md)                 |
| **주니어 / 어소시에이트 DevOps** | [Core Concepts](../core-devops-concepts/README.md) → [Docker](../docker/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Scripting](../scripting-and-automation/README.md) → [CI/CD](../cicd/README.md)                           |
| **DevSecOps 엔지니어**           | [DevSecOps](../devsecops/README.md) → [Security & Compliance](../security-and-compliance/README.md) → [Network Security](../network-security/README.md) → [CI/CD](../cicd/README.md)                                                                                                          |
| **SecOps 엔지니어**              | [SecOps](../secops/README.md) → [Network Security](../network-security/README.md) → [Incident Management](../incident-management/README.md) → [Security & Compliance](../security-and-compliance/README.md)                                                                                   |
| **SRE 엔지니어**                 | [SRE](../site-reliability-engineering/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Incident Management](../incident-management/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Metrics](../devops-metrics-and-kpis/README.md)          |
| **SLO 엔지니어**                 | [SLO Engineering](../slo-engineering/README.md) → [SRE](../site-reliability-engineering/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Monitoring & Logging](../monitoring-and-logging/README.md)                                                        |
| **SLA 엔지니어**                 | [SLA Management](../sla-management/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md) → [Backup & DR](../backup-and-disaster-recovery/README.md)                                                               |
| **AWS 엔지니어**                 | [AWS Engineering](../aws-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Azure 엔지니어**               | [Azure Engineering](../azure-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                 |
| **GCP 엔지니어**                 | [GCP Engineering](../gcp-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **클라우드 엔지니어**            | [Cloud Engineering](../cloud-engineering/README.md) → [Cloud Platforms](../cloud-platforms/README.md) → [IaC](../infrastructure-as-code/README.md) → [Cloud Migration](../cloud-migration/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md)                     |
| **플랫폼 엔지니어**              | [Platform Engineering](../platform-engineering/README.md) → [Kubernetes](../kubernetes/README.md) → [Orchestration Advanced](../container-orchestration-advanced/README.md) → [Tools & Automation](../devops-tools-and-automation/README.md) → [Advanced](../advanced-devops-cloud/README.md) |
| **시니어 / 리드**                | [Cloud Native](../cloud-native-architecture/README.md) → [Platform Engineering](../platform-engineering/README.md) → [Cost](../cloud-cost-optimization/README.md) → [Culture](../devops-culture-and-practices/README.md) → [Advanced](../advanced-devops-cloud/README.md)                     |

---

## 📚 주제와 질문 둘러보기

전체 색인(주제별 질문 수와 주제별로 묶은 모든 질문)은 [영어 README](../README.md#-all-questions)에 있습니다. 각 주제 색인과 레슨의 기계 번역본은 [`translations` 브랜치](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/ko)에 있습니다.

---

## 🧠 답변 구성

모든 답변은 같은 네 부분으로 구성되어 있어, 한 부분만 깊이 읽거나 네 부분을 모두 읽을 수 있습니다.

| 부분                           | 얻을 수 있는 것                                                       |
| ------------------------------ | --------------------------------------------------------------------- |
| **짧은 답변** (_Short answer_) | 소리 내어 말할 수 있는 두세 문장. 여기서 시작하세요.                  |
| **세부 내용** (_Detail_)       | 핵심: 동작 원리, 트레이드오프, 경험을 드러내는 용어.                  |
| **예제** (_Example_)           | 실행하고 응용할 수 있는 실제 명령어, YAML, 코드.                      |
| **면접 팁** (_Interview tips_) | 후속 질문, 흔한 함정, 그리고 외운 답변과 탄탄한 답변을 가르는 포인트. |

난이도는 🟢 초급 · 🟡 중급 · 🔴 고급으로 표시합니다.

**활용하는 세 가지 방법:**

- **특정 직무 준비**: 위 표의 트랙을 따라가고, 각 주제의 질문을 보기 전에 해당 README의 "What interviewers probe here"를 먼저 읽으세요.
- **폭넓은 복습**: 한 주제의 짧은 답변을 훑어보고, 망설여지는 부분만 깊이 파고드세요.
- **Obsidian / 노트 보관함**: 모든 파일에 YAML 프런트매터(`title`, `id`, `category`, `difficulty`, `tags`)가 있어 저장소 전체를 보관함으로 열고 태그로 탐색할 수 있습니다.

---

## 🌍 번역 안내

- **이 페이지**는 사람이 직접 번역했으며 다른 변경 사항과 마찬가지로 리뷰를 거칩니다. 수정 사항은 `i18n/README.ko.md`에 대한 pull request로 보내 주세요.
- **레슨 페이지**는 영어 콘텐츠가 바뀔 때마다 GitHub Actions 워크플로가 기계 번역해 `translations` 브랜치에 게시합니다. 코드, 명령어, 설정은 번역하지 않습니다.
- **레슨을 고치려면** 영어 원문을 개선하세요. 번역은 원문에서 자동으로 다시 생성됩니다. `translations` 브랜치를 직접 수정하면 덮어써집니다.
- **원하는 언어가 없나요?** [이슈를 열어](https://github.com/mchittineni/ultimate-devops-guide/issues/new) 요청해 주세요.

---

## 🤝 기여하기

새 질문, 더 나은 답변, 수정 모두 환영합니다. 영어가 기준 소스이므로 영어로 작성해 주세요. [CONTRIBUTING.md](../CONTRIBUTING.md)에 파일 형식, 이름 규칙, pull request 전에 로컬에서 실행할 검사가 정리되어 있습니다. [행동 강령](../CODE_OF_CONDUCT.md)과 [보안 정책](../SECURITY.md)이 기본 규칙입니다.

## 📄 라이선스

[MIT 라이선스](../LICENSE)로 배포됩니다.
