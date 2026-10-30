<div align="center">

# ⚙️ Guida a Cloud, DevOps, Platform Engineering e SRE

**Domande da colloquio con risposte alla profondità che un selezionatore si aspetta davvero.**

Percorsi per ruolo: **DevOps** (junior → senior) · **DevSecOps** · **SecOps** · **SRE** · **SLO** · **SLA** · **AWS** · **Azure** · **GCP** · **Cloud** · **Platform Engineering**

Ogni risposta ti dà una risposta breve da dire ad alta voce, i dettagli e i compromessi che ci sono dietro, un esempio eseguibile e le domande di approfondimento da aspettarsi.

<!-- LANGS:START -->

🌐 **Leggi nella tua lingua:** [English](../README.md) · [Español](./README.es.md) · [Français](./README.fr.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · **Italiano** · [简体中文](./README.zh-CN.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [हिन्दी](./README.hi.md) · [العربية](./README.ar.md) · [Русский](./README.ru.md) · [Türkçe](./README.tr.md)

<!-- LANGS:END -->

[![Validate](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml)
[![Deploy Knowledge Graph](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml)

<!-- BADGES:START -->

![Questions](https://img.shields.io/badge/questions-787-blue)
![Topics](https://img.shields.io/badge/topics-40-blueviolet)
![Difficulty](https://img.shields.io/badge/difficulty-🟢%20177%20·%20🟡%20394%20·%20🔴%20216-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

<!-- BADGES:END -->

[🌐 Grafo della conoscenza 3D](https://mchittineni.github.io/ultimate-devops-guide/) · [📖 Lezioni tradotte](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/it) · [📋 Indice completo delle domande (inglese)](../README.md#-all-questions) · [🤝 Contribuire](../CONTRIBUTING.md)

⭐ Metti una stella al progetto se ti aiuta a ottenere il ruolo.

</div>

> [!NOTE]
> **Fa fede l'inglese.** Questa pagina iniziale è tradotta a mano e salvata nel repository. Le lezioni sono tradotte automaticamente sul branch [`translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n): [leggile in italiano](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/it). Se una traduzione non corrisponde all'originale inglese, ha ragione l'originale inglese.

---

## 🌐 Grafo della conoscenza 3D

Esplora visivamente tutte le domande e tutti gli argomenti: le relazioni tra loro, i concetti trasversali e filtri in tempo reale per difficoltà, area o parola chiave.

👉 **[Apri il grafo della conoscenza 3D interattivo](https://mchittineni.github.io/ultimate-devops-guide/)**

---

## 🚀 Scegli il tuo ruolo

Tredici percorsi, ognuno un ordine di lettura e non un mucchio di link. Parti da sinistra e prosegui verso destra.

> **Colloquio tra due settimane?** Inizia da [Interview Experience](../interview-experience/README.md): struttura dei round, come spiegare il tuo progetto, come affrontare le domande di scenario e una checklist di ciò che viene chiesto davvero.

| 🎯 Ruolo obiettivo            | Leggi in quest'ordine                                                                                                                                                                                                                                                                         |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **In colloquio adesso**       | [Interview Experience](../interview-experience/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Docker](../docker/README.md) → [Kubernetes](../kubernetes/README.md) → [IaC](../infrastructure-as-code/README.md)                 |
| **DevOps junior / associate** | [Core Concepts](../core-devops-concepts/README.md) → [Docker](../docker/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Scripting](../scripting-and-automation/README.md) → [CI/CD](../cicd/README.md)                           |
| **Ingegnere DevSecOps**       | [DevSecOps](../devsecops/README.md) → [Security & Compliance](../security-and-compliance/README.md) → [Network Security](../network-security/README.md) → [CI/CD](../cicd/README.md)                                                                                                          |
| **Ingegnere SecOps**          | [SecOps](../secops/README.md) → [Network Security](../network-security/README.md) → [Incident Management](../incident-management/README.md) → [Security & Compliance](../security-and-compliance/README.md)                                                                                   |
| **Ingegnere SRE**             | [SRE](../site-reliability-engineering/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Incident Management](../incident-management/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Metrics](../devops-metrics-and-kpis/README.md)          |
| **Ingegnere SLO**             | [SLO Engineering](../slo-engineering/README.md) → [SRE](../site-reliability-engineering/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Monitoring & Logging](../monitoring-and-logging/README.md)                                                        |
| **Ingegnere SLA**             | [SLA Management](../sla-management/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md) → [Backup & DR](../backup-and-disaster-recovery/README.md)                                                               |
| **Ingegnere AWS**             | [AWS Engineering](../aws-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Ingegnere Azure**           | [Azure Engineering](../azure-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                 |
| **Ingegnere GCP**             | [GCP Engineering](../gcp-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Ingegnere cloud**           | [Cloud Engineering](../cloud-engineering/README.md) → [Cloud Platforms](../cloud-platforms/README.md) → [IaC](../infrastructure-as-code/README.md) → [Cloud Migration](../cloud-migration/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md)                     |
| **Ingegnere di piattaforma**  | [Platform Engineering](../platform-engineering/README.md) → [Kubernetes](../kubernetes/README.md) → [Orchestration Advanced](../container-orchestration-advanced/README.md) → [Tools & Automation](../devops-tools-and-automation/README.md) → [Advanced](../advanced-devops-cloud/README.md) |
| **Senior / lead**             | [Cloud Native](../cloud-native-architecture/README.md) → [Platform Engineering](../platform-engineering/README.md) → [Cost](../cloud-cost-optimization/README.md) → [Culture](../devops-culture-and-practices/README.md) → [Advanced](../advanced-devops-cloud/README.md)                     |

---

## 📚 Sfoglia argomenti e domande

L'indice completo (ogni argomento con il numero di domande e ogni domanda raggruppata per argomento) si trova nel [README in inglese](../README.md#-all-questions). Le versioni tradotte automaticamente di ogni indice e di ogni lezione sono sul [branch `translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/it).

---

## 🧠 Come sono strutturate le risposte

Ogni risposta segue gli stessi quattro passaggi, così puoi leggere una sezione a fondo oppure tutte e quattro:

| Sezione                                          | Cosa ti offre                                                                                                        |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| **Risposta breve** (_Short answer_)              | Due o tre frasi da dire ad alta voce. Inizia da qui.                                                                 |
| **Dettaglio** (_Detail_)                         | La sostanza: meccanismi, compromessi e il lessico che segnala esperienza.                                            |
| **Esempio** (_Example_)                          | Comandi, YAML o codice reali da eseguire e adattare.                                                                 |
| **Consigli per il colloquio** (_Interview tips_) | Le domande di approfondimento, le trappole comuni e ciò che distingue una risposta solida da una imparata a memoria. |

La difficoltà è indicata con 🟢 Base · 🟡 Intermedio · 🔴 Avanzato.

**Tre modi per usarla:**

- **Prepararsi a un ruolo specifico**: segui il percorso della tabella qui sopra e leggi la parte "What interviewers probe here" del README di ogni argomento prima delle domande.
- **Ripasso generale**: leggi le risposte brevi di un argomento e approfondisci solo dove esiti.
- **Obsidian / vault di note**: ogni file ha un frontmatter YAML (`title`, `id`, `category`, `difficulty`, `tags`), quindi l'intero repository può essere aperto come vault e consultato per tag.

---

## 🌍 Sulle traduzioni

- **Questa pagina** è tradotta a mano e rivista come qualsiasi altra modifica. Le correzioni sono benvenute come pull request su `i18n/README.it.md`.
- **Le lezioni** sono tradotte automaticamente da un workflow GitHub Actions ogni volta che cambia il contenuto in inglese e pubblicate sul branch `translations`. Codice, comandi e configurazione non vengono mai tradotti.
- **Per correggere una lezione**, migliora l'originale inglese: la traduzione viene rigenerata a partire da esso. Le modifiche fatte direttamente sul branch `translations` vengono sovrascritte.
- **Manca la tua lingua?** [Apri una issue](https://github.com/mchittineni/ultimate-devops-guide/issues/new) per richiederla.

---

## 🤝 Contribuire

Nuove domande, risposte migliori e correzioni sono benvenute, in inglese, perché l'inglese è la fonte di riferimento. [CONTRIBUTING.md](../CONTRIBUTING.md) descrive il formato dei file, le regole di denominazione e i controlli locali da eseguire prima di aprire una pull request. Il [Codice di condotta](../CODE_OF_CONDUCT.md) e la [Politica di sicurezza](../SECURITY.md) stabiliscono le regole di base.

## 📄 Licenza

Rilasciato con [licenza MIT](../LICENSE).
