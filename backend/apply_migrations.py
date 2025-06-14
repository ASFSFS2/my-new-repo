#!/usr/bin/env python3
"""
Скрипт для применения миграций к базе данных Supabase
"""
import os
import asyncio
from supabase import create_client, Client
import glob

# Загружаем переменные окружения
SUPABASE_URL = "https://rglnzrvwkdpwhbhrzvdo.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJnbG56cnZ3a2Rwd2hiaHJ6dmRvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTgxNDgyNCwiZXhwIjoyMDY1MzkwODI0fQ.NUQ1l5nbGWCKkLupBL8c_qaTHsa1LzEqlXYzf2-KxZI"

def apply_migrations():
    """Применяет все миграции к базе данных"""
    print("🔄 ПОДКЛЮЧАЮСЬ К SUPABASE...")
    
    # Создаем клиент Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    # Получаем список всех миграций
    migrations_dir = "/workspace/neo/backend/supabase/migrations"
    migration_files = sorted(glob.glob(f"{migrations_dir}/*.sql"))
    
    print(f"📁 НАЙДЕНО {len(migration_files)} МИГРАЦИЙ:")
    for file in migration_files:
        print(f"  - {os.path.basename(file)}")
    
    # Применяем каждую миграцию
    for migration_file in migration_files:
        print(f"\n🔧 ПРИМЕНЯЮ МИГРАЦИЮ: {os.path.basename(migration_file)}")
        
        try:
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Выполняем SQL через RPC
            result = supabase.rpc('exec_sql', {'sql': sql_content}).execute()
            print(f"✅ МИГРАЦИЯ ПРИМЕНЕНА: {os.path.basename(migration_file)}")
            
        except Exception as e:
            print(f"❌ ОШИБКА В МИГРАЦИИ {os.path.basename(migration_file)}: {e}")
            # Продолжаем с следующей миграцией
            continue
    
    print("\n🎉 ВСЕ МИГРАЦИИ ОБРАБОТАНЫ!")

if __name__ == "__main__":
    apply_migrations()