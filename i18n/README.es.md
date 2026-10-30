<div align="center">

# ⚙️ Guía de Cloud, DevOps, Platform Engineering y SRE

**Preguntas de entrevista respondidas con la profundidad que un entrevistador realmente espera.**

Rutas por rol: **DevOps** (junior → senior) · **DevSecOps** · **SecOps** · **SRE** · **SLO** · **SLA** · **AWS** · **Azure** · **GCP** · **Cloud** · **Platform Engineering**

Cada respuesta incluye una respuesta breve que puedes decir en voz alta, el detalle y los compromisos que hay detrás, un ejemplo ejecutable y las preguntas de seguimiento que cabe esperar.

<!-- LANGS:START -->

🌐 **Lee en tu idioma:** [English](../README.md) · **Español** · [Français](./README.fr.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [Italiano](./README.it.md) · [简体中文](./README.zh-CN.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [हिन्दी](./README.hi.md) · [العربية](./README.ar.md) · [Русский](./README.ru.md) · [Türkçe](./README.tr.md)

<!-- LANGS:END -->

[![Validate](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml)
[![Deploy Knowledge Graph](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml)

<!-- BADGES:START -->

![Questions](https://img.shields.io/badge/questions-787-blue)
![Topics](https://img.shields.io/badge/topics-40-blueviolet)
![Difficulty](https://img.shields.io/badge/difficulty-🟢%20177%20·%20🟡%20394%20·%20🔴%20216-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

<!-- BADGES:END -->

[🌐 Grafo de conocimiento 3D](https://mchittineni.github.io/ultimate-devops-guide/) · [📖 Lecciones traducidas](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/es) · [📋 Índice completo de preguntas (inglés)](../README.md#-all-questions) · [🤝 Contribuir](../CONTRIBUTING.md)

⭐ Dale una estrella al proyecto si te ayuda a conseguir el puesto.

</div>

> [!NOTE]
> **El inglés es la versión de referencia.** Esta página de inicio está traducida a mano y guardada en el repositorio. Las lecciones se traducen automáticamente en la rama [`translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n): [léelas en español](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/es). Si una traducción no coincide con el original en inglés, el original en inglés es el correcto.

---

## 🌐 Grafo de conocimiento 3D

Explora visualmente todas las preguntas y temas: las relaciones entre ellos, los conceptos que atraviesan varios temas y filtros en vivo por dificultad, área o palabra clave.

👉 **[Abrir el grafo de conocimiento 3D interactivo](https://mchittineni.github.io/ultimate-devops-guide/)**

---

## 🚀 Elige tu rol

Trece rutas, cada una un orden de lectura y no un montón de enlaces. Empieza por la izquierda y avanza hacia la derecha.

> **¿Entrevista en dos semanas?** Empieza por [Interview Experience](../interview-experience/README.md): cubre la estructura de las rondas, cómo explicar tu proyecto, cómo afrontar preguntas de escenario y una lista de lo que realmente se pregunta.

| 🎯 Rol objetivo               | Lee en este orden                                                                                                                                                                                                                                                                             |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Entrevistando ahora**       | [Interview Experience](../interview-experience/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Docker](../docker/README.md) → [Kubernetes](../kubernetes/README.md) → [IaC](../infrastructure-as-code/README.md)                 |
| **DevOps junior / asociado**  | [Core Concepts](../core-devops-concepts/README.md) → [Docker](../docker/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Scripting](../scripting-and-automation/README.md) → [CI/CD](../cicd/README.md)                           |
| **Ingeniero/a DevSecOps**     | [DevSecOps](../devsecops/README.md) → [Security & Compliance](../security-and-compliance/README.md) → [Network Security](../network-security/README.md) → [CI/CD](../cicd/README.md)                                                                                                          |
| **Ingeniero/a SecOps**        | [SecOps](../secops/README.md) → [Network Security](../network-security/README.md) → [Incident Management](../incident-management/README.md) → [Security & Compliance](../security-and-compliance/README.md)                                                                                   |
| **Ingeniero/a SRE**           | [SRE](../site-reliability-engineering/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Incident Management](../incident-management/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Metrics](../devops-metrics-and-kpis/README.md)          |
| **Ingeniero/a de SLO**        | [SLO Engineering](../slo-engineering/README.md) → [SRE](../site-reliability-engineering/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Monitoring & Logging](../monitoring-and-logging/README.md)                                                        |
| **Ingeniero/a de SLA**        | [SLA Management](../sla-management/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md) → [Backup & DR](../backup-and-disaster-recovery/README.md)                                                               |
| **Ingeniero/a AWS**           | [AWS Engineering](../aws-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Ingeniero/a Azure**         | [Azure Engineering](../azure-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                 |
| **Ingeniero/a GCP**           | [GCP Engineering](../gcp-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Ingeniero/a cloud**         | [Cloud Engineering](../cloud-engineering/README.md) → [Cloud Platforms](../cloud-platforms/README.md) → [IaC](../infrastructure-as-code/README.md) → [Cloud Migration](../cloud-migration/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md)                     |
| **Ingeniero/a de plataforma** | [Platform Engineering](../platform-engineering/README.md) → [Kubernetes](../kubernetes/README.md) → [Orchestration Advanced](../container-orchestration-advanced/README.md) → [Tools & Automation](../devops-tools-and-automation/README.md) → [Advanced](../advanced-devops-cloud/README.md) |
| **Senior / líder técnico**    | [Cloud Native](../cloud-native-architecture/README.md) → [Platform Engineering](../platform-engineering/README.md) → [Cost](../cloud-cost-optimization/README.md) → [Culture](../devops-culture-and-practices/README.md) → [Advanced](../advanced-devops-cloud/README.md)                     |

---

## 📚 Explorar temas y preguntas

El índice completo (cada tema con su número de preguntas y cada pregunta agrupada por tema) está en el [README en inglés](../README.md#-all-questions). Las versiones traducidas automáticamente de cada índice de tema y de cada lección están en la [rama `translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/es).

---

## 🧠 Cómo se estructuran las respuestas

Todas las respuestas siguen los mismos cuatro pasos, así que puedes leer una sección a fondo o las cuatro:

| Sección                                            | Qué te aporta                                                                                                   |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **Respuesta breve** (_Short answer_)               | Dos o tres frases que podrías decir en voz alta. Empieza aquí.                                                  |
| **Detalle** (_Detail_)                             | La sustancia: mecanismos, compromisos y el vocabulario que demuestra experiencia.                               |
| **Ejemplo** (_Example_)                            | Comandos, YAML o código reales que puedes ejecutar y adaptar.                                                   |
| **Consejos para la entrevista** (_Interview tips_) | Las preguntas de seguimiento, las trampas habituales y lo que distingue una respuesta sólida de una memorizada. |

La dificultad se indica con 🟢 Principiante · 🟡 Intermedio · 🔴 Avanzado.

**Tres formas de recorrerla:**

- **Preparar un rol concreto**: sigue la ruta de la tabla anterior y lee la sección «What interviewers probe here» del README de cada tema antes de sus preguntas.
- **Repaso general**: lee las respuestas breves de un tema y profundiza solo donde dudes.
- **Obsidian / bóveda de notas**: cada archivo lleva frontmatter YAML (`title`, `id`, `category`, `difficulty`, `tags`), así que todo el repositorio puede abrirse como bóveda y navegarse por etiquetas.

---

## 🌍 Sobre las traducciones

- **Esta página** está traducida a mano y se revisa como cualquier otro cambio. Las correcciones son bienvenidas como pull request sobre `i18n/README.es.md`.
- **Las lecciones** las traduce automáticamente un workflow de GitHub Actions cada vez que cambia el contenido en inglés, y se publican en la rama `translations`. El código, los comandos y la configuración nunca se traducen.
- **Para corregir una lección**, mejora el original en inglés: la traducción se regenera a partir de él. Los cambios hechos directamente en la rama `translations` se sobrescriben.
- **¿Falta tu idioma?** [Abre un issue](https://github.com/mchittineni/ultimate-devops-guide/issues/new) para solicitarlo.

---

## 🤝 Contribuir

Las preguntas nuevas, las mejores respuestas y las correcciones son bienvenidas, en inglés, porque el inglés es la fuente de referencia. [CONTRIBUTING.md](../CONTRIBUTING.md) describe el formato de los archivos, las reglas de nombres y las comprobaciones locales antes de abrir un pull request. El [Código de conducta](../CODE_OF_CONDUCT.md) y la [Política de seguridad](../SECURITY.md) fijan las reglas básicas.

## 📄 Licencia

Publicado bajo la [licencia MIT](../LICENSE).
