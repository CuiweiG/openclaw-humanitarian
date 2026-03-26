[English](README.md) | [فارسی](README.fa.md) | [العربية](README.ar.md) | [中文](README.zh.md) | **Français** | [Español](README.es.md) | [Русский](README.ru.md)

---

# 🌍 CrisisBridge — Réseau Humanitaire

**Bulletins humanitaires multilingues alimentés par l'IA pour les civils touchés par la crise au Moyen-Orient.**

[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://t.me/openclaw_aid_bot)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Le Problème

Quand les bombes tombent, l'information est aussi vitale que l'eau.

Des millions de personnes en Iran, au Liban et en Syrie vivent dans des conflits armés qui s'intensifient. Des organisations comme l'OCHA, le PAM et le HCR publient des rapports de situation chaque jour — mais ces rapports sont :

- **Rédigés en anglais** — alors que les personnes qui en ont le plus besoin parlent arabe, persan et dari
- **Publiés sur des sites web** — inaccessibles pour des déplacés avec une connexion mobile à faible débit
- **Remplis de jargon technique** — difficile à comprendre rapidement même pour les locuteurs anglophones

Résultat : un **fossé d'information humanitaire** — des données vitales existent, mais n'atteignent pas ceux qui en ont besoin.

### Les chiffres

- **600 000 à 1 million** de ménages déplacés rien qu'en Iran (HCR, mars 2026)
- **33 000** réfugiés afghans bénéficiant de l'aide alimentaire du PAM en Iran
- **58 000+** retournés syriens et entrées au Liban assistés aux postes frontière
- Accès humanitaire **sévèrement restreint** dans le sud du Liban

Ces chiffres proviennent de rapports que la plupart des civils concernés ne liront jamais.

---

## Ce Que Nous Faisons

Nous comblons ce fossé avec trois produits :

### 📡 Produit 1 : Bot Humanitaire Multilingue (Telegram)
**Statut : En ligne** ✅

Un bot Telegram qui diffuse quotidiennement des bulletins humanitaires en **9 langues** : arabe, persan, dari, anglais, chinois, turc, français, espagnol et russe.

- Numéros d'urgence
- Mises à jour de situation en temps réel
- Orientations pour les dons (vers des organisations établies)
- Ressources de recherche de famille

👉 **Utiliser maintenant :** [@openclaw_aid_bot](https://t.me/openclaw_aid_bot)

### 🏠 Produit 2 : Localisateur d'Abris en Temps Réel (En développement)
**Statut : En cours** 🔧

Données d'abris collaboratives → agrégation IA → requêtes instantanées via Telegram.

### 🌐 Produit 3 : Plateforme de Traduction de Données Humanitaires
**Statut : Opérationnel** ✅

Pipeline automatisé qui :
1. Scanne les derniers rapports de ReliefWeb, OCHA et WHO
2. Extrait les informations clés
3. Traduit en bulletins en persan, dari et arabe (200 mots max)
4. Publie le jour même sur Telegram

---

## Démarrage Rapide

```bash
git clone https://github.com/CuiweiG/openclaw-humanitarian.git
cd openclaw-humanitarian
pip install -r requirements.txt
python src/demo.py  # Voyez-le fonctionner en 30 secondes
```

---

## Produits

| Produit | Description |
|---------|-------------|
| 📡 **Scraper de Crise** | Récupère automatiquement les rapports de situation depuis ReliefWeb, OCHA et les agences ONU toutes les 6 heures |
| 🌐 **Traducteur Multilingue** | Traduction par IA avec glossaire humanitaire spécialisé (40+ termes vérifiés) |
| 🤖 **Bot Telegram** | Diffuse les bulletins en AR / FA / DAR / ZH / TR / FR / ES / RU / EN sur demande et via alertes push |

---

## Feuille de Route

- [x] Bulletins de crise multilingues (AR/FA/DAR/EN/ZH/TR/FR/ES/RU)
- [x] Pipeline d'extraction automatique ReliefWeb/OCHA
- [x] Glossaire humanitaire de 40 termes (9 langues)
- [x] Bot Telegram avec support 9 langues
- [ ] Suivi d'abris en temps réel pour le Liban
- [ ] Couche de communication hors ligne Briar + Meshtastic
- [ ] Passerelle SMS pour zones à connectivité partielle
- [ ] Support des langues pachto et kurde
- [ ] Extension navigateur pour traduction inline des rapports

---

## Contribuer

Nous accueillons traducteurs, développeurs, travailleurs humanitaires et toute personne engagée.

- 🐛 [Signaler un bug](.github/ISSUE_TEMPLATE/bug_report.md)
- ✨ [Demander une fonctionnalité](.github/ISSUE_TEMPLATE/feature_request.md)
- 🌐 [Contribuer une traduction](.github/ISSUE_TEMPLATE/translation_request.md)
- 📖 Guide complet : [CONTRIBUTING.md](CONTRIBUTING.md)

Tous niveaux bienvenus. Si vous parlez une langue de zone de crise et pouvez vérifier des traductions, c'est plus précieux que du code.

---

## Nous N'Acceptons Pas de Dons

Ce projet sera toujours gratuit et ouvert. Si vous souhaitez aider financièrement, veuillez donner directement aux organisations qui sauvent des vies sur le terrain :

- 🔴 **CICR** — [icrc.org/fr/faire-un-don](https://www.icrc.org/fr/faire-un-don)
- 🔵 **HCR** — [donate.unhcr.org](https://donate.unhcr.org)
- ⚕️ **MSF / Médecins Sans Frontières** — [msf.org/fr/faire-un-don](https://www.msf.org/fr/faire-un-don)

---

## Contact

- 📧 E-mail : [aid@agentmail.to](mailto:aid@agentmail.to)
- 🤖 Telegram : [@openclaw_aid_bot](https://t.me/openclaw_aid_bot)
- 🐛 Issues : [GitHub Issues](https://github.com/CuiweiG/openclaw-humanitarian/issues)

---

## Licence

MIT — utilisez-le, forkez-le, construisez dessus. Voir [LICENSE](LICENSE).

---

*Construit dans l'urgence. Chaque étoile aide ce projet à atteindre quelqu'un qui en a besoin.*
