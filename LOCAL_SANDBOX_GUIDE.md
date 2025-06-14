# 🐳 Локальная песочница Neo AI

## 🎯 Что это такое?

Локальная песочница - это **бесплатная альтернатива Daytona**, которая работает на вашем компьютере через Docker. Она предоставляет те же возможности:

- ✅ **Выполнение кода** (Python, JavaScript, Bash)
- ✅ **Браузерная автоматизация** (Playwright + Chrome)
- ✅ **Скриншоты веб-страниц**
- ✅ **Файловые операции**
- ✅ **Графический интерфейс** (VNC/noVNC)

## 🚀 Преимущества локальной песочницы

| Локальная | Daytona (облако) |
|-----------|------------------|
| ✅ **Бесплатно** | 💰 Платно |
| ✅ **Приватность** | ⚠️ Данные в облаке |
| ✅ **Быстрый доступ** | 🌐 Зависит от интернета |
| ✅ **Полный контроль** | 🔒 Ограничения провайдера |
| ⚠️ Требует Docker | ✅ Готово к использованию |

## 📋 Требования

1. **Docker Desktop** установлен и запущен
2. **4GB+ RAM** для контейнера
3. **2GB+ свободного места** на диске

## ⚙️ Настройка

### 1. Установка Docker

#### Windows/Mac:
```bash
# Скачать Docker Desktop с https://docker.com
# Установить и запустить
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER
```

### 2. Настройка Neo AI для локальной песочницы

Отредактируйте `backend/.env`:

```bash
# Вариант 1: Принудительно использовать локальную песочницу
SANDBOX_MODE=local

# Вариант 2: Автоматический выбор (локальная, если нет Daytona)
SANDBOX_MODE=auto

# Вариант 3: Убрать Daytona API ключ (автофоллбэк на локальную)
# DAYTONA_API_KEY=
```

## 🧪 Тестирование

Запустите тест локальной песочницы:

```bash
cd /workspace/neo
python test_local_sandbox.py
```

Ожидаемый результат:
```
🧪 Testing Local Docker Sandbox
==================================================
1. Checking Docker availability...
✅ Docker is available
2. Building sandbox image...
✅ Sandbox image built successfully
3. Creating sandbox container...
✅ Sandbox created: neo-sandbox-abc123
4. Getting container information...
✅ Container status: running
   noVNC URL: http://localhost:32768
   VNC Port: 32769
5. Testing Python code execution...
✅ Python code executed successfully
   Output: Hello from local sandbox!
4
6. Testing JavaScript code execution...
✅ JavaScript code executed successfully
   Output: Hello from Node.js!
4
7. Testing screenshot functionality...
✅ Screenshot taken successfully
   Format: base64_png
   Data length: 15234 characters
8. Cleaning up...
✅ Sandbox cleaned up successfully
==================================================
🎉 Local sandbox test completed!
```

## 🔧 Использование

### В коде Neo AI:

```python
from backend.sandbox.hybrid_sandbox import hybrid_sandbox

# Проверить статус
status = hybrid_sandbox.get_status()
print(f"Режим песочницы: {status['preferred_mode']}")

# Создать песочницу
sandbox = hybrid_sandbox.create_sandbox()

# Выполнить код
result = hybrid_sandbox.execute_code(
    sandbox['id'], 
    "print('Hello World!')", 
    "python"
)

# Сделать скриншот
screenshot = hybrid_sandbox.take_screenshot(
    sandbox['id'], 
    "https://example.com"
)
```

### Через API:

```bash
# Создать песочницу
curl -X POST http://localhost:8000/api/sandbox/create

# Выполнить код
curl -X POST http://localhost:8000/api/sandbox/execute \
  -H "Content-Type: application/json" \
  -d '{"sandbox_id": "abc123", "code": "print(2+2)", "language": "python"}'

# Сделать скриншот
curl -X POST http://localhost:8000/api/sandbox/screenshot \
  -H "Content-Type: application/json" \
  -d '{"sandbox_id": "abc123", "url": "https://google.com"}'
```

## 🌐 Доступ к графическому интерфейсу

После создания песочницы:

1. **noVNC (веб-браузер)**: http://localhost:[PORT]
2. **VNC клиент**: localhost:[VNC_PORT]
3. **Пароль**: `neopassword`

Можете видеть рабочий стол Linux с браузером Chrome!

## 🔧 Конфигурация контейнера

### Включенные инструменты:

- **Python 3.11** + популярные библиотеки
- **Node.js 20** + npm
- **Chrome/Chromium** + Playwright
- **Инструменты обработки данных**: pandas, numpy, jq
- **PDF/документы**: poppler, wkhtmltopdf
- **OCR**: tesseract
- **Утилиты**: git, vim, curl, wget

### Порты:

- **6080**: noVNC веб-интерфейс
- **5901**: VNC сервер
- **9222**: Chrome remote debugging
- **8003**: API сервер песочницы
- **8080**: HTTP сервер

## 🚨 Устранение проблем

### Docker не запускается:
```bash
# Linux
sudo systemctl start docker

# Windows/Mac
# Запустить Docker Desktop
```

### Недостаточно памяти:
```bash
# Увеличить лимиты Docker в настройках
# Минимум 4GB RAM для контейнера
```

### Порты заняты:
```bash
# Проверить занятые порты
netstat -tulpn | grep :6080

# Остановить конфликтующие сервисы
docker ps
docker stop <container_id>
```

### Ошибки сборки образа:
```bash
# Очистить Docker кэш
docker system prune -a

# Пересобрать образ
cd /workspace/neo/backend/sandbox/docker
docker build -t neo-sandbox:latest .
```

## 📊 Сравнение режимов

### Auto (рекомендуется):
- Использует Daytona если есть API ключ
- Автоматически переключается на локальную если Daytona недоступна
- Лучший пользовательский опыт

### Local (принудительно):
- Всегда использует локальную песочницу
- Игнорирует Daytona даже если настроена
- Максимальная приватность

### Daytona (принудительно):
- Всегда использует облачную Daytona
- Ошибка если Daytona недоступна
- Максимальная производительность

## 🎉 Готово!

Теперь у вас есть **бесплатная локальная альтернатива Daytona**! 

### Команды для запуска:

```bash
# 1. Настроить локальную песочницу
echo "SANDBOX_MODE=local" >> backend/.env

# 2. Запустить Neo AI
docker-compose up -d

# 3. Открыть приложение
open http://localhost:3000
```

**Neo AI теперь работает полностью локально без облачных зависимостей!** 🚀