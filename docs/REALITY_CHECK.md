# بررسی وضعیت واقعی مخزن (ویرایش ۱.۰ · ۱۵ نوامبر ۲۰۲۶)

این فایل جای ادعاهای README را می‌گیرد: هر چیزی که اینجا نوشته شده با اجرا تأیید شده است.

## آنچه واقعاً وجود دارد

| بخش | وضعیت | شاهد |
|---|---|---|
| هسته تحلیلی `aurora/**` | بدون وابستگی زمان اجرا | `python -m unittest discover -s tests -t .` → **۷۰۷ تست سبز** |
| قرارداد هسته | ۸۸ عضو محافظت‌شده | `python -m aurora.core_contract` |
| کاتالوگ ابزار | ۳۳۵ ابزار، ۱۲ کلاس، ۲۰ بورس | `aurora/core/asset_universe.py` + `docs/catalogue.json` |
| تحلیل تکنیکال و بنیادی جدا | دو بسته مستقل + انتخاب‌گر | `aurora/analysis/technical/`, `aurora/analysis/fundamental/`, `aurora/analysis/combine.py` |
| موتور توصیه | رتبه‌بندی با دلیل و وتوی هزینه | `aurora/advisory/recommender.py` |
| آنبوردینگ و سبد مشتری | پرسشنامه، پروفایل، ترکیب، بازتوازن، اشتراک | `aurora/advice/onboarding.py`, `aurora/advice/holdings.py` |
| کش محلی کندل | SQLite، بدون تکرار | `aurora/data/data_cache.py` |
| تقویم و اخبار | RSS خالص + CSV + دروازه ریسک رویداد | `aurora/data/news_calendar.py` |
| روان‌سنجی و ربا-ادوایزر | ماژول‌ها هستند، **بدون آزمون** | `aurora/saas/` |
| لایه API وب | فایل `backend_api.py` هست، سرور اجرا نشده | `aurora/saas/backend_api.py` |

## آنچه وجود ندارد (و قبلاً README ادعا می‌کرد)

- پوشه `api/` با REST/WebSocket پیاده‌سازی‌شده وجود ندارد؛ تنها یک ماژول نمونه در `aurora/saas/` است.
- پل‌های بروکر (MT5، صرافی، TSETMC) به‌صورت کد اجرایی وجود ندارند؛ آنچه هست `aurora/execution/` با شبیه‌ساز، تیکت دستی، تطبیق و مسیریاب است.
- `aurora/risk/portfolio_risk.py` نه همبستگی محاسبه می‌کند نه VaR؛ فقط مواجهه، تعداد پوزیشن و افت باز را می‌سنجد. ریسک همبستگی در `aurora/portfolio/risk_budget.py` و بازپخش بحران در `aurora/portfolio/scenarios.py` است.

## مجوز

از این نسخه، مخزن با مجوز **MIT** منتشر می‌شود (فایل `LICENSE`). وابستگی‌های لایه SaaS در `requirements.txt` اعلام شده‌اند؛ هسته تحلیلی همچنان بدون وابستگی است.
