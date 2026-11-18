"""Enterprise Localization & Multi-Language Core for Aurora Quant Platform.
Supports: FA, EN, AR, TR, ES, RU.
"""
from __future__ import annotations
from typing import Dict, Any

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "fa": {
        "dashboard": "داشبورد مدیریت ثروت",
        "psych": "تست روانشناسی و ریسک",
        "smc": "تحلیل اسمارت‌مانی و تکنیکال",
        "robo": "سبدگردان هوشمند (Robo-Advisor)",
        "stress": "سناریوی بحران (Aladdin Engine)",
        "vault": "گاوصندوق امنیتی و 2FA",
        "aav_label": "ارزش خالص دارایی‌ها (AAV)",
        "rebalance_btn": "اجرای خودکار بازتوزیع پرتفوی"
    },
    "en": {
        "dashboard": "Wealth Dashboard",
        "psych": "Psychometric & Risk Test",
        "smc": "Smart Money & Technical Analysis",
        "robo": "Robo-Advisor Rebalancing",
        "stress": "Stress Test (Aladdin Engine)",
        "vault": "Security Vault & 2FA",
        "aav_label": "Net Asset Value (AAV)",
        "rebalance_btn": "Execute Auto-Rebalance"
    },
    "ru": {
        "dashboard": "Панель управления благосостоянием",
        "psych": "Психометрический тест риска",
        "smc": "Smart Money и Технический анализ",
        "robo": "Робо-Советник (Резерв)",
        "stress": "Стресс-тест (Aladdin)",
        "vault": "Хранилище безопасности и 2FA",
        "aav_label": "Чистая стоимость активов (AAV)",
        "rebalance_btn": "Выполнить ребалансировку"
    },
    "ar": {
        "dashboard": "لوحة تحكم الثروة",
        "psych": "اختبار السلوك والمخاطر",
        "smc": "تحليل الأموال الذكية",
        "robo": "المستشار الآلي",
        "stress": "اختبار الإجهاد",
        "vault": "خزنة الأمان"
    },
    "tr": {
        "dashboard": "Varlık Paneli",
        "psych": "Psikometrik Risk Testi",
        "smc": "Akıllı Para Analizi",
        "robo": "Robot Danışman",
        "stress": "Stres Testi",
        "vault": "Güvenlik Kasası"
    },
    "es": {
        "dashboard": "Panel de Riqueza",
        "psych": "Test Psicométrico",
        "smc": "Dinero Inteligente",
        "robo": "Robo-Asesor",
        "stress": "Prueba de Estrés",
        "vault": "Bóveda"
    }
}

class LocalizationEngine:
    @staticmethod
    def get_text(lang: str, key: str) -> str:
        return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
