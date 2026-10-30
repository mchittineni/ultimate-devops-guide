<div align="center">

# ⚙️ Guia de Cloud, DevOps, Platform Engineering e SRE

**Perguntas de entrevista respondidas com a profundidade que um entrevistador realmente espera.**

Trilhas por função: **DevOps** (júnior → sênior) · **DevSecOps** · **SecOps** · **SRE** · **SLO** · **SLA** · **AWS** · **Azure** · **GCP** · **Cloud** · **Platform Engineering**

Cada resposta traz uma resposta curta para você dizer em voz alta, o detalhe e os trade-offs por trás dela, um exemplo executável e as perguntas de acompanhamento que você deve esperar.

<!-- LANGS:START -->

🌐 **Leia no seu idioma:** [English](../README.md) · [Español](./README.es.md) · [Français](./README.fr.md) · **Português** · [Deutsch](./README.de.md) · [Italiano](./README.it.md) · [简体中文](./README.zh-CN.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [हिन्दी](./README.hi.md) · [العربية](./README.ar.md) · [Русский](./README.ru.md) · [Türkçe](./README.tr.md)

<!-- LANGS:END -->

[![Validate](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml)
[![Deploy Knowledge Graph](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml)

<!-- BADGES:START -->

![Questions](https://img.shields.io/badge/questions-787-blue)
![Topics](https://img.shields.io/badge/topics-40-blueviolet)
![Difficulty](https://img.shields.io/badge/difficulty-🟢%20177%20·%20🟡%20394%20·%20🔴%20216-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

<!-- BADGES:END -->

[🌐 Grafo de conhecimento 3D](https://mchittineni.github.io/ultimate-devops-guide/) · [📖 Lições traduzidas](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/pt) · [📋 Índice completo de perguntas (inglês)](../README.md#-all-questions) · [🤝 Como contribuir](../CONTRIBUTING.md)

⭐ Dê uma estrela ao projeto se ele ajudar você a conquistar a vaga.

</div>

> [!NOTE]
> **O inglês é a versão de referência.** Esta página inicial é traduzida à mão e versionada no repositório. As lições são traduzidas automaticamente no branch [`translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n): [leia-as em português](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/pt). Se uma tradução divergir do original em inglês, vale o original em inglês.

---

## 🌐 Grafo de conhecimento 3D

Explore visualmente todas as perguntas e todos os temas: as relações entre eles, os conceitos que cruzam temas e filtros em tempo real por dificuldade, área ou palavra-chave.

👉 **[Abrir o grafo de conhecimento 3D interativo](https://mchittineni.github.io/ultimate-devops-guide/)**

---

## 🚀 Escolha sua função

Treze trilhas, cada uma uma ordem de leitura, não uma pilha de links. Comece pela esquerda e siga para a direita.

> **Entrevista daqui a duas semanas?** Comece por [Interview Experience](../interview-experience/README.md): estrutura das etapas, como explicar seu projeto, como lidar com perguntas de cenário e uma checklist do que realmente é perguntado.

| 🎯 Função desejada              | Leia nesta ordem                                                                                                                                                                                                                                                                              |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Em entrevistas agora**        | [Interview Experience](../interview-experience/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Docker](../docker/README.md) → [Kubernetes](../kubernetes/README.md) → [IaC](../infrastructure-as-code/README.md)                 |
| **DevOps júnior / associado**   | [Core Concepts](../core-devops-concepts/README.md) → [Docker](../docker/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Scripting](../scripting-and-automation/README.md) → [CI/CD](../cicd/README.md)                           |
| **Engenheiro(a) DevSecOps**     | [DevSecOps](../devsecops/README.md) → [Security & Compliance](../security-and-compliance/README.md) → [Network Security](../network-security/README.md) → [CI/CD](../cicd/README.md)                                                                                                          |
| **Engenheiro(a) SecOps**        | [SecOps](../secops/README.md) → [Network Security](../network-security/README.md) → [Incident Management](../incident-management/README.md) → [Security & Compliance](../security-and-compliance/README.md)                                                                                   |
| **Engenheiro(a) SRE**           | [SRE](../site-reliability-engineering/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Incident Management](../incident-management/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Metrics](../devops-metrics-and-kpis/README.md)          |
| **Engenheiro(a) de SLO**        | [SLO Engineering](../slo-engineering/README.md) → [SRE](../site-reliability-engineering/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Monitoring & Logging](../monitoring-and-logging/README.md)                                                        |
| **Engenheiro(a) de SLA**        | [SLA Management](../sla-management/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md) → [Backup & DR](../backup-and-disaster-recovery/README.md)                                                               |
| **Engenheiro(a) AWS**           | [AWS Engineering](../aws-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Engenheiro(a) Azure**         | [Azure Engineering](../azure-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                 |
| **Engenheiro(a) GCP**           | [GCP Engineering](../gcp-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Engenheiro(a) de cloud**      | [Cloud Engineering](../cloud-engineering/README.md) → [Cloud Platforms](../cloud-platforms/README.md) → [IaC](../infrastructure-as-code/README.md) → [Cloud Migration](../cloud-migration/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md)                     |
| **Engenheiro(a) de plataforma** | [Platform Engineering](../platform-engineering/README.md) → [Kubernetes](../kubernetes/README.md) → [Orchestration Advanced](../container-orchestration-advanced/README.md) → [Tools & Automation](../devops-tools-and-automation/README.md) → [Advanced](../advanced-devops-cloud/README.md) |
| **Sênior / líder técnico**      | [Cloud Native](../cloud-native-architecture/README.md) → [Platform Engineering](../platform-engineering/README.md) → [Cost](../cloud-cost-optimization/README.md) → [Culture](../devops-culture-and-practices/README.md) → [Advanced](../advanced-devops-cloud/README.md)                     |

---

## 📚 Navegar por temas e perguntas

O índice completo (cada tema com a contagem de perguntas e cada pergunta agrupada por tema) está no [README em inglês](../README.md#-all-questions). As versões traduzidas automaticamente de cada índice de tema e de cada lição estão no [branch `translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/pt).

---

## 🧠 Como as respostas são estruturadas

Toda resposta segue as mesmas quatro etapas, então você pode ler uma seção a fundo ou as quatro:

| Seção                                      | O que ela oferece                                                                                        |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| **Resposta curta** (_Short answer_)        | Duas ou três frases que você poderia dizer em voz alta. Comece aqui.                                     |
| **Detalhe** (_Detail_)                     | A substância: mecanismos, trade-offs e o vocabulário que demonstra experiência.                          |
| **Exemplo** (_Example_)                    | Comandos, YAML ou código reais que você pode executar e adaptar.                                         |
| **Dicas de entrevista** (_Interview tips_) | As perguntas de acompanhamento, as armadilhas comuns e o que separa uma resposta sólida de uma decorada. |

A dificuldade é marcada como 🟢 Iniciante · 🟡 Intermediário · 🔴 Avançado.

**Três formas de estudar:**

- **Preparação para uma função específica**: siga a trilha da tabela acima e leia a parte "What interviewers probe here" do README de cada tema antes das perguntas.
- **Revisão geral**: leia as respostas curtas de um tema e aprofunde-se só onde hesitar.
- **Obsidian / cofre de notas**: todo arquivo tem frontmatter YAML (`title`, `id`, `category`, `difficulty`, `tags`), então o repositório inteiro pode ser aberto como cofre e navegado por tags.

---

## 🌍 Sobre as traduções

- **Esta página** é traduzida à mão e revisada como qualquer outra mudança. Correções são bem-vindas como pull request em `i18n/README.pt.md`.
- **As lições** são traduzidas automaticamente por um workflow do GitHub Actions sempre que o conteúdo em inglês muda, e publicadas no branch `translations`. Código, comandos e configuração nunca são traduzidos.
- **Para corrigir uma lição**, melhore o original em inglês: a tradução é gerada novamente a partir dele. Edições feitas diretamente no branch `translations` são sobrescritas.
- **Falta o seu idioma?** [Abra uma issue](https://github.com/mchittineni/ultimate-devops-guide/issues/new) para pedir.

---

## 🤝 Como contribuir

Novas perguntas, respostas melhores e correções são bem-vindas, em inglês, já que o inglês é a fonte de referência. O [CONTRIBUTING.md](../CONTRIBUTING.md) descreve o formato dos arquivos, as regras de nomes e as verificações locais antes de abrir um pull request. O [Código de conduta](../CODE_OF_CONDUCT.md) e a [Política de segurança](../SECURITY.md) definem as regras básicas.

## 📄 Licença

Publicado sob a [licença MIT](../LICENSE).
