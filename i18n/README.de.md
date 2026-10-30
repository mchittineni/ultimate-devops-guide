<div align="center">

# ⚙️ Leitfaden für Cloud, DevOps, Platform Engineering und SRE

**Interviewfragen, beantwortet in der Tiefe, die Interviewer tatsächlich erwarten.**

Rollenpfade: **DevOps** (Junior → Senior) · **DevSecOps** · **SecOps** · **SRE** · **SLO** · **SLA** · **AWS** · **Azure** · **GCP** · **Cloud** · **Platform Engineering**

Jede Antwort liefert eine Kurzantwort, die du laut sagen kannst, die Details und Abwägungen dahinter, ein lauffähiges Beispiel und die Rückfragen, mit denen du rechnen solltest.

<!-- LANGS:START -->

🌐 **In deiner Sprache lesen:** [English](../README.md) · [Español](./README.es.md) · [Français](./README.fr.md) · [Português](./README.pt.md) · **Deutsch** · [Italiano](./README.it.md) · [简体中文](./README.zh-CN.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [हिन्दी](./README.hi.md) · [العربية](./README.ar.md) · [Русский](./README.ru.md) · [Türkçe](./README.tr.md)

<!-- LANGS:END -->

[![Validate](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml)
[![Deploy Knowledge Graph](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml)

<!-- BADGES:START -->

![Questions](https://img.shields.io/badge/questions-787-blue)
![Topics](https://img.shields.io/badge/topics-40-blueviolet)
![Difficulty](https://img.shields.io/badge/difficulty-🟢%20177%20·%20🟡%20394%20·%20🔴%20216-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

<!-- BADGES:END -->

[🌐 3D-Wissensgraph](https://mchittineni.github.io/ultimate-devops-guide/) · [📖 Übersetzte Lektionen](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/de) · [📋 Vollständiger Fragenindex (Englisch)](../README.md#-all-questions) · [🤝 Mitwirken](../CONTRIBUTING.md)

⭐ Gib dem Projekt einen Stern, wenn es dir zur Stelle verhilft.

</div>

> [!NOTE]
> **Maßgeblich ist das Englische.** Diese Startseite ist von Hand übersetzt und im Repository eingecheckt. Die Lektionen werden auf dem Branch [`translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n) maschinell übersetzt: [auf Deutsch lesen](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/de). Weicht eine Übersetzung vom englischen Original ab, gilt das englische Original.

---

## 🌐 3D-Wissensgraph

Erkunde alle Fragen und Themen visuell: die Beziehungen zwischen ihnen, themenübergreifende Konzepte und Live-Filter nach Schwierigkeit, Bereich oder Stichwort.

👉 **[Interaktiven 3D-Wissensgraphen öffnen](https://mchittineni.github.io/ultimate-devops-guide/)**

---

## 🚀 Wähle deine Rolle

Dreizehn Pfade, jeder eine Lesereihenfolge statt eines Haufens Links. Beginne links und arbeite dich nach rechts vor.

> **Interview in zwei Wochen?** Beginne mit [Interview Experience](../interview-experience/README.md): Ablauf der Runden, wie du dein Projekt erklärst, wie du mit Szenariofragen umgehst, und eine Checkliste dessen, was tatsächlich gefragt wird.

| 🎯 Zielrolle                  | In dieser Reihenfolge lesen                                                                                                                                                                                                                                                                   |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Gerade in Interviews**      | [Interview Experience](../interview-experience/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Docker](../docker/README.md) → [Kubernetes](../kubernetes/README.md) → [IaC](../infrastructure-as-code/README.md)                 |
| **Junior / Associate DevOps** | [Core Concepts](../core-devops-concepts/README.md) → [Docker](../docker/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Scripting](../scripting-and-automation/README.md) → [CI/CD](../cicd/README.md)                           |
| **DevSecOps Engineer**        | [DevSecOps](../devsecops/README.md) → [Security & Compliance](../security-and-compliance/README.md) → [Network Security](../network-security/README.md) → [CI/CD](../cicd/README.md)                                                                                                          |
| **SecOps Engineer**           | [SecOps](../secops/README.md) → [Network Security](../network-security/README.md) → [Incident Management](../incident-management/README.md) → [Security & Compliance](../security-and-compliance/README.md)                                                                                   |
| **SRE Engineer**              | [SRE](../site-reliability-engineering/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Incident Management](../incident-management/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Metrics](../devops-metrics-and-kpis/README.md)          |
| **SLO Engineer**              | [SLO Engineering](../slo-engineering/README.md) → [SRE](../site-reliability-engineering/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Monitoring & Logging](../monitoring-and-logging/README.md)                                                        |
| **SLA Engineer**              | [SLA Management](../sla-management/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md) → [Backup & DR](../backup-and-disaster-recovery/README.md)                                                               |
| **AWS Engineer**              | [AWS Engineering](../aws-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Azure Engineer**            | [Azure Engineering](../azure-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                 |
| **GCP Engineer**              | [GCP Engineering](../gcp-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Cloud Engineer**            | [Cloud Engineering](../cloud-engineering/README.md) → [Cloud Platforms](../cloud-platforms/README.md) → [IaC](../infrastructure-as-code/README.md) → [Cloud Migration](../cloud-migration/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md)                     |
| **Platform Engineer**         | [Platform Engineering](../platform-engineering/README.md) → [Kubernetes](../kubernetes/README.md) → [Orchestration Advanced](../container-orchestration-advanced/README.md) → [Tools & Automation](../devops-tools-and-automation/README.md) → [Advanced](../advanced-devops-cloud/README.md) |
| **Senior / Lead**             | [Cloud Native](../cloud-native-architecture/README.md) → [Platform Engineering](../platform-engineering/README.md) → [Cost](../cloud-cost-optimization/README.md) → [Culture](../devops-culture-and-practices/README.md) → [Advanced](../advanced-devops-cloud/README.md)                     |

---

## 📚 Themen und Fragen durchsuchen

Der vollständige Index (jedes Thema mit seiner Fragenzahl und jede Frage nach Thema gruppiert) steht im [englischen README](../README.md#-all-questions). Maschinell übersetzte Fassungen jedes Themenindex und jeder Lektion liegen auf dem [Branch `translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/de).

---

## 🧠 So sind die Antworten aufgebaut

Jede Antwort folgt denselben vier Schritten, sodass du einen Abschnitt oder alle vier lesen kannst:

| Abschnitt                             | Was er dir bringt                                                                                             |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Kurzantwort** (_Short answer_)      | Zwei oder drei Sätze, die du laut sagen könntest. Fang hier an.                                               |
| **Details** (_Detail_)                | Die Substanz: Mechanismen, Abwägungen und das Vokabular, das Erfahrung signalisiert.                          |
| **Beispiel** (_Example_)              | Echte Befehle, YAML oder Code zum Ausführen und Anpassen.                                                     |
| **Interviewtipps** (_Interview tips_) | Die Rückfragen, die typischen Fallen und was eine starke Antwort von einer auswendig gelernten unterscheidet. |

Die Schwierigkeit ist markiert mit 🟢 Einsteiger · 🟡 Fortgeschritten · 🔴 Experte.

**Drei Arten, damit zu arbeiten:**

- **Vorbereitung auf eine bestimmte Rolle**: Folge dem Pfad aus der Tabelle oben und lies im README jedes Themas den Abschnitt „What interviewers probe here“ vor den Fragen.
- **Breite Wiederholung**: Lies die Kurzantworten eines Themas und geh nur dort in die Tiefe, wo du zögerst.
- **Obsidian / Notiz-Vault**: Jede Datei hat YAML-Frontmatter (`title`, `id`, `category`, `difficulty`, `tags`), sodass sich das ganze Repository als Vault öffnen und nach Tags durchsuchen lässt.

---

## 🌍 Zu den Übersetzungen

- **Diese Seite** ist von Hand übersetzt und wird wie jede andere Änderung geprüft. Korrekturen sind als Pull Request auf `i18n/README.de.md` willkommen.
- **Die Lektionen** werden bei jeder Änderung des englischen Inhalts von einem GitHub-Actions-Workflow maschinell übersetzt und auf dem Branch `translations` veröffentlicht. Code, Befehle und Konfiguration werden nie übersetzt.
- **Um eine Lektion zu korrigieren**, verbessere das englische Original: Die Übersetzung wird daraus neu erzeugt. Direkte Änderungen auf dem Branch `translations` werden überschrieben.
- **Deine Sprache fehlt?** [Eröffne ein Issue](https://github.com/mchittineni/ultimate-devops-guide/issues/new), um sie anzufragen.

---

## 🤝 Mitwirken

Neue Fragen, bessere Antworten und Korrekturen sind willkommen, auf Englisch, da Englisch die maßgebliche Quelle ist. [CONTRIBUTING.md](../CONTRIBUTING.md) beschreibt das Dateiformat, die Benennungsregeln und die lokalen Prüfungen vor einem Pull Request. Der [Verhaltenskodex](../CODE_OF_CONDUCT.md) und die [Sicherheitsrichtlinie](../SECURITY.md) legen die Grundregeln fest.

## 📄 Lizenz

Veröffentlicht unter der [MIT-Lizenz](../LICENSE).
