"""
Self-Help Techniques
Evidence-based psychological first aid techniques.
Translated into all 9 supported languages.

References:
- WHO Psychological First Aid Guide (2011)
- IASC Guidelines on MHPSS in Emergency Settings (2007)
"""

from typing import Dict, List

BREATHING_EXERCISE: Dict[str, List[str]] = {
    "en": [
        "1. Find a comfortable position. You are safe right now.",
        "2. Breathe in slowly through your nose for 4 seconds.",
        "3. Hold your breath gently for 4 seconds.",
        "4. Breathe out slowly through your mouth for 6 seconds.",
        "5. Repeat 5 times. You are doing well.",
    ],
    "fa": [
        "۱. یک وضعیت راحت پیدا کنید. شما الان در امنیت هستید.",
        "۲. آرام از بینی نفس بکشید — ۴ ثانیه.",
        "۳. نفس خود را آرام نگه دارید — ۴ ثانیه.",
        "۴. آرام از دهان بازدم کنید — ۶ ثانیه.",
        "۵. ۵ بار تکرار کنید. شما خوب عمل می‌کنید.",
    ],
    "dar": [
        "۱. یک وضعیت آرام پیدا کنید. شما فعلاً امن هستید.",
        "۲. آهسته از بینی نفس بکشید — ۴ ثانیه.",
        "۳. نفس خود را آرام نگهدارید — ۴ ثانیه.",
        "۴. آهسته از دهان نفس بیرون بدهید — ۶ ثانیه.",
        "۵. ۵ بار تکرار کنید. شما خوب کار می‌کنید.",
    ],
    "ar": [
        "١. اجلس في وضع مريح. أنت بأمان الآن.",
        "٢. تنفس ببطء من أنفك لمدة ٤ ثوانِ.",
        "٣. احبس نفسك برفق لمدة ٤ ثوانِ.",
        "٤. أخرج الهواء ببطء من فمك لمدة ٦ ثوانِ.",
        "٥. كرر ٥ مرات. أنت تبلي حسناً.",
    ],
    "zh": [
        "1. 找一个舒适的姿势。你现在是安全的。",
        "2. 用鼻子慢慢吸气—4秒。",
        "3. 轻轻屏住呼吸—4秒。",
        "4. 用嘴慢慢呼气—6秒。",
        "5. 重复5次。你做得很好。",
    ],
    "fr": [
        "1. Trouvez une position confortable. Vous êtes en sécurité.",
        "2. Inspirez lentement par le nez pendant 4 secondes.",
        "3. Retenez doucement votre souffle pendant 4 secondes.",
        "4. Expirez lentement par la bouche pendant 6 secondes.",
        "5. Répétez 5 fois. Vous vous en sortez bien.",
    ],
    "es": [
        "1. Busca una posición cómoda. Estás a salvo ahora.",
        "2. Inhala lentamente por la nariz durante 4 segundos.",
        "3. Mantén la respiración suavemente durante 4 segundos.",
        "4. Exhala lentamente por la boca durante 6 segundos.",
        "5. Repite 5 veces. Lo estás haciendo bien.",
    ],
    "ru": [
        "1. Займите удобное положение. Сейчас вы в безопасности.",
        "2. Медленно вдохните через нос — 4 секунды.",
        "3. Задержите дыхание — 4 секунды.",
        "4. Медленно выдохните через рот — 6 секунд.",
        "5. Повторите 5 раз. Вы справляетесь.",
    ],
    "tr": [
        "1. Rahat bir pozisyon bulun. Şu anda güvendesiniz.",
        "2. Burnunuzdan yavaşça nefes alın — 4 saniye.",
        "3. Nefesinizi nazikçe tutun — 4 saniye.",
        "4. Ağzınızdan yavaşça nefes verin — 6 saniye.",
        "5. 5 kez tekrarlayın. İyi gidiyorsunuz.",
    ],
}

GROUNDING_5_4_3_2_1: Dict[str, str] = {
    "en": "Look around and find:\nU0001F590 5 things you can SEE\n✋ 4 things you can TOUCH\nU0001F442 3 things you can HEAR\nU0001F443 2 things you can SMELL\nU0001F445 1 thing you can TASTE\n\nTake your time. You are here. You are present.",
    "fa": "به اطرافتان نگاه کنید:\nU0001F590 ۵ چیز که می‌بینید\n✋ ۴ چیز که لمس می‌کنید\nU0001F442 ۳ صدا که می‌شنوید\nU0001F443 ۲ بو که حس می‌کنید\nU0001F445 ۱ مزه که حس می‌کنید\n\nعجله نکنید. شما اینجایید.",
    "dar": "به اطراف خود نگاه کنید:\nU0001F590 ۵ چیز\n✋ ۴ چیز\nU0001F442 ۳ صدا\nU0001F443 ۲ بو\nU0001F445 ۱ مزه\n\nآهسته باشید. شما اینجا هستید.",
    "ar": "انظر حولك وابحث عن:\nU0001F590 ٥ أشياء\n✋ ٤ أشياء\nU0001F442 ٣ أصوات\nU0001F443 شيئان\nU0001F445 شيء واحد\n\nخذ وقتك. أنت هنا. أنت حاضر.",
    "zh": "观察周围，找到：\nU0001F590 5样\n✋ 4样\nU0001F442 3种\nU0001F443 2种\nU0001F445 1种\n\n慢慢来。你在这里。你是安全的。",
    "fr": "Regardez autour de vous et trouvez :\nU0001F590 5 choses que vous pouvez VOIR\n✋ 4 choses que vous pouvez TOUCHER\nU0001F442 3 sons que vous pouvez ENTENDRE\nU0001F443 2 odeurs que vous pouvez SENTIR\nU0001F445 1 chose que vous pouvez GOÛTER\n\nPrenez votre temps. Vous êtes ici.",
    "es": "Mira a tu alrededor y encuentra:\nU0001F590 5 cosas que puedas VER\n✋ 4 cosas que puedas TOCAR\nU0001F442 3 sonidos que puedas OÍR\nU0001F443 2 olores que puedas OLER\nU0001F445 1 cosa que puedas SABOREAR\n\nTómate tu tiempo. Estás aquí. Estás presente.",
    "ru": "Осмотритесь и найдите:\nU0001F590 5 вещей\n✋ 4 вещи\nU0001F442 3 звука\nU0001F443 2 запаха\nU0001F445 1 вкус\n\nНе торопитесь. Вы здесь. Вы в безопасности.",
    "tr": "Etrafınıza bakın ve bulun:\nU0001F590 GÖREBİLECEĞİNİZ 5 şey\n✋ DOKUNABİLECEĞİNİZ 4 şey\nU0001F442 DUYABİLECEĞİNİZ 3 ses\nU0001F443 HİSSEDEBİLECEĞİNİZ 2 koku\nU0001F445 TADABİLECEĞİNİZ 1 tat\n\nAceleniz yok. Buradasinız.",
}


def get_breathing_exercise(language: str = "en") -> List[str]:
    """Get breathing exercise steps in the specified language."""
    return BREATHING_EXERCISE.get(language, BREATHING_EXERCISE["en"])

def get_grounding_exercise(language: str = "en") -> str:
    """Get 5-4-3-2-1 grounding technique in the specified language."""
    return GROUNDING_5_4_3_2_1.get(language, GROUNDING_5_4_3_2_1["en"])
