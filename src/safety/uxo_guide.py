"""
UXO (Unexploded Ordnance) Safety Education
Critical safety information for civilians in post-conflict areas.

Sources:
- HALO Trust safety guidelines
- LMAC (Lebanon Mine Action Center) public guides
- UNMAS (UN Mine Action Service) educational materials
"""

from typing import Dict

UXO_SAFETY_RULES: Dict[str, Dict[str, str]] = {
    "en": {
        "recognize": "⚠️ RECOGNIZE: Do not touch, pick up, or kick any unfamiliar metal objects. Unexploded ordnance can look like toys, pipes, or small containers.",
        "retreat": "U0001f6b6 RETREAT: Slowly walk back the way you came. Do not run. Avoid stepping on soft or disturbed ground.",
        "report": "U0001f4de REPORT: Immediately report the location to local authorities, mine action center, or Red Cross/Red Crescent.",
        "remember": "U0001f9e0 REMEMBER: If you didn't drop it, don't pick it up. Mark the area if possible and warn others.",
    },
    "fa": {
        "recognize": "⚠️ شناسایی: هیچ شیء فلزی ناآشنایی را لمس، بردارید یا لگد نزنید.",
        "retreat": "U0001f6b6 عقب‌نشینی: آرام از همان مسیر آمده برگردید. ندوید.",
        "report": "U0001f4de گزارش: فوراً محل را به مقامات محلی، مرکز مین‌زدایی یا هلال‌احمر گزارش دهید.",
        "remember": "U0001f9e0 یادآوری: اگر شما آن را نینداخته‌اید، برندارید.",
    },
    "dar": {
        "recognize": "⚠️ شناسایی: هیچ شیء فلزی ناآشنا را لمس، بردارید یا لگد نزنید.",
        "retreat": "U0001f6b6 عقب‌نشینی: آهسته از همان راهی که آمدید برگردید. ندوید.",
        "report": "U0001f4de گزارش: فوراً محل را به مقامات محلی یا سازمان ماین‌پاکی گزارش دهید.",
        "remember": "U0001f9e0 یادآوری: اگر شما نینداخته‌اید، برندارید.",
    },
    "ar": {
        "recognize": "⚠️ تعرَّف: لا تلمس أو تلتقط أي جسم معدني غير مألوف.",
        "retreat": "U0001f6b6 تراجَع: ارجع ببطء من نفس الطريق. لا تركض.",
        "report": "U0001f4de أبلِغ: أبلغ فوراً السلطات المحلية أو مركز الألغام أو الصليب الأحمر.",
        "remember": "U0001f9e0 تذكَّر: إذا لم تُسقطه أنت، فلا تلتقطه.",
    },
    "zh": {
        "recognize": "⚠️ 识别：不要触摸、拣起或踢任何不明金属物体。未爆弹药可能看起来像玩具。",
        "retreat": "U0001f6b6 撤退：沿来时的路慢慢走回去。不要跌。",
        "report": "U0001f4de 报告：立即向当地排雷组织或红十字会报告位置。",
        "remember": "U0001f9e0 记住：如果不是你丢的，就不要捡。",
    },
    "fr": {
        "recognize": "⚠️ IDENTIFIER : Ne touchez pas d'objets métalliques inconnus. Les munitions non explosées peuvent ressembler à des jouets.",
        "retreat": "U0001f6b6 RECULER : Revenez lentement par le même chemin. Ne courez pas.",
        "report": "U0001f4de SIGNALER : Signalez immédiatement aux autorités locales ou à la Croix-Rouge.",
        "remember": "U0001f9e0 RETENIR : Si vous ne l'avez pas posé, ne le ramassez pas.",
    },
    "es": {
        "recognize": "⚠️ RECONOCER: No toque objetos metálicos desconocidos. Las municiones sin explotar pueden parecer juguetes.",
        "retreat": "U0001f6b6 RETIRARSE: Regrese lentamente por el mismo camino. No corra.",
        "report": "U0001f4de REPORTAR: Informe inmediatamente a las autoridades locales o a la Cruz Roja.",
        "remember": "U0001f9e0 RECORDAR: Si usted no lo dejó ahí, no lo recoja.",
    },
    "ru": {
        "recognize": "⚠️ ОПРЕДЕЛИТЬ: Не трогайте незнакомые металлические предметы.",
        "retreat": "U0001f6b6 ОТОЙТИ: Медленно вернитесь тем же путём. Не бегите.",
        "report": "U0001f4de СООБЩИТЬ: Немедленно сообщите местным властям или Красному Кресту.",
        "remember": "U0001f9e0 ПОМНИТЬ: Если вы это не бросали — не поднимайте.",
    },
    "tr": {
        "recognize": "⚠️ TANI: Tanımadığınız metal nesnelere dokunmayın. Patlamamlş mühimmat oyuncak gibi görünebilir.",
        "retreat": "U0001f6b6 GERİ ÇEKİL: Geldiğiniz yoldan yavaşça geri dönün. Koşmayın.",
        "report": "U0001f4de BİLDİR: Durumu derhal yerel makamlara veya Kızılhaç'a bildirin.",
        "remember": "U0001f9e0 HATIRLA: Siz bırakmadıysanız, almayın.",
    },
}

DEMINING_CONTACTS: Dict[str, dict] = {
    "ir": {"org": "IRAMAC (Iran Mine Action Center)", "contact": "Via local authorities"},
    "lb": {"org": "LMAC (Lebanon Mine Action Center)", "contact": "+961-5-927-170", "url": "http://www.lebmac.org"},
    "af": {"org": "DMAC (Afghanistan Mine Action)", "contact": "+93-20-210-3442"},
    "sy": {"org": "Via UNMAS Syria", "contact": "unmas-syria@un.org"},
    "international": {"org": "HALO Trust", "url": "https://www.halotrust.org", "contact": "info@halotrust.org"},
}


def get_uxo_guide(language: str = "en") -> Dict[str, str]:
    """Get UXO safety rules in the specified language."""
    return UXO_SAFETY_RULES.get(language, UXO_SAFETY_RULES["en"])

def get_demining_contact(country_code: str) -> dict:
    """Get the local demining organization contact."""
    return DEMINING_CONTACTS.get(country_code.lower(), DEMINING_CONTACTS["international"])
