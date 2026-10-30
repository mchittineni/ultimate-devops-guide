<div dir="rtl">

<div align="center">

# ⚙️ دليل الحوسبة السحابية وDevOps وهندسة المنصات وSRE

**أسئلة مقابلات مُجاب عنها بالعمق الذي يتوقعه المُقابِل فعلًا.**

مسارات حسب الدور: **DevOps** (مبتدئ ← خبير) · **DevSecOps** · **SecOps** · **SRE** · **SLO** · **SLA** · **AWS** · **Azure** · **GCP** · **Cloud** · **Platform Engineering**

تمنحك كل إجابة: إجابة قصيرة يمكنك قولها بصوت عالٍ، والتفاصيل والمفاضلات الكامنة وراءها، ومثالًا قابلًا للتشغيل، وأسئلة المتابعة المتوقعة.

<!-- LANGS:START -->

🌐 **اقرأ بلغتك:** [English](../README.md) · [Español](./README.es.md) · [Français](./README.fr.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [Italiano](./README.it.md) · [简体中文](./README.zh-CN.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [हिन्दी](./README.hi.md) · **العربية** · [Русский](./README.ru.md) · [Türkçe](./README.tr.md)

<!-- LANGS:END -->

[![Validate](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml)
[![Deploy Knowledge Graph](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml)

<!-- BADGES:START -->

![Questions](https://img.shields.io/badge/questions-787-blue)
![Topics](https://img.shields.io/badge/topics-40-blueviolet)
![Difficulty](https://img.shields.io/badge/difficulty-🟢%20177%20·%20🟡%20394%20·%20🔴%20216-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

<!-- BADGES:END -->

[🌐 الرسم المعرفي ثلاثي الأبعاد](https://mchittineni.github.io/ultimate-devops-guide/) · [📖 الدروس المترجمة](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/ar) · [📋 الفهرس الكامل للأسئلة (بالإنجليزية)](../README.md#-all-questions) · [🤝 المساهمة](../CONTRIBUTING.md)

⭐ امنح المشروع نجمة إن ساعدك في الحصول على الوظيفة.

</div>

> [!NOTE]
> **النسخة الإنجليزية هي المرجع.** هذه الصفحة الرئيسية مترجمة يدويًا ومحفوظة في المستودع. أما الدروس فتُترجم آليًا على الفرع [`translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n): [اقرأها بالعربية](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/ar). إذا اختلفت ترجمة عن الأصل الإنجليزي، فالأصل الإنجليزي هو الصحيح.

---

## 🌐 الرسم المعرفي ثلاثي الأبعاد

استكشف جميع الأسئلة والمواضيع بصريًا: العلاقات بينها، والمفاهيم المشتركة بين المواضيع، وعوامل تصفية فورية حسب الصعوبة أو المجال أو الكلمة المفتاحية.

👉 **[افتح الرسم المعرفي التفاعلي ثلاثي الأبعاد](https://mchittineni.github.io/ultimate-devops-guide/)**

---

## 🚀 اختر دورك

ثلاثة عشر مسارًا، كل منها ترتيب للقراءة وليس كومة من الروابط. ابدأ بأول موضوع في المسار وتابع بالترتيب.

> **لديك مقابلة بعد أسبوعين؟** ابدأ بـ [Interview Experience](../interview-experience/README.md): يغطي بنية جولات المقابلة، وكيف تشرح مشروعك، وكيف تتعامل مع أسئلة السيناريوهات، وقائمة تحقق بما يُسأل عنه فعلًا.

| 🎯 الدور المستهدف           | اقرأ بهذا الترتيب                                                                                                                                                                                                                                                                             |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **في مرحلة المقابلات الآن** | [Interview Experience](../interview-experience/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Docker](../docker/README.md) → [Kubernetes](../kubernetes/README.md) → [IaC](../infrastructure-as-code/README.md)                 |
| **DevOps مبتدئ / مساعد**    | [Core Concepts](../core-devops-concepts/README.md) → [Docker](../docker/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Scripting](../scripting-and-automation/README.md) → [CI/CD](../cicd/README.md)                           |
| **مهندس DevSecOps**         | [DevSecOps](../devsecops/README.md) → [Security & Compliance](../security-and-compliance/README.md) → [Network Security](../network-security/README.md) → [CI/CD](../cicd/README.md)                                                                                                          |
| **مهندس SecOps**            | [SecOps](../secops/README.md) → [Network Security](../network-security/README.md) → [Incident Management](../incident-management/README.md) → [Security & Compliance](../security-and-compliance/README.md)                                                                                   |
| **مهندس SRE**               | [SRE](../site-reliability-engineering/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Incident Management](../incident-management/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Metrics](../devops-metrics-and-kpis/README.md)          |
| **مهندس SLO**               | [SLO Engineering](../slo-engineering/README.md) → [SRE](../site-reliability-engineering/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Monitoring & Logging](../monitoring-and-logging/README.md)                                                        |
| **مهندس SLA**               | [SLA Management](../sla-management/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md) → [Backup & DR](../backup-and-disaster-recovery/README.md)                                                               |
| **مهندس AWS**               | [AWS Engineering](../aws-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **مهندس Azure**             | [Azure Engineering](../azure-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                 |
| **مهندس GCP**               | [GCP Engineering](../gcp-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **مهندس سحابة**             | [Cloud Engineering](../cloud-engineering/README.md) → [Cloud Platforms](../cloud-platforms/README.md) → [IaC](../infrastructure-as-code/README.md) → [Cloud Migration](../cloud-migration/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md)                     |
| **مهندس منصات**             | [Platform Engineering](../platform-engineering/README.md) → [Kubernetes](../kubernetes/README.md) → [Orchestration Advanced](../container-orchestration-advanced/README.md) → [Tools & Automation](../devops-tools-and-automation/README.md) → [Advanced](../advanced-devops-cloud/README.md) |
| **خبير / قائد تقني**        | [Cloud Native](../cloud-native-architecture/README.md) → [Platform Engineering](../platform-engineering/README.md) → [Cost](../cloud-cost-optimization/README.md) → [Culture](../devops-culture-and-practices/README.md) → [Advanced](../advanced-devops-cloud/README.md)                     |

---

## 📚 تصفّح المواضيع والأسئلة

الفهرس الكامل (كل موضوع مع عدد أسئلته، وكل سؤال مصنّف حسب موضوعه) موجود في [ملف README الإنجليزي](../README.md#-all-questions). والنسخ المترجمة آليًا لكل فهرس موضوع ولكل درس موجودة على [الفرع `translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/ar).

---

## 🧠 كيف تُبنى الإجابات

تتبع كل إجابة الأجزاء الأربعة نفسها، فيمكنك قراءة جزء واحد بعمق أو الأجزاء الأربعة كلها:

| الجزء                                 | ما يقدمه لك                                                                     |
| ------------------------------------- | ------------------------------------------------------------------------------- |
| **إجابة قصيرة** (_Short answer_)      | جملتان أو ثلاث يمكنك قولها بصوت عالٍ. ابدأ من هنا.                              |
| **التفاصيل** (_Detail_)               | الجوهر: الآليات، والمفاضلات، والمصطلحات التي تدل على الخبرة.                    |
| **مثال** (_Example_)                  | أوامر أو YAML أو شيفرة حقيقية يمكنك تشغيلها وتعديلها.                           |
| **نصائح للمقابلة** (_Interview tips_) | أسئلة المتابعة، والأخطاء الشائعة، وما يميز الإجابة المتينة عن الإجابة المحفوظة. |

تُحدَّد الصعوبة بـ 🟢 مبتدئ · 🟡 متوسط · 🔴 متقدم.

**ثلاث طرق للاستفادة منه:**

- **التحضير لدور محدد**: اتبع المسار من الجدول أعلاه، واقرأ قسم "What interviewers probe here" في ملف README لكل موضوع قبل أسئلته.
- **مراجعة شاملة**: اقرأ الإجابات القصيرة في موضوع ما، ثم تعمّق فقط حيث تتردد.
- **Obsidian / خزنة ملاحظات**: يحمل كل ملف بيانات YAML أمامية (`title` و`id` و`category` و`difficulty` و`tags`)، لذا يمكن فتح المستودع كله كخزنة وتصفّحه حسب الوسوم.

---

## 🌍 عن الترجمات

- **هذه الصفحة** مترجمة يدويًا وتُراجَع مثل أي تغيير آخر. نرحب بالتصحيحات عبر pull request على الملف `i18n/README.ar.md`.
- **الدروس** يترجمها آليًا سير عمل GitHub Actions في كل مرة يتغير فيها المحتوى الإنجليزي، وتُنشر على الفرع `translations`. لا تُترجم الشيفرة ولا الأوامر ولا الإعدادات أبدًا.
- **لتصحيح درس**، حسّن الأصل الإنجليزي: تُعاد الترجمة منه تلقائيًا. أي تعديل مباشر على الفرع `translations` سيُستبدل.
- **لغتك غير موجودة؟** [افتح issue](https://github.com/mchittineni/ultimate-devops-guide/issues/new) لطلبها.

---

## 🤝 المساهمة

نرحب بالأسئلة الجديدة والإجابات الأفضل والتصحيحات، باللغة الإنجليزية لأنها المصدر المرجعي. يشرح [CONTRIBUTING.md](../CONTRIBUTING.md) صيغة الملفات وقواعد التسمية والفحوص المحلية قبل فتح pull request. وتحدد [مدونة السلوك](../CODE_OF_CONDUCT.md) و[سياسة الأمان](../SECURITY.md) القواعد الأساسية.

## 📄 الترخيص

منشور بموجب [ترخيص MIT](../LICENSE).

</div>
