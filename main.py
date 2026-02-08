#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OTP Telegram Bot - Railway.app Deployment Version
Optimized for cloud deployment with automatic restarts
"""

import requests
import time
import re
from datetime import datetime
import json
import os
import sys

# ==================== CONFIGURATION ====================
# Environment variables se config (Railway par set karenge)
API_URL = os.getenv("API_URL", "http://51.77.216.195/crapi/dgroup/viewstats")
API_TOKEN = os.getenv("API_TOKEN", "RVBXRjRSQouDZnhDQZBYSWdqj2tZlWp7VnFUf3hSdVeEjXV1gGeP")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8430484880:AAEDwu_Rf6-E25d4DdCSOYTqvEhcoCf8ga0")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "-1003852492977")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "15"))  # seconds

# Track processed messages to avoid duplicates
processed_messages = set()

# ==================== EXTENSIVE COUNTRY MAPPING ====================
COUNTRY_DATA = {
    # Americas
    "1": {"flag": "🇺🇸", "name": "USA/Canada"},
    "52": {"flag": "🇲🇽", "name": "Mexico"},
    "54": {"flag": "🇦🇷", "name": "Argentina"},
    "55": {"flag": "🇧🇷", "name": "Brazil"},
    "56": {"flag": "🇨🇱", "name": "Chile"},
    "57": {"flag": "🇨🇴", "name": "Colombia"},
    "58": {"flag": "🇻🇪", "name": "Venezuela"},
    "51": {"flag": "🇵🇪", "name": "Peru"},
    "53": {"flag": "🇨🇺", "name": "Cuba"},
    "591": {"flag": "🇧🇴", "name": "Bolivia"},
    "593": {"flag": "🇪🇨", "name": "Ecuador"},
    "595": {"flag": "🇵🇾", "name": "Paraguay"},
    "598": {"flag": "🇺🇾", "name": "Uruguay"},
    
    # Europe
    "44": {"flag": "🇬🇧", "name": "United Kingdom"},
    "33": {"flag": "🇫🇷", "name": "France"},
    "49": {"flag": "🇩🇪", "name": "Germany"},
    "39": {"flag": "🇮🇹", "name": "Italy"},
    "34": {"flag": "🇪🇸", "name": "Spain"},
    "7": {"flag": "🇷🇺", "name": "Russia"},
    "48": {"flag": "🇵🇱", "name": "Poland"},
    "31": {"flag": "🇳🇱", "name": "Netherlands"},
    "32": {"flag": "🇧🇪", "name": "Belgium"},
    "41": {"flag": "🇨🇭", "name": "Switzerland"},
    "43": {"flag": "🇦🇹", "name": "Austria"},
    "45": {"flag": "🇩🇰", "name": "Denmark"},
    "46": {"flag": "🇸🇪", "name": "Sweden"},
    "47": {"flag": "🇳🇴", "name": "Norway"},
    "358": {"flag": "🇫🇮", "name": "Finland"},
    "30": {"flag": "🇬🇷", "name": "Greece"},
    "351": {"flag": "🇵🇹", "name": "Portugal"},
    "353": {"flag": "🇮🇪", "name": "Ireland"},
    "420": {"flag": "🇨🇿", "name": "Czech Republic"},
    "36": {"flag": "🇭🇺", "name": "Hungary"},
    "40": {"flag": "🇷🇴", "name": "Romania"},
    "380": {"flag": "🇺🇦", "name": "Ukraine"},
    "90": {"flag": "🇹🇷", "name": "Turkey"},
    
    # Asia
    "86": {"flag": "🇨🇳", "name": "China"},
    "91": {"flag": "🇮🇳", "name": "India"},
    "92": {"flag": "🇵🇰", "name": "Pakistan"},
    "81": {"flag": "🇯🇵", "name": "Japan"},
    "82": {"flag": "🇰🇷", "name": "South Korea"},
    "84": {"flag": "🇻🇳", "name": "Vietnam"},
    "66": {"flag": "🇹🇭", "name": "Thailand"},
    "62": {"flag": "🇮🇩", "name": "Indonesia"},
    "60": {"flag": "🇲🇾", "name": "Malaysia"},
    "63": {"flag": "🇵🇭", "name": "Philippines"},
    "65": {"flag": "🇸🇬", "name": "Singapore"},
    "880": {"flag": "🇧🇩", "name": "Bangladesh"},
    "94": {"flag": "🇱🇰", "name": "Sri Lanka"},
    "95": {"flag": "🇲🇲", "name": "Myanmar"},
    "855": {"flag": "🇰🇭", "name": "Cambodia"},
    "856": {"flag": "🇱🇦", "name": "Laos"},
    "93": {"flag": "🇦🇫", "name": "Afghanistan"},
    "98": {"flag": "🇮🇷", "name": "Iran"},
    "964": {"flag": "🇮🇶", "name": "Iraq"},
    "972": {"flag": "🇮🇱", "name": "Israel"},
    "966": {"flag": "🇸🇦", "name": "Saudi Arabia"},
    "971": {"flag": "🇦🇪", "name": "UAE"},
    "974": {"flag": "🇶🇦", "name": "Qatar"},
    "965": {"flag": "🇰🇼", "name": "Kuwait"},
    "968": {"flag": "🇴🇲", "name": "Oman"},
    "973": {"flag": "🇧🇭", "name": "Bahrain"},
    "962": {"flag": "🇯🇴", "name": "Jordan"},
    "961": {"flag": "🇱🇧", "name": "Lebanon"},
    "963": {"flag": "🇸🇾", "name": "Syria"},
    "967": {"flag": "🇾🇪", "name": "Yemen"},
    "996": {"flag": "🇰🇬", "name": "Kyrgyzstan"},
    "998": {"flag": "🇺🇿", "name": "Uzbekistan"},
    "992": {"flag": "🇹🇯", "name": "Tajikistan"},
    "993": {"flag": "🇹🇲", "name": "Turkmenistan"},
    "994": {"flag": "🇦🇿", "name": "Azerbaijan"},
    "995": {"flag": "🇬🇪", "name": "Georgia"},
    "374": {"flag": "🇦🇲", "name": "Armenia"},
    "977": {"flag": "🇳🇵", "name": "Nepal"},
    
    # Africa
    "20": {"flag": "🇪🇬", "name": "Egypt"},
    "27": {"flag": "🇿🇦", "name": "South Africa"},
    "234": {"flag": "🇳🇬", "name": "Nigeria"},
    "233": {"flag": "🇬🇭", "name": "Ghana"},
    "254": {"flag": "🇰🇪", "name": "Kenya"},
    "255": {"flag": "🇹🇿", "name": "Tanzania"},
    "256": {"flag": "🇺🇬", "name": "Uganda"},
    "251": {"flag": "🇪🇹", "name": "Ethiopia"},
    "212": {"flag": "🇲🇦", "name": "Morocco"},
    "213": {"flag": "🇩🇿", "name": "Algeria"},
    "216": {"flag": "🇹🇳", "name": "Tunisia"},
    "218": {"flag": "🇱🇾", "name": "Libya"},
    "221": {"flag": "🇸🇳", "name": "Senegal"},
    "225": {"flag": "🇨🇮", "name": "Ivory Coast"},
    "237": {"flag": "🇨🇲", "name": "Cameroon"},
    "243": {"flag": "🇨🇩", "name": "DR Congo"},
    "244": {"flag": "🇦🇴", "name": "Angola"},
    "258": {"flag": "🇲🇿", "name": "Mozambique"},
    "260": {"flag": "🇿🇲", "name": "Zambia"},
    "263": {"flag": "🇿🇼", "name": "Zimbabwe"},
    
    # Oceania
    "61": {"flag": "🇦🇺", "name": "Australia"},
    "64": {"flag": "🇳🇿", "name": "New Zealand"},
    "679": {"flag": "🇫🇯", "name": "Fiji"},
}

# ==================== SERVICE NAME MAPPING ====================
SERVICE_NAMES = {
    "whatsapp": "WhatsApp", "facebook": "Facebook", "instagram": "Instagram",
    "snapchat": "Snapchat", "twitter": "Twitter", "tiktok": "TikTok",
    "telegram": "Telegram", "linkedin": "LinkedIn", "discord": "Discord",
    "viber": "Viber", "wechat": "WeChat", "line": "LINE", "kakaotalk": "KakaoTalk",
    "google": "Google", "microsoft": "Microsoft", "apple": "Apple",
    "yahoo": "Yahoo", "amazon": "Amazon", "uber": "Uber", "netflix": "Netflix",
    "paypal": "PayPal", "grab": "Grab", "gojek": "GoJek", "olx": "OLX",
    "steam": "Steam", "roblox": "Roblox", "naver": "Naver",
    "verify": "Verification Service", "otp": "OTP Service",
}

def get_country_info(phone_number):
    """Extract country flag and name from phone number"""
    phone_str = str(phone_number).strip()
    
    # Check for 3-digit country codes first
    for code in ["880", "420", "855", "856", "591", "593", "595", "598", "358", "351", "353", "380", "374", "234", "233", "254", "255", "256", "251", "212", "213", "216", "218", "221", "225", "237", "243", "244", "258", "260", "263", "961", "962", "963", "964", "965", "966", "967", "968", "971", "972", "973", "974", "992", "993", "994", "995", "996", "998", "977", "679"]:
        if phone_str.startswith(code):
            return COUNTRY_DATA[code]["flag"], COUNTRY_DATA[code]["name"]
    
    prefix = phone_str[:2]
    if prefix in COUNTRY_DATA:
        return COUNTRY_DATA[prefix]["flag"], COUNTRY_DATA[prefix]["name"]
    
    prefix = phone_str[:1]
    if prefix in COUNTRY_DATA:
        return COUNTRY_DATA[prefix]["flag"], COUNTRY_DATA[prefix]["name"]
    
    return "🌍", "Unknown"

def get_service_name(cli):
    """Get proper service name from CLI"""
    if not cli:
        return "Unknown Service"
    
    cli_lower = cli.lower().strip()
    for key, value in SERVICE_NAMES.items():
        if key in cli_lower:
            return value
    
    return cli.title()

def extract_otp(message):
    """Extract OTP code from message"""
    match = re.search(r'\b(\d{6})\b', message)
    if match:
        return match.group(1)
    
    match = re.search(r'\b(\d{3}-\d{3})\b', message)
    if match:
        return match.group(1)
    
    match = re.search(r'\b(\d{2}-\d{3})\b', message)
    if match:
        return match.group(1)
    
    match = re.search(r'\b(\d{4,6})\b', message)
    if match:
        return match.group(1)
    
    return "N/A"

def mask_phone_number(phone):
    """Mask middle digits of phone number"""
    phone_str = str(phone)
    if len(phone_str) <= 4:
        return phone_str
    return f"{phone_str[:4]}****{phone_str[-3:]}"

def format_telegram_message(data):
    """Format data into beautiful Telegram message"""
    dt = data.get('dt', '')
    num = data.get('num', '')
    cli = data.get('cli', 'Unknown')
    message = data.get('message', '').strip()
    
    flag, country = get_country_info(num)
    service = get_service_name(cli)
    otp = extract_otp(message)
    masked_num = mask_phone_number(num)
    
    telegram_msg = f"""✨    <b>NEW  OTP   RECEIVED</b>    ✨

