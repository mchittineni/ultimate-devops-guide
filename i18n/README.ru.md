<div align="center">

# ⚙️ Руководство по Cloud, DevOps, Platform Engineering и SRE

**Вопросы с собеседований с ответами той глубины, которую действительно ждёт интервьюер.**

Треки по ролям: **DevOps** (junior → senior) · **DevSecOps** · **SecOps** · **SRE** · **SLO** · **SLA** · **AWS** · **Azure** · **GCP** · **Cloud** · **Platform Engineering**

Каждый ответ содержит короткий ответ, который можно произнести вслух, подробности и компромиссы за ним, рабочий пример и уточняющие вопросы, которых стоит ждать.

<!-- LANGS:START -->

🌐 **Читать на вашем языке:** [English](../README.md) · [Español](./README.es.md) · [Français](./README.fr.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [Italiano](./README.it.md) · [简体中文](./README.zh-CN.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [हिन्दी](./README.hi.md) · [العربية](./README.ar.md) · **Русский** · [Türkçe](./README.tr.md)

<!-- LANGS:END -->

[![Validate](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml)
[![Deploy Knowledge Graph](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml)

<!-- BADGES:START -->

![Questions](https://img.shields.io/badge/questions-787-blue)
![Topics](https://img.shields.io/badge/topics-40-blueviolet)
![Difficulty](https://img.shields.io/badge/difficulty-🟢%20177%20·%20🟡%20394%20·%20🔴%20216-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

<!-- BADGES:END -->

[🌐 3D-граф знаний](https://mchittineni.github.io/ultimate-devops-guide/) · [📖 Переведённые уроки](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/ru) · [📋 Полный список вопросов (на английском)](../README.md#-all-questions) · [🤝 Как помочь проекту](../CONTRIBUTING.md)

⭐ Поставьте звезду проекту, если он помог вам получить работу.

</div>

> [!NOTE]
> **Эталоном служит английская версия.** Эта главная страница переведена вручную и хранится в репозитории. Уроки переводятся автоматически в ветке [`translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n): [читать на русском](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/ru). Если перевод расходится с английским оригиналом, прав английский оригинал.

---

## 🌐 3D-граф знаний

Исследуйте все вопросы и темы визуально: связи между ними, сквозные понятия и живые фильтры по сложности, области или ключевому слову.

👉 **[Открыть интерактивный 3D-граф знаний](https://mchittineni.github.io/ultimate-devops-guide/)**

---

## 🚀 Выберите свою роль

Тринадцать треков, и каждый из них — порядок чтения, а не куча ссылок. Начните слева и двигайтесь вправо.

> **Собеседование через две недели?** Начните с [Interview Experience](../interview-experience/README.md): структура этапов, как рассказать о своём проекте, как отвечать на сценарные вопросы, и чек-лист того, о чём спрашивают на самом деле.

| 🎯 Целевая роль                  | Читайте в этом порядке                                                                                                                                                                                                                                                                        |
| -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Прохожу собеседования сейчас** | [Interview Experience](../interview-experience/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Docker](../docker/README.md) → [Kubernetes](../kubernetes/README.md) → [IaC](../infrastructure-as-code/README.md)                 |
| **Junior / Associate DevOps**    | [Core Concepts](../core-devops-concepts/README.md) → [Docker](../docker/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Scripting](../scripting-and-automation/README.md) → [CI/CD](../cicd/README.md)                           |
| **DevSecOps-инженер**            | [DevSecOps](../devsecops/README.md) → [Security & Compliance](../security-and-compliance/README.md) → [Network Security](../network-security/README.md) → [CI/CD](../cicd/README.md)                                                                                                          |
| **SecOps-инженер**               | [SecOps](../secops/README.md) → [Network Security](../network-security/README.md) → [Incident Management](../incident-management/README.md) → [Security & Compliance](../security-and-compliance/README.md)                                                                                   |
| **SRE-инженер**                  | [SRE](../site-reliability-engineering/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Incident Management](../incident-management/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Metrics](../devops-metrics-and-kpis/README.md)          |
| **SLO-инженер**                  | [SLO Engineering](../slo-engineering/README.md) → [SRE](../site-reliability-engineering/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Monitoring & Logging](../monitoring-and-logging/README.md)                                                        |
| **SLA-инженер**                  | [SLA Management](../sla-management/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md) → [Backup & DR](../backup-and-disaster-recovery/README.md)                                                               |
| **AWS-инженер**                  | [AWS Engineering](../aws-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Azure-инженер**                | [Azure Engineering](../azure-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                 |
| **GCP-инженер**                  | [GCP Engineering](../gcp-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Облачный инженер**             | [Cloud Engineering](../cloud-engineering/README.md) → [Cloud Platforms](../cloud-platforms/README.md) → [IaC](../infrastructure-as-code/README.md) → [Cloud Migration](../cloud-migration/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md)                     |
| **Платформенный инженер**        | [Platform Engineering](../platform-engineering/README.md) → [Kubernetes](../kubernetes/README.md) → [Orchestration Advanced](../container-orchestration-advanced/README.md) → [Tools & Automation](../devops-tools-and-automation/README.md) → [Advanced](../advanced-devops-cloud/README.md) |
| **Senior / Lead**                | [Cloud Native](../cloud-native-architecture/README.md) → [Platform Engineering](../platform-engineering/README.md) → [Cost](../cloud-cost-optimization/README.md) → [Culture](../devops-culture-and-practices/README.md) → [Advanced](../advanced-devops-cloud/README.md)                     |

---

## 📚 Темы и вопросы

Полный указатель (каждая тема с числом вопросов и все вопросы, сгруппированные по темам) находится в [английском README](../README.md#-all-questions). Машинные переводы указателей тем и уроков лежат в [ветке `translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/ru).

---

## 🧠 Как устроены ответы

Каждый ответ состоит из одних и тех же четырёх частей, поэтому можно прочитать одну часть глубоко или все четыре:

| Часть                                           | Что она даёт                                                                         |
| ----------------------------------------------- | ------------------------------------------------------------------------------------ |
| **Короткий ответ** (_Short answer_)             | Два-три предложения, которые можно сказать вслух. Начните отсюда.                    |
| **Подробности** (_Detail_)                      | Суть: механизмы, компромиссы и терминология, по которой видно опыт.                  |
| **Пример** (_Example_)                          | Реальные команды, YAML или код, которые можно запустить и адаптировать.              |
| **Советы для собеседования** (_Interview tips_) | Уточняющие вопросы, типичные ловушки и то, что отличает сильный ответ от заученного. |

Сложность обозначена так: 🟢 Начальный · 🟡 Средний · 🔴 Продвинутый.

**Три способа работать с материалом:**

- **Подготовка к конкретной роли**: идите по треку из таблицы выше и перед вопросами каждой темы читайте в её README раздел «What interviewers probe here».
- **Общее повторение**: прочитайте короткие ответы по теме и углубляйтесь только там, где сомневаетесь.
- **Obsidian / хранилище заметок**: у каждого файла есть YAML-фронтматтер (`title`, `id`, `category`, `difficulty`, `tags`), поэтому весь репозиторий можно открыть как хранилище и просматривать по тегам.

---

## 🌍 О переводах

- **Эта страница** переведена вручную и проходит ревью, как любое другое изменение. Исправления приветствуются в виде pull request к `i18n/README.ru.md`.
- **Уроки** автоматически переводятся workflow в GitHub Actions при каждом изменении английского текста и публикуются в ветке `translations`. Код, команды и конфигурация никогда не переводятся.
- **Чтобы исправить урок**, улучшите английский оригинал: перевод пересоздаётся из него автоматически. Правки, сделанные прямо в ветке `translations`, будут перезаписаны.
- **Нет вашего языка?** [Создайте issue](https://github.com/mchittineni/ultimate-devops-guide/issues/new), чтобы запросить его.

---

## 🤝 Как помочь проекту

Новые вопросы, более точные ответы и исправления приветствуются — на английском, поскольку английский является эталонным источником. В [CONTRIBUTING.md](../CONTRIBUTING.md) описаны формат файлов, правила именования и локальные проверки перед открытием pull request. [Кодекс поведения](../CODE_OF_CONDUCT.md) и [Политика безопасности](../SECURITY.md) задают основные правила.

## 📄 Лицензия

Распространяется по [лицензии MIT](../LICENSE).
