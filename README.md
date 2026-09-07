# EduNova murojaat boti

Bot kanalga majburiy obunani tekshiradi va foydalanuvchining taklif yoki murojaatini admin `7180980386` ga yuboradi.

## O'rnatish

1. Telegram'da `@BotFather` orqali bot yarating va token oling.
2. Botni `@edunova_maktabi` kanaliga administrator sifatida qo'shing. Bu `get_chat_member` orqali obunani tekshirish uchun kerak.
3. Python 3.10 yoki undan yangi versiyasini o'rnating.
4. Virtual muhit yarating va kutubxonalarni o'rnating:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

5. `.env.example` faylidan `.env` nusxa yarating va `BOT_TOKEN` qiymatini kiriting:

```powershell
Copy-Item .env.example .env
```

6. Botni ishga tushiring:

```powershell
python bot.py
```

## Vercel'ga deploy qilish

Vercel `api/index.py` webhook endpointini avtomatik serverless function sifatida ishga tushiradi. Project Settings > Environment Variables bo'limida quyidagi qiymatlarni Production, Preview va Development uchun qo'shing:

- `BOT_TOKEN`
- `ADMIN_IDS` (masalan, `7180980386`)
- `CHANNEL_USERNAME`
- `CHANNEL_URL`

Deploy tugagach, Telegram webhook'ini Vercel URL'iga ulang:

```powershell
curl "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://<VERCEL-DOMAIN>/api"
```

Webhook holatini tekshirish:

```powershell
curl "https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo"
```

Vercel serverless muhitida `python bot.py` orqali polling ishga tushirilmaydi.

## Ishlash tartibi

- Foydalanuvchi `/start` yuboradi.
- Bot kanalga obunani tekshiradi.
- Obuna tasdiqlangach, foydalanuvchi taklif yoki murojaat turini tanlaydi.
- Yuborilgan matn admin ID `7180980386` ga foydalanuvchi ma'lumotlari bilan jo'natiladi.
