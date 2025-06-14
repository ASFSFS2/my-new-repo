-- Создание основных таблиц для Neo AI

-- 1. Создаем таблицу projects
CREATE TABLE IF NOT EXISTS projects (
    project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    account_id UUID NOT NULL,
    sandbox JSONB DEFAULT '{}'::jsonb,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 2. Создаем таблицу threads
CREATE TABLE IF NOT EXISTS threads (
    thread_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID,
    project_id UUID REFERENCES projects(project_id) ON DELETE CASCADE,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 3. Создаем таблицу agents
CREATE TABLE IF NOT EXISTS agents (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    system_prompt TEXT NOT NULL,
    configured_mcps JSONB DEFAULT '[]'::jsonb,
    agentpress_tools JSONB DEFAULT '{}'::jsonb,
    is_default BOOLEAN DEFAULT false,
    avatar VARCHAR(10),
    avatar_color VARCHAR(7),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Создаем таблицу messages
CREATE TABLE IF NOT EXISTS messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL REFERENCES threads(thread_id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    is_llm_message BOOLEAN NOT NULL DEFAULT TRUE,
    content JSONB NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 5. Создаем таблицу agent_runs
CREATE TABLE IF NOT EXISTS agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL REFERENCES threads(thread_id),
    status TEXT NOT NULL DEFAULT 'running',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    responses JSONB NOT NULL DEFAULT '[]'::jsonb,
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Создаем индексы для производительности
CREATE INDEX IF NOT EXISTS idx_threads_created_at ON threads(created_at);
CREATE INDEX IF NOT EXISTS idx_threads_account_id ON threads(account_id);
CREATE INDEX IF NOT EXISTS idx_threads_project_id ON threads(project_id);
CREATE INDEX IF NOT EXISTS idx_agent_runs_thread_id ON agent_runs(thread_id);
CREATE INDEX IF NOT EXISTS idx_agent_runs_status ON agent_runs(status);
CREATE INDEX IF NOT EXISTS idx_agent_runs_created_at ON agent_runs(created_at);
CREATE INDEX IF NOT EXISTS idx_projects_account_id ON projects(account_id);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_thread_id ON messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_agents_account_id ON agents(account_id);
CREATE INDEX IF NOT EXISTS idx_agents_is_default ON agents(is_default);
CREATE INDEX IF NOT EXISTS idx_agents_created_at ON agents(created_at);

-- Создаем функцию для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Создаем триггеры для updated_at
CREATE TRIGGER IF NOT EXISTS update_threads_updated_at
    BEFORE UPDATE ON threads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_messages_updated_at
    BEFORE UPDATE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_agent_runs_updated_at
    BEFORE UPDATE ON agent_runs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER IF NOT EXISTS update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Создаем функцию для обновления updated_at для agents
CREATE OR REPLACE FUNCTION update_agents_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Создаем триггер для agents
CREATE TRIGGER IF NOT EXISTS trigger_agents_updated_at
    BEFORE UPDATE ON agents
    FOR EACH ROW
    EXECUTE FUNCTION update_agents_updated_at();

-- Добавляем agent_id в threads если не существует
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='threads' AND column_name='agent_id') THEN
        ALTER TABLE threads ADD COLUMN agent_id UUID REFERENCES agents(agent_id) ON DELETE SET NULL;
        CREATE INDEX idx_threads_agent_id ON threads(agent_id);
    END IF;
END $$;

-- Создаем уникальный индекс для default agent per account
CREATE UNIQUE INDEX IF NOT EXISTS idx_agents_account_default ON agents(account_id, is_default) WHERE is_default = true;

-- Включаем RLS (Row Level Security)
ALTER TABLE threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;

-- Создаем базовые RLS политики (если basejump доступен)
-- Эти политики будут работать только если basejump.has_role_on_account функция существует

-- Политики для threads
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'has_role_on_account') THEN
        -- Политики для threads
        CREATE POLICY IF NOT EXISTS thread_select_policy ON threads
            FOR SELECT
            USING (basejump.has_role_on_account(account_id));

        CREATE POLICY IF NOT EXISTS thread_insert_policy ON threads
            FOR INSERT
            WITH CHECK (basejump.has_role_on_account(account_id));

        CREATE POLICY IF NOT EXISTS thread_update_policy ON threads
            FOR UPDATE
            USING (basejump.has_role_on_account(account_id));

        CREATE POLICY IF NOT EXISTS thread_delete_policy ON threads
            FOR DELETE
            USING (basejump.has_role_on_account(account_id));

        -- Политики для projects
        CREATE POLICY IF NOT EXISTS project_select_policy ON projects
            FOR SELECT
            USING (basejump.has_role_on_account(account_id) OR is_public = true);

        CREATE POLICY IF NOT EXISTS project_insert_policy ON projects
            FOR INSERT
            WITH CHECK (basejump.has_role_on_account(account_id));

        CREATE POLICY IF NOT EXISTS project_update_policy ON projects
            FOR UPDATE
            USING (basejump.has_role_on_account(account_id));

        CREATE POLICY IF NOT EXISTS project_delete_policy ON projects
            FOR DELETE
            USING (basejump.has_role_on_account(account_id));

        -- Политики для agents
        CREATE POLICY IF NOT EXISTS agents_select_own ON agents
            FOR SELECT
            USING (basejump.has_role_on_account(account_id));

        CREATE POLICY IF NOT EXISTS agents_insert_own ON agents
            FOR INSERT
            WITH CHECK (basejump.has_role_on_account(account_id));

        CREATE POLICY IF NOT EXISTS agents_update_own ON agents
            FOR UPDATE
            USING (basejump.has_role_on_account(account_id));

        CREATE POLICY IF NOT EXISTS agents_delete_own ON agents
            FOR DELETE
            USING (basejump.has_role_on_account(account_id) AND is_default = false);

        -- Политики для messages
        CREATE POLICY IF NOT EXISTS message_select_policy ON messages
            FOR SELECT
            USING (
                EXISTS (
                    SELECT 1 FROM threads t 
                    WHERE t.thread_id = messages.thread_id 
                    AND basejump.has_role_on_account(t.account_id)
                )
            );

        CREATE POLICY IF NOT EXISTS message_insert_policy ON messages
            FOR INSERT
            WITH CHECK (
                EXISTS (
                    SELECT 1 FROM threads t 
                    WHERE t.thread_id = messages.thread_id 
                    AND basejump.has_role_on_account(t.account_id)
                )
            );

        -- Политики для agent_runs
        CREATE POLICY IF NOT EXISTS agent_run_select_policy ON agent_runs
            FOR SELECT
            USING (
                EXISTS (
                    SELECT 1 FROM threads t 
                    WHERE t.thread_id = agent_runs.thread_id 
                    AND basejump.has_role_on_account(t.account_id)
                )
            );

        CREATE POLICY IF NOT EXISTS agent_run_insert_policy ON agent_runs
            FOR INSERT
            WITH CHECK (
                EXISTS (
                    SELECT 1 FROM threads t 
                    WHERE t.thread_id = agent_runs.thread_id 
                    AND basejump.has_role_on_account(t.account_id)
                )
            );

        RAISE NOTICE 'RLS политики созданы с basejump функциями';
    ELSE
        RAISE NOTICE 'basejump функции не найдены, RLS политики пропущены';
    END IF;
END $$;

-- Выводим информацию о созданных таблицах
SELECT 'Таблицы успешно созданы!' as status;
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('threads', 'projects', 'agents', 'messages', 'agent_runs')
ORDER BY table_name, ordinal_position;