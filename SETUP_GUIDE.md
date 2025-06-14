# Neo AI - Руководство по настройке

## ✅ Выполненные настройки

### 🔧 Конфигурация
- ✅ Подключен Supabase: `https://qytdfvyzywvbhcykwfox.supabase.co`
- ✅ Настроен OpenRouter с ключом API
- ✅ Установлена модель по умолчанию: `deepseek/deepseek-chat:free`
- ✅ Отключены все остальные модели (только DeepSeek доступен)
- ✅ Переименован проект с "Neo" на "Neo"

### 📁 Измененные файлы
- `backend/.env` - основная конфигурация backend
- `frontend/.env` - конфигурация frontend
- `backend/utils/constants.py` - настройки доступных моделей
- `backend/utils/config.py` - конфигурация по умолчанию
- `frontend/src/lib/site.ts` - настройки сайта
- `frontend/package.json` - имя frontend пакета
- `backend/pyproject.toml` - имя backend пакета
- `README.md` - обновленное описание проекта

## 🚀 Запуск приложения

### Предварительные требования
- Docker и Docker Compose
- Python 3.11+
- Node.js 18+

### Шаги запуска

1. **Проверка конфигурации:**
   ```bash
   python test_config.py
   ```

2. **Запуск мастера настройки:**
   ```bash
   python setup.py
   ```

3. **Запуск приложения:**
   ```bash
   python start.py
   ```

### Доступ к приложению
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## 🔑 Настроенные ключи

### Supabase
- URL: `https://qytdfvyzywvbhcykwfox.supabase.co`
- Anon Key: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### OpenRouter
- API Key: `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`
- Модель: `deepseek/deepseek-chat:free`

## 🤖 Доступные модели

Настроено только одна модель для всех уровней подписки:
- `deepseek/deepseek-chat:free`

Все остальные модели (Claude, GPT-4, Gemini и т.д.) отключены.

## 📝 Дополнительные настройки

Если нужно добавить дополнительные API ключи, отредактируйте файл `backend/.env`:

```bash
# Поиск в интернете (опционально)
TAVILY_API_KEY=your_tavily_key

# Веб-скрапинг (опционально)
FIRECRAWL_API_KEY=your_firecrawl_key

# Песочница для выполнения кода (опционально)
DAYTONA_API_KEY=your_daytona_key
DAYTONA_SERVER_URL=your_daytona_url
DAYTONA_TARGET=your_target
```

## 🎯 Готово к использованию!

Проект Neo AI настроен и готов к запуску с:
- Подключенной базой данных Supabase
- Настроенной моделью DeepSeek через OpenRouter
- Переименованным брендингом на "Neo"
- Отключенными альтернативными моделями