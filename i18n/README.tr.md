<div align="center">

# ⚙️ Bulut, DevOps, Platform Mühendisliği ve SRE Rehberi

**Mülakat soruları, mülakatçının gerçekten beklediği derinlikte yanıtlandı.**

Role göre yollar: **DevOps** (junior → senior) · **DevSecOps** · **SecOps** · **SRE** · **SLO** · **SLA** · **AWS** · **Azure** · **GCP** · **Cloud** · **Platform Engineering**

Her yanıt size sesli söyleyebileceğiniz kısa bir cevap, arkasındaki ayrıntılar ve ödünleşimler, çalıştırılabilir bir örnek ve beklenecek takip sorularını verir.

<!-- LANGS:START -->

🌐 **Kendi dilinde oku:** [English](../README.md) · [Español](./README.es.md) · [Français](./README.fr.md) · [Português](./README.pt.md) · [Deutsch](./README.de.md) · [Italiano](./README.it.md) · [简体中文](./README.zh-CN.md) · [日本語](./README.ja.md) · [한국어](./README.ko.md) · [हिन्दी](./README.hi.md) · [العربية](./README.ar.md) · [Русский](./README.ru.md) · **Türkçe**

<!-- LANGS:END -->

[![Validate](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/validate-and-format.yml)
[![Deploy Knowledge Graph](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml/badge.svg)](https://github.com/mchittineni/ultimate-devops-guide/actions/workflows/knowledge-graph.yml)

<!-- BADGES:START -->

![Questions](https://img.shields.io/badge/questions-787-blue)
![Topics](https://img.shields.io/badge/topics-40-blueviolet)
![Difficulty](https://img.shields.io/badge/difficulty-🟢%20177%20·%20🟡%20394%20·%20🔴%20216-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

<!-- BADGES:END -->

[🌐 3B Bilgi Grafiği](https://mchittineni.github.io/ultimate-devops-guide/) · [📖 Çevrilmiş dersler](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/tr) · [📋 Tüm soruların dizini (İngilizce)](../README.md#-all-questions) · [🤝 Katkıda bulunma](../CONTRIBUTING.md)

⭐ İşi almanıza yardımcı olursa projeye yıldız verin.

</div>

> [!NOTE]
> **Esas alınan dil İngilizcedir.** Bu ana sayfa elle çevrilmiş ve depoya işlenmiştir. Dersler [`translations`](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n) dalında makine çevirisiyle çevrilir: [Türkçe okuyun](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/tr). Bir çeviri İngilizce orijinalle çelişirse doğru olan İngilizce orijinaldir.

---

## 🌐 3B Bilgi Grafiği

Tüm soruları ve konuları görsel olarak keşfedin: aralarındaki ilişkiler, konular arası kavramlar ve zorluk, alan ya da anahtar kelimeye göre canlı filtreler.

👉 **[Etkileşimli 3B bilgi grafiğini açın](https://mchittineni.github.io/ultimate-devops-guide/)**

---

## 🚀 Rolünüzü seçin

On üç yol; her biri bir link yığını değil, bir okuma sırası. Soldan başlayın ve sağa doğru ilerleyin.

> **Mülakata iki hafta mı kaldı?** [Interview Experience](../interview-experience/README.md) ile başlayın: mülakat turlarının yapısı, projenizi nasıl anlatacağınız, senaryo sorularıyla nasıl başa çıkacağınız ve gerçekten sorulanların bir kontrol listesi.

| 🎯 Hedef rol                  | Bu sırayla okuyun                                                                                                                                                                                                                                                                             |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Şu an mülakatlarda**        | [Interview Experience](../interview-experience/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Docker](../docker/README.md) → [Kubernetes](../kubernetes/README.md) → [IaC](../infrastructure-as-code/README.md)                 |
| **Junior / Associate DevOps** | [Core Concepts](../core-devops-concepts/README.md) → [Docker](../docker/README.md) → [Linux](../linux-administration/README.md) → [Version Control](../version-control/README.md) → [Scripting](../scripting-and-automation/README.md) → [CI/CD](../cicd/README.md)                           |
| **DevSecOps Mühendisi**       | [DevSecOps](../devsecops/README.md) → [Security & Compliance](../security-and-compliance/README.md) → [Network Security](../network-security/README.md) → [CI/CD](../cicd/README.md)                                                                                                          |
| **SecOps Mühendisi**          | [SecOps](../secops/README.md) → [Network Security](../network-security/README.md) → [Incident Management](../incident-management/README.md) → [Security & Compliance](../security-and-compliance/README.md)                                                                                   |
| **SRE Mühendisi**             | [SRE](../site-reliability-engineering/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Incident Management](../incident-management/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Metrics](../devops-metrics-and-kpis/README.md)          |
| **SLO Mühendisi**             | [SLO Engineering](../slo-engineering/README.md) → [SRE](../site-reliability-engineering/README.md) → [Infrastructure Monitoring](../infrastructure-monitoring/README.md) → [Monitoring & Logging](../monitoring-and-logging/README.md)                                                        |
| **SLA Mühendisi**             | [SLA Management](../sla-management/README.md) → [SLO Engineering](../slo-engineering/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md) → [Backup & DR](../backup-and-disaster-recovery/README.md)                                                               |
| **AWS Mühendisi**             | [AWS Engineering](../aws-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Azure Mühendisi**           | [Azure Engineering](../azure-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                 |
| **GCP Mühendisi**             | [GCP Engineering](../gcp-engineering/README.md) → [Cloud Engineering](../cloud-engineering/README.md) → [IaC](../infrastructure-as-code/README.md) → [Kubernetes](../kubernetes/README.md) → [Cost](../cloud-cost-optimization/README.md)                                                     |
| **Bulut Mühendisi**           | [Cloud Engineering](../cloud-engineering/README.md) → [Cloud Platforms](../cloud-platforms/README.md) → [IaC](../infrastructure-as-code/README.md) → [Cloud Migration](../cloud-migration/README.md) → [Scalability & HA](../scalability-and-high-availability/README.md)                     |
| **Platform Mühendisi**        | [Platform Engineering](../platform-engineering/README.md) → [Kubernetes](../kubernetes/README.md) → [Orchestration Advanced](../container-orchestration-advanced/README.md) → [Tools & Automation](../devops-tools-and-automation/README.md) → [Advanced](../advanced-devops-cloud/README.md) |
| **Senior / Lead**             | [Cloud Native](../cloud-native-architecture/README.md) → [Platform Engineering](../platform-engineering/README.md) → [Cost](../cloud-cost-optimization/README.md) → [Culture](../devops-culture-and-practices/README.md) → [Advanced](../advanced-devops-cloud/README.md)                     |

---

## 📚 Konulara ve sorulara göz atın

Tam dizin (her konu ve soru sayısı, konuya göre gruplanmış tüm sorular) [İngilizce README](../README.md#-all-questions) dosyasındadır. Her konu dizininin ve her dersin makine çevirisi [`translations` dalında](https://github.com/mchittineni/ultimate-devops-guide/tree/translations/i18n/tr) bulunur.

---

## 🧠 Yanıtların yapısı

Her yanıt aynı dört bölümü izler; bir bölümü derinlemesine ya da dördünü birden okuyabilirsiniz:

| Bölüm                                   | Size ne kazandırır                                                                       |
| --------------------------------------- | ---------------------------------------------------------------------------------------- |
| **Kısa cevap** (_Short answer_)         | Sesli söyleyebileceğiniz iki üç cümle. Buradan başlayın.                                 |
| **Ayrıntı** (_Detail_)                  | Özü: mekanizmalar, ödünleşimler ve deneyimi gösteren terimler.                           |
| **Örnek** (_Example_)                   | Çalıştırıp uyarlayabileceğiniz gerçek komutlar, YAML veya kod.                           |
| **Mülakat ipuçları** (_Interview tips_) | Takip soruları, yaygın tuzaklar ve güçlü bir yanıtı ezberlenmiş olandan ayıran noktalar. |

Zorluk 🟢 Başlangıç · 🟡 Orta · 🔴 İleri ile işaretlenir.

**Kullanmanın üç yolu:**

- **Belirli bir role hazırlanmak**: yukarıdaki tablodaki yolu izleyin ve her konunun sorularından önce README dosyasındaki "What interviewers probe here" bölümünü okuyun.
- **Genel tekrar**: bir konudaki kısa cevapları okuyun, yalnızca tereddüt ettiğiniz yerlerde derine inin.
- **Obsidian / not kasası**: her dosyada YAML frontmatter (`title`, `id`, `category`, `difficulty`, `tags`) bulunur; böylece deponun tamamı bir kasa olarak açılıp etiketlere göre gezilebilir.

---

## 🌍 Çeviriler hakkında

- **Bu sayfa** elle çevrilmiştir ve diğer değişiklikler gibi incelenir. Düzeltmeler `i18n/README.tr.md` dosyasına pull request olarak memnuniyetle karşılanır.
- **Dersler**, İngilizce içerik her değiştiğinde bir GitHub Actions iş akışı tarafından makine çevirisiyle çevrilir ve `translations` dalında yayımlanır. Kod, komutlar ve yapılandırma asla çevrilmez.
- **Bir dersi düzeltmek için** İngilizce orijinali iyileştirin: çeviri ondan otomatik olarak yeniden üretilir. `translations` dalında doğrudan yapılan değişikliklerin üzerine yazılır.
- **Diliniz yok mu?** Talep etmek için [bir issue açın](https://github.com/mchittineni/ultimate-devops-guide/issues/new).

---

## 🤝 Katkıda bulunma

Yeni sorular, daha iyi yanıtlar ve düzeltmeler memnuniyetle karşılanır; esas kaynak İngilizce olduğu için lütfen İngilizce yazın. [CONTRIBUTING.md](../CONTRIBUTING.md) dosya biçimini, adlandırma kurallarını ve pull request açmadan önce çalıştırılacak yerel kontrolleri anlatır. [Davranış Kuralları](../CODE_OF_CONDUCT.md) ve [Güvenlik Politikası](../SECURITY.md) temel kuralları belirler.

## 📄 Lisans

[MIT Lisansı](../LICENSE) ile yayımlanmıştır.
