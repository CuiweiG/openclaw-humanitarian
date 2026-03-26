[English](README.md) | [فارسی](README.fa.md) | [العربية](README.ar.md) | [中文](README.zh.md) | [Français](README.fr.md) | **Español** | [Русский](README.ru.md)

---

# 🌍 OpenClaw — Red Humanitaria

**Boletines humanitarios multilingües impulsados por IA para civiles afectados por la crisis en Oriente Medio.**

[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://t.me/openclaw_aid_bot)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## El Problema

Cuando caen las bombas, la información es tan vital como el agua.

Millones de personas en Irán, Líbano y Siria viven en conflictos armados que se intensifican. Organizaciones como OCHA, PMA y ACNUR publican informes de situación cada día — pero estos informes son:

- **Redactados en inglés** — mientras que quienes más los necesitan hablan árabe, persa y dari
- **Publicados en sitios web** — inaccesibles para personas desplazadas con conexión móvil de bajo ancho de banda
- **Llenos de jerga técnica** — difícil de entender rápidamente incluso para angloparlantes

Resultado: una **brecha de información humanitaria** — los datos que salvan vidas existen, pero no llegan a quienes los necesitan.

### Los datos

- **600.000 a 1 millón** de hogares desplazados solo en Irán (ACNUR, marzo 2026)
- **33.000** refugiados afganos que reciben asistencia alimentaria del PMA en Irán
- **58.000+** retornados sirios y entradas al Líbano asistidos en puestos fronterizos
- Acceso humanitario **severamente restringido** en el sur del Líbano

Estas cifras provienen de informes que la mayoría de los civiles afectados nunca leerán.

---

## Lo Que Hacemos

Cerramos esta brecha con tres productos:

### 📡 Producto 1: Bot Humanitario Multilingüe (Telegram)
**Estado: En línea** ✅

Un bot de Telegram que difunde diariamente boletines humanitarios en **9 idiomas**: árabe, persa, dari, inglés, chino, turco, francés, español y ruso.

- Números de emergencia
- Actualizaciones de situación en tiempo real
- Orientación para donaciones (a organizaciones establecidas)
- Recursos de búsqueda de familias

👉 **Usar ahora:** [@openclaw_aid_bot](https://t.me/openclaw_aid_bot)

### 🏠 Producto 2: Localizador de Refugios en Tiempo Real (En desarrollo)
**Estado: En progreso** 🔧

Datos de refugios colaborativos → agregación IA → consultas instantáneas por Telegram.

### 🌐 Producto 3: Plataforma de Traducción de Datos Humanitarios
**Estado: Operativo** ✅

Pipeline automatizado que:
1. Escanea los últimos informes de ReliefWeb, OCHA y OMS
2. Extrae información clave
3. Traduce a boletines en persa, dari y árabe (máx. 200 palabras)
4. Publica el mismo día en Telegram

---

## Inicio Rápido

```bash
git clone https://github.com/CuiweiG/openclaw-humanitarian.git
cd openclaw-humanitarian
pip install -r requirements.txt
python src/demo.py  # Véalo funcionar en 30 segundos
```

---

## Productos

| Producto | Descripción |
|---------|-------------|
| 📡 **Scraper de Crisis** | Extrae automáticamente informes de situación de ReliefWeb, OCHA y agencias ONU cada 6 horas |
| 🌐 **Traductor Multilingüe** | Traducción por IA con glosario humanitario especializado (40+ términos verificados) |
| 🤖 **Bot de Telegram** | Distribuye boletines en AR / FA / DAR / ZH / TR / FR / ES / RU / EN bajo demanda y mediante alertas push |

---

## Hoja de Ruta

- [x] Boletines de crisis multilingüe (AR/FA/DAR/EN/ZH/TR)
- [x] Pipeline de extracción automática ReliefWeb/OCHA
- [x] Glosario humanitario de 40 términos (9 idiomas)
- [x] Bot de Telegram con soporte de 9 idiomas
- [ ] Rastreador de refugios en tiempo real para el Líbano
- [ ] Capa de comunicación offline Briar + Meshtastic
- [ ] Pasarela SMS para zonas con conectividad parcial
- [ ] Soporte de idiomas pastún y kurdo
- [ ] Extensión de navegador para traducción en línea de informes

---

## Contribuir

Damos la bienvenida a traductores, desarrolladores, trabajadores humanitarios y cualquier persona comprometida.

- 🐛 [Reportar un error](.github/ISSUE_TEMPLATE/bug_report.md)
- ✨ [Solicitar una función](.github/ISSUE_TEMPLATE/feature_request.md)
- 🌐 [Contribuir una traducción](.github/ISSUE_TEMPLATE/translation_request.md)
- 📖 Guía completa: [CONTRIBUTING.md](CONTRIBUTING.md)

Todos los niveles son bienvenidos. Si habla un idioma de zona de crisis y puede verificar traducciones, eso es más valioso que el código.

---

## No Aceptamos Donaciones

Este proyecto siempre será gratuito y abierto. Si desea ayudar económicamente, por favor done directamente a las organizaciones que salvan vidas sobre el terreno:

- 🔴 **CICR** — [icrc.org/es/donar](https://www.icrc.org/es/donar)
- 🔵 **ACNUR** — [donate.unhcr.org](https://donate.unhcr.org)
- ⚕️ **MSF / Médicos Sin Fronteras** — [msf.org/es/donar](https://www.msf.org/es/donar)

---

## Contacto

- 📧 Correo: [aid@agentmail.to](mailto:aid@agentmail.to)
- 🤖 Telegram: [@openclaw_aid_bot](https://t.me/openclaw_aid_bot)
- 🐛 Issues: [GitHub Issues](https://github.com/CuiweiG/openclaw-humanitarian/issues)

---

## Licencia

MIT — úselo, forkéelo, construya sobre él. Ver [LICENSE](LICENSE).

---

*Construido con urgencia. Cada estrella ayuda a que este proyecto llegue a alguien que lo necesita.*