━━━━━━━━━━━━━━━━━━━━━━━━━━

🕐 <b>Time:</b> <code>{dt}</code>

{flag} <b>Country:</b> {country}

🟢 <b>Service:</b> {service}

📞 <b>Number:</b> <code>+{masked_num}</code>

🔑 <b>OTP:</b> <code>{otp}</code>

━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 <b>Full Message:</b>

<pre>{message}</pre>

━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Powered By Power Modz</b>"""
    
    return telegram_msg, otp

def send_telegram_message(message, otp_code):
    """Send message to Telegram channel"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    keyboard = {
        "inline_keyboard": [[{
            "text": f"📋 Copy OTP: {otp_code}",
            "callback_data": f"copy_{otp_code}"
        }]]
    }
    
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(keyboard)
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ Message sent successfully! OTP: {otp_code}")
            return True
        else:
            print(f"❌ Failed to send message: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def fetch_api_data():
    """Fetch data from API"""
    params = {"token": API_TOKEN, "records": 10}
    
    try:
        response = requests.get(API_URL, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data.get('data', [])
            else:
                print(f"⚠️ API Error: {data.get('msg', 'Unknown error')}")
                return []
        else:
            print(f"⚠️ HTTP Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching API: {e}")
        return []

def create_message_id(data):
    """Create unique ID for message to track duplicates"""
    return f"{data['dt']}_{data['num']}_{data['cli']}"

def health_check():
    """Send a test message to verify bot is working"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✅ Bot connected: @{bot_info['result']['username']}")
            return True
        return False
    except:
        return False

def main():
    """Main function to run the bot"""
    print("=" * 60)
    print("🚀 OTP TELEGRAM BOT - RAILWAY DEPLOYMENT")
    print("=" * 60)
    print(f"📡 Checking API every {CHECK_INTERVAL} seconds...")
    print(f"📢 Sending to Channel: {TELEGRAM_CHANNEL_ID}")
    print(f"🌍 Supporting 100+ countries with auto-detect")
    print(f"🎯 Auto service name detection enabled")
    print(f"☁️  Running on Railway.app (No restrictions!)")
    print("=" * 60)
    
    # Health check
    if health_check():
        print("✅ Telegram connection verified!")
    else:
        print("⚠️ Warning: Could not verify Telegram connection")
    
    print()
    
    while True:
        try:
            records = fetch_api_data()
            
            if records:
                print(f"📥 Fetched {len(records)} records from API")
                
                new_count = 0
                duplicate_count = 0
                
                for record in records:
                    msg_id = create_message_id(record)
                    
                    if msg_id not in processed_messages:
                        telegram_msg, otp = format_telegram_message(record)
                        
                        if send_telegram_message(telegram_msg, otp):
                            processed_messages.add(msg_id)
                            new_count += 1
                            
                            if len(processed_messages) > 1000:
                                processed_messages.pop()
                        
                        time.sleep(1)
                    else:
                        duplicate_count += 1
                
                if duplicate_count > 0:
                    print(f"⏭️ Skipped {duplicate_count} duplicate messages")
                
                if new_count > 0:
                    print(f"✨ Sent {new_count} new OTP(s) to Telegram")
                    
            else:
                print("📭 No new records found")
            
            print(f"⏳ Waiting {CHECK_INTERVAL} seconds...\n")
            sys.stdout.flush()  # Force flush output for Railway logs
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n" + "=" * 60)
            print("🛑 Bot stopped by user")
            print("=" * 60)
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print(f"🔄 Retrying in {CHECK_INTERVAL} seconds...")
            sys.stdout.flush()
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
