# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import time
import re
import json
from datetime import datetime
from telegram import Bot
import asyncio

# ===================== إعداداتك =====================
TOKEN = "8084220581:AAGq85Jf-Uu5ayszUdoFFx6OXHtfQzyeCdU"
CHAT_ID = "7842518434"
STATE_FILE = "processed_ids.json"

# الكوكيز الجديدة اللي أنت لسه باعتها
RAW_COOKIE = "XSRF-TOKEN=eyJpdiI6Im90OGJDeVkyTW1VZy9MNE5BaFN4YUE9PSIsInZhbHVlIjoiWDBkTzdEMnA0VVN0RmxiZWtIU3M3VG1TS3lyYzZWOXJZaUJWaHNUYkFQQWxwaEJvVDhERXZqVVBoSWdGQ085NFhKcHZ0bFhoL1l5bkhydnBlQVhMWFBTSkkvQnVIbkVYTmkvalh5MkpvS1BSVG4rNWRmZjlJZzJwbTJYZ240aDMiLCJtYWMiOiI5MTUwMzIyYTEyMTY3OWE1MGM4OWI0ZDI4NzEyNjk3ODIzOTVjZDg0YzZkNjE5MzU0ZTYzMGRhYzI4ODlmYWZlIiwidGFnIjoiIn0%3D; ivas_sms_session=eyJpdiI6IlozUG1CWXRsd2NQVzJhcUxmU1l5ZlE9PSIsInZhbHVlIjoicGphZ0dKWUlYL0kyL2dOcHFCU2E3Mmk2ZDBGWFl0dFBaeGpUMThPRjdqVEpzeHlaTElsRnhVNEw1U1Z4QVlmNWhOK1JQT0VJL1M4N2hwY1k2TVA3alBxODBUcE9WcnNNYzNpN2RhN01hTkxEa2VUQ215SkNSemZLa1ZCOTBDZUQiLCJtYWMiOiIyZDJhYzVlNmUxMGZiMmQyNGIwZjQwN2EzYzBjMDU1MTMyY2Q1NmVhYzkxNTY2OTBlM2FmZTY4NjAzZmFiZDAyIiwidGFnIjoiIn0%3D"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Cookie': RAW_COOKIE,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive'
}

bot = Bot(token=TOKEN)

def extract_otp(text):
    whatsapp_style = re.search(r'(\d{3})[-\s](\d{3})', text)
    if whatsapp_style:
        return f"‎{whatsapp_style.group(2)}{whatsapp_style.group(1)}"
    all_potential = re.findall(r'\b\d{4,8}\b', text)
    return f"‎{all_potential[0]}" if all_potential else "N/A"

def get_old_ids():
    if os.path.exists(STATE_FILE):
        try: return set(json.load(open(STATE_FILE)))
        except: return set()
    return set()

async def run_bot():
    processed = set()
    print("🚀 البوت الخفيف بدأ العمل الآن...")
    
    while True:
        try:
            response = requests.get("https://www.ivasms.com/portal/live/my_sms", headers=HEADERS, timeout=15)
            
            # لو الكوكيز انتهت، هيرجعك لصفحة اللوجن
            if "login" in response.url.lower():
                print("❌ انتهت صلاحية الكوكيز! يرجى تحديثها.")
                await bot.send_message(CHAT_ID, "⚠️ الكوكيز ماتت يا فارس، هات واحدة جديدة!")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.find_all('tr')
            
            for row in reversed(rows):
                cols = row.find_all('td')
                if len(cols) >= 5:
                    phone = cols[0].get_text(strip=True)
                    if not phone or "المرسل" in phone: continue
                    
                    service = cols[1].get_text(strip=True)
                    msg_content = cols[4].get_text(strip=True)
                    uid = f"{phone}_{msg_content[-15:]}"

                    if uid not in processed:
                        otp = extract_otp(msg_content)
                        report = (
                            f"✨ <b>OTP Received</b> ✨\n\n"
                            f"📞 <b>Number:</b> <code>{phone}</code>\n"
                            f"⚙️ <b>Service:</b> {service}\n"
                            f"🔑 <b>OTP:</b> <code>{otp}</code>\n"
                            f"📝 <b>Message:</b> {msg_content}"
                        )
                        await bot.send_message(chat_id=CHAT_ID, text=report, parse_mode='HTML')
                        processed.add(uid)
                        print(f"✅ تم إرسال كود لـ {phone}")

        except Exception as e:
            print(f"⚠️ خطأ: {e}")
        
        await asyncio.sleep(2) # فحص كل ثانيتين

if __name__ == "__main__":
    import os
    asyncio.run(run_bot())