<div align="center">

# ⚙️ क्लाउड, DevOps, प्लेटफ़ॉर्म इंजीनियरिंग और SRE गाइड

**इंटरव्यू के सवाल, उसी गहराई से जवाब दिए गए जिसकी इंटरव्यूअर सच में उम्मीद करते हैं।**

रोल ट्रैक: **DevOps** (जूनियर → सीनियर) · **DevSecOps** · **SecOps** · **SRE** · **SLO** · **SLA** · **AWS** · **Azure** · **GCP** · **Cloud** · **Platform Engineering**

हर जवाब में आपको मिलता है: एक छोटा जवाब जिसे आप बोलकर कह सकें, उसके पीछे का विवरण और ट्रेड-ऑफ़, चलाने लायक एक उदाहरण, और आगे पूछे जाने वाले सवाल।

<!-- LANGS:START -->

🌐 **अपनी भाषा में पढ़ें:** [English](../README.md) · [Español](./README.es.md) · [Français](./README.fr.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [Italiano](./README.it.md) · [简体中文](./README.zh-CN.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · **हिन्दी** · [العربية](./README.ar.md) · [Русский](./README.ru.md) · [Türkçe](./README.tr.md)

<!-- LANGS:END -->

[![Validate](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml)
[![Deploy Knowledge Graph](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml)

<!-- BADGES:START -->

![Questions](https://img.shields.io/badge/questions-787-blue)
![Topics](https://img.shields.io/badge/topics-40-blueviolet)
![Difficulty](https://img.shields.io/badge/difficulty-🟢%20177%20·%20🟡%20394%20·%20🔴%20216-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

<!-- BADGES:END -->

[🌐 3D नॉलेज ग्राफ़](https://mchittineni.github.io/ultimate-devops-guide/) · [📖 अनुवादित पाठ](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/hi) · [📋 सभी सवालों की पूरी सूची (अंग्रेज़ी)](../README.md#-all-questions) · [🤝 योगदान करें](../CONTRIBUTING.md)

⭐ अगर यह प्रोजेक्ट आपको नौकरी पाने में मदद करे, तो इसे स्टार दें।

</div>

> [!NOTE]
> **अंग्रेज़ी संस्करण ही मानक है।** यह मुख्य पृष्ठ हाथ से अनुवादित है और रिपॉज़िटरी में कमिट किया गया है। पाठों का मशीन अनुवाद [`translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n) ब्रांच पर होता है: [उन्हें हिन्दी में पढ़ें](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/hi)। अगर किसी अनुवाद और अंग्रेज़ी मूल में अंतर हो, तो अंग्रेज़ी मूल ही सही है।

---

## 🌐 3D नॉलेज ग्राफ़

सभी सवालों और विषयों को विज़ुअल रूप में देखें: उनके आपसी संबंध, कई विषयों में फैली अवधारणाएँ, और कठिनाई, क्षेत्र या कीवर्ड के आधार पर लाइव फ़िल्टर।

👉 **[इंटरैक्टिव 3D नॉलेज ग्राफ़ खोलें](https://mchittineni.github.io/ultimate-devops-guide/)**

---

## 🚀 अपना रोल चुनें

तेरह ट्रैक, हर एक पढ़ने का एक क्रम है, लिंक का ढेर नहीं। बाईं ओर से शुरू करें और दाईं ओर बढ़ें।

> **दो हफ़्ते में इंटरव्यू है?** [Interview Experience](../interview-experience/README.md) से शुरू करें: इसमें इंटरव्यू राउंड की संरचना, अपने प्रोजेक्ट को समझाने का तरीका, सिनेरियो वाले सवालों से निपटना, और सच में पूछे जाने वाले सवालों की चेकलिस्ट है।

| 🎯 लक्ष्य रोल               | इस क्रम में पढ़ें                                                                                                                                                                                                                                                                             |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **अभी इंटरव्यू दे रहे हैं** | [Interview Experience](../interview-experience/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Docker](../docker/README.md) → [Kubernetes](../kubernetes/README.md) → [IaC](../infrastructure-as-code/README.md)                 |
| **जूनियर / एसोसिएट DevOps** | [Core Concepts](../core-devops-concepts/README.md) → [Docker](../docker/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Scripting](../scripting-and-automation/README.md) → [CI/CD](../cicd/README.md)                           |
| **DevSecOps इंजीनियर**      | [DevSecOps](../devsecops/README.md) → [Security & Compliance](../security-and-compliance/README.md) → [Network Security](../network-security/README.md) → [CI/CD](../cicd/README.md)                                                                                                          |
| **SecOps इंजीनियर**         | [SecOps](../secops/README.md) → [Network Security](../network-security/README.md) → [Incident Management](../incident-management/README.md) → [Security & Compliance](../security-and-compliance/README.md)                                                                                   |
| **SRE इंजीनियर**            | [SRE](../site-reliability-engineering/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Incident Management](../incident-management/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Metrics](../devops-metrics-and-kpis/README.md)          |
| **SLO इंजीनियर**            | [SLO Engineering](../slo-engineering/README.md) → [SRE](../site-reliability-engineering/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Monitoring & Logging](../monitoring-and-logging/README.md)                                                        |
| **SLA इंजीनियर**            | [SLA Management](../sla-management/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md) → [Backup & DR](../backup-and-disaster-recovery/README.md)                                                               |
| **AWS इंजीनियर**            | [AWS Engineering](../aws-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Azure इंजीनियर**          | [Azure Engineering](../azure-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                 |
| **GCP इंजीनियर**            | [GCP Engineering](../gcp-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **क्लाउड इंजीनियर**         | [Cloud Engineering](../cloud-engineering/README.md) → [Cloud Platforms](../cloud-platforms/README.md) → [IaC](../infrastructure-as-code/README.md) → [Cloud Migration](../cloud-migration/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md)                     |
| **प्लेटफ़ॉर्म इंजीनियर**    | [Platform Engineering](../platform-engineering/README.md) → [Kubernetes](../kubernetes/README.md) → [Orchestration Advanced](../container-orchestration-advanced/README.md) → [Tools & Automation](../devops-tools-and-automation/README.md) → [Advanced](../advanced-devops-cloud/README.md) |
| **सीनियर / लीड**            | [Cloud Native](../cloud-native-architecture/README.md) → [Platform Engineering](../platform-engineering/README.md) → [Cost](../cloud-cost-optimization/README.md) → [Culture](../devops-culture-and-practices/README.md) → [Advanced](../advanced-devops-cloud/README.md)                     |

---

## 📚 विषय और सवाल देखें

पूरी सूची (हर विषय और उसके सवालों की संख्या, और विषय के अनुसार समूहित हर सवाल) [अंग्रेज़ी README](../README.md#-all-questions) में है। हर विषय-सूची और हर पाठ के मशीन-अनुवादित संस्करण [`translations` ब्रांच](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/hi) पर हैं।

---

## 🧠 जवाबों की संरचना

हर जवाब एक जैसे चार हिस्सों में बँटा है, इसलिए आप किसी एक हिस्से को गहराई से या चारों को पढ़ सकते हैं:

| हिस्सा                                | आपको क्या मिलता है                                                                                  |
| ------------------------------------- | --------------------------------------------------------------------------------------------------- |
| **छोटा जवाब** (_Short answer_)        | दो-तीन वाक्य जिन्हें आप बोलकर कह सकें। यहीं से शुरू करें।                                           |
| **विवरण** (_Detail_)                  | असली बात: काम करने का तरीका, ट्रेड-ऑफ़, और वह शब्दावली जो अनुभव दिखाती है।                          |
| **उदाहरण** (_Example_)                | असली कमांड, YAML या कोड जिन्हें आप चला और बदल सकें।                                                 |
| **इंटरव्यू टिप्स** (_Interview tips_) | आगे पूछे जाने वाले सवाल, आम गलतियाँ, और वे बातें जो एक मज़बूत जवाब को रटे हुए जवाब से अलग करती हैं। |

कठिनाई को 🟢 शुरुआती · 🟡 मध्यम · 🔴 उन्नत से दर्शाया गया है।

**इसे इस्तेमाल करने के तीन तरीके:**

- **किसी खास रोल की तैयारी**: ऊपर दी गई तालिका का ट्रैक अपनाएँ, और हर विषय के सवालों से पहले उसके README का "What interviewers probe here" हिस्सा पढ़ें।
- **व्यापक दोहराव**: किसी विषय के छोटे जवाब पढ़ें, और सिर्फ़ वहीं गहराई में जाएँ जहाँ आपको संदेह हो।
- **Obsidian / नोट वॉल्ट**: हर फ़ाइल में YAML फ़्रंटमैटर (`title`, `id`, `category`, `difficulty`, `tags`) है, इसलिए पूरी रिपॉज़िटरी को वॉल्ट की तरह खोलकर टैग से ब्राउज़ किया जा सकता है।

---

## 🌍 अनुवाद के बारे में

- **यह पृष्ठ** हाथ से अनुवादित है और किसी भी दूसरे बदलाव की तरह इसकी समीक्षा होती है। सुधार `i18n/README.hi.md` पर pull request के रूप में स्वागत योग्य हैं।
- **पाठ** हर बार अंग्रेज़ी सामग्री बदलने पर GitHub Actions वर्कफ़्लो द्वारा मशीन से अनुवादित होते हैं और `translations` ब्रांच पर प्रकाशित होते हैं। कोड, कमांड और कॉन्फ़िगरेशन का कभी अनुवाद नहीं होता।
- **किसी पाठ को सुधारने के लिए** अंग्रेज़ी मूल को बेहतर बनाएँ: अनुवाद उसी से अपने-आप दोबारा बनता है। `translations` ब्रांच पर सीधे किए गए बदलाव मिट जाते हैं।
- **आपकी भाषा नहीं है?** उसका अनुरोध करने के लिए [issue खोलें](https://github.com/mchittineni/ultimate-devops-guide/issues/new)।

---

## 🤝 योगदान करें

नए सवाल, बेहतर जवाब और सुधार, सभी का स्वागत है; कृपया अंग्रेज़ी में लिखें, क्योंकि अंग्रेज़ी ही मानक स्रोत है। [CONTRIBUTING.md](../CONTRIBUTING.md) में फ़ाइल फ़ॉर्मेट, नामकरण के नियम और pull request खोलने से पहले चलाई जाने वाली लोकल जाँचें दी गई हैं। [आचार संहिता](../CODE_OF_CONDUCT.md) और [सुरक्षा नीति](../SECURITY.md) बुनियादी नियम तय करती हैं।

## 📄 लाइसेंस

[MIT लाइसेंस](../LICENSE) के तहत जारी।
