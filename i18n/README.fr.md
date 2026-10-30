<div align="center">

# ⚙️ Guide Cloud, DevOps, Platform Engineering et SRE

**Des questions d'entretien traitées avec la profondeur qu'un recruteur attend vraiment.**

Parcours par rôle: **DevOps** (junior → senior) · **DevSecOps** · **SecOps** · **SRE** · **SLO** · **SLA** · **AWS** · **Azure** · **GCP** · **Cloud** · **Platform Engineering**

Chaque réponse vous donne une réponse courte à dire à voix haute, le détail et les compromis qui la sous-tendent, un exemple exécutable et les questions de relance à prévoir.

<!-- LANGS:START -->

🌐 **Lire dans votre langue:** [English](../README.md) · [Español](./README.es.md) · **Français** · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [Italiano](./README.it.md) · [简体中文](./README.zh-CN.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [हिन्दी](./README.hi.md) · [العربية](./README.ar.md) · [Русский](./README.ru.md) · [Türkçe](./README.tr.md)

<!-- LANGS:END -->

[![Validate](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml)
[![Deploy Knowledge Graph](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml)

<!-- BADGES:START -->

![Questions](https://img.shields.io/badge/questions-787-blue)
![Topics](https://img.shields.io/badge/topics-40-blueviolet)
![Difficulty](https://img.shields.io/badge/difficulty-🟢%20177%20·%20🟡%20394%20·%20🔴%20216-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

<!-- BADGES:END -->

[🌐 Graphe de connaissances 3D](https://mchittineni.github.io/ultimate-devops-guide/) · [📖 Leçons traduites](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/fr) · [📋 Index complet des questions (anglais)](../README.md#-all-questions) · [🤝 Contribuer](../CONTRIBUTING.md)

⭐ Ajoutez une étoile au projet s'il vous aide à décrocher le poste.

</div>

> [!NOTE]
> **L'anglais fait foi.** Cette page d'accueil est traduite à la main et versionnée dans le dépôt. Les leçons sont traduites automatiquement sur la branche [`translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n) : [lisez-les en français](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/fr). En cas de divergence avec l'original anglais, c'est l'original anglais qui a raison.

---

## 🌐 Graphe de connaissances 3D

Explorez visuellement toutes les questions et tous les thèmes : les liens entre eux, les concepts transverses et des filtres en direct par difficulté, domaine ou mot-clé.

👉 **[Ouvrir le graphe de connaissances 3D interactif](https://mchittineni.github.io/ultimate-devops-guide/)**

---

## 🚀 Choisissez votre rôle

Treize parcours, chacun étant un ordre de lecture plutôt qu'une pile de liens. Commencez à gauche et avancez vers la droite.

> **Un entretien dans quinze jours ?** Commencez par [Interview Experience](../interview-experience/README.md) : déroulé des tours, comment présenter votre projet, comment aborder les questions de mise en situation, et une liste de ce qui est réellement demandé.

| 🎯 Rôle visé                | À lire dans cet ordre                                                                                                                                                                                                                                                                         |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **En entretien maintenant** | [Interview Experience](../interview-experience/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Docker](../docker/README.md) → [Kubernetes](../kubernetes/README.md) → [IaC](../infrastructure-as-code/README.md)                 |
| **DevOps junior / associé** | [Core Concepts](../core-devops-concepts/README.md) → [Docker](../docker/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Scripting](../scripting-and-automation/README.md) → [CI/CD](../cicd/README.md)                           |
| **Ingénieur·e DevSecOps**   | [DevSecOps](../devsecops/README.md) → [Security & Compliance](../security-and-compliance/README.md) → [Network Security](../network-security/README.md) → [CI/CD](../cicd/README.md)                                                                                                          |
| **Ingénieur·e SecOps**      | [SecOps](../secops/README.md) → [Network Security](../network-security/README.md) → [Incident Management](../incident-management/README.md) → [Security & Compliance](../security-and-compliance/README.md)                                                                                   |
| **Ingénieur·e SRE**         | [SRE](../site-reliability-engineering/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Incident Management](../incident-management/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Metrics](../devops-metrics-and-kpis/README.md)          |
| **Ingénieur·e SLO**         | [SLO Engineering](../slo-engineering/README.md) → [SRE](../site-reliability-engineering/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Monitoring & Logging](../monitoring-and-logging/README.md)                                                        |
| **Ingénieur·e SLA**         | [SLA Management](../sla-management/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md) → [Backup & DR](../backup-and-disaster-recovery/README.md)                                                               |
| **Ingénieur·e AWS**         | [AWS Engineering](../aws-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Ingénieur·e Azure**       | [Azure Engineering](../azure-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                 |
| **Ingénieur·e GCP**         | [GCP Engineering](../gcp-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Ingénieur·e cloud**       | [Cloud Engineering](../cloud-engineering/README.md) → [Cloud Platforms](../cloud-platforms/README.md) → [IaC](../infrastructure-as-code/README.md) → [Cloud Migration](../cloud-migration/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md)                     |
| **Ingénieur·e plateforme**  | [Platform Engineering](../platform-engineering/README.md) → [Kubernetes](../kubernetes/README.md) → [Orchestration Advanced](../container-orchestration-advanced/README.md) → [Tools & Automation](../devops-tools-and-automation/README.md) → [Advanced](../advanced-devops-cloud/README.md) |
| **Senior / lead**           | [Cloud Native](../cloud-native-architecture/README.md) → [Platform Engineering](../platform-engineering/README.md) → [Cost](../cloud-cost-optimization/README.md) → [Culture](../devops-culture-and-practices/README.md) → [Advanced](../advanced-devops-cloud/README.md)                     |

---

## 📚 Parcourir les thèmes et les questions

L'index complet (chaque thème avec son nombre de questions, et chaque question regroupée par thème) se trouve dans le [README anglais](../README.md#-all-questions). Les versions traduites automatiquement de chaque index de thème et de chaque leçon sont sur la [branche `translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/fr).

---

## 🧠 Structure des réponses

Chaque réponse suit les mêmes quatre temps : lisez une section en profondeur, ou les quatre.

| Section                                     | Ce qu'elle vous apporte                                                                                              |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Réponse courte** (_Short answer_)         | Deux ou trois phrases à dire à voix haute. Commencez ici.                                                            |
| **Détail** (_Detail_)                       | Le fond : mécanismes, compromis et le vocabulaire qui trahit l'expérience.                                           |
| **Exemple** (_Example_)                     | De vraies commandes, du YAML ou du code à exécuter et adapter.                                                       |
| **Conseils d'entretien** (_Interview tips_) | Les questions de relance, les pièges courants et ce qui distingue une réponse solide d'une réponse apprise par cœur. |

La difficulté est indiquée par 🟢 Débutant · 🟡 Intermédiaire · 🔴 Avancé.

**Trois façons de l'utiliser :**

- **Préparer un rôle précis** : suivez le parcours du tableau ci-dessus et lisez la partie « What interviewers probe here » du README de chaque thème avant ses questions.
- **Révision générale** : lisez les réponses courtes d'un thème, puis approfondissez seulement là où vous hésitez.
- **Obsidian / coffre de notes** : chaque fichier porte un frontmatter YAML (`title`, `id`, `category`, `difficulty`, `tags`), ce qui permet d'ouvrir tout le dépôt comme coffre et de le parcourir par tag.

---

## 🌍 À propos des traductions

- **Cette page** est traduite à la main et relue comme toute autre modification. Les corrections sont bienvenues sous forme de pull request sur `i18n/README.fr.md`.
- **Les leçons** sont traduites automatiquement par un workflow GitHub Actions à chaque modification du contenu anglais, puis publiées sur la branche `translations`. Le code, les commandes et la configuration ne sont jamais traduits.
- **Pour corriger une leçon**, améliorez l'original anglais : la traduction est régénérée à partir de lui. Les modifications faites directement sur la branche `translations` sont écrasées.
- **Votre langue manque ?** [Ouvrez une issue](https://github.com/mchittineni/ultimate-devops-guide/issues/new) pour la demander.

---

## 🤝 Contribuer

Nouvelles questions, meilleures réponses et corrections sont les bienvenues, en anglais, puisque l'anglais est la source de référence. [CONTRIBUTING.md](../CONTRIBUTING.md) décrit le format des fichiers, les règles de nommage et les vérifications locales à lancer avant d'ouvrir une pull request. Le [Code de conduite](../CODE_OF_CONDUCT.md) et la [Politique de sécurité](../SECURITY.md) fixent les règles du jeu.

## 📄 Licence

Publié sous [licence MIT](../LICENSE).
