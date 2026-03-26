"""
Document Protection Guide
Helps civilians protect and digitize critical documents during crisis.

Critical documents that should be backed up:
- Passport / National ID
- Birth certificates
- Marriage certificates
- Property deeds
- Medical records
"""

from typing import Dict, List

CRITICAL_DOCUMENTS = [
    "passport", "national_id", "birth_certificate",
    "marriage_certificate", "property_deed", "medical_records",
]

BACKUP_GUIDE: Dict[str, str] = {
    "en": """U0001f4cb Document Protection Guide

1. PHOTOGRAPH all important documents with your phone
2. STORE photos in a cloud service (Google Drive, iCloud)
3. EMAIL copies to a trusted family member abroad
4. KEEP originals in a waterproof bag
5. CARRY copies (not originals) when traveling
6. KNOW your document numbers by heart if possible

⚠️ If documents are lost: Contact your embassy or UNHCR for replacement guidance.""",

    "fa": """U0001f4cb راهنمای حفاظت از مدارک

۱. از تمام مدارک مهم با گوشی عکس بگیرید
۲. عکس‌ها را در فضای ابری ذخیره کنید
۳. کپی‌ها را به یک عضو خانواده مورد اعتماد ایمیل کنید
۴. اصل مدارک را در کیسه ضدآب نگه دارید
۵. هنگام سفر کپی حمل کنید نه اصل
۶. شماره مدارک خود را حفظ کنید

⚠️ در صورت گم شدن: با سفارت یا UNHCR تماس بگیرید.""",

    "ar": """U0001f4cb دليل حماية المستندات

١. صوِّر جميع المستندات المهمة بهاتفك
٢. خزِّن الصور في خدمة سحابية
٣. أرسل نسخاً إلى فرد موثوق من العائلة
٤. احفظ الأصول في حقيبة مقاومة للماء
٥. احمل نسخاً (لا الأصول) عند السفر
٦. احفظ أرقام مستنداتك غيباً

⚠️ في حالة الفقدان: تواصل مع سفارتك أو المفوضية السامية.""",
}

EMBASSY_DIRECTORY: Dict[str, List[dict]] = {
    "ir": [
        {"country": "Iran", "type": "UNHCR", "contact": "+98-21-8802-6814", "url": "https://www.unhcr.org/ir/"},
    ],
    "lb": [
        {"country": "Lebanon", "type": "UNHCR", "contact": "+961-1-849-201", "url": "https://www.unhcr.org/lb/"},
    ],
    "af": [
        {"country": "Afghanistan", "type": "UNHCR", "contact": "+93-20-210-1475", "url": "https://www.unhcr.org/af/"},
    ],
}


def get_backup_guide(language: str = "en") -> str:
    """Get document backup guide in specified language."""
    return BACKUP_GUIDE.get(language, BACKUP_GUIDE["en"])

def get_embassy_contacts(country_code: str) -> List[dict]:
    """Get UNHCR and embassy contacts for a country."""
    return EMBASSY_DIRECTORY.get(country_code.lower(), [])
