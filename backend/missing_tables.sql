-- Создание недостающих таблиц для Neo AI

-- Таблица account_user (связь пользователей с аккаунтами)
CREATE TABLE IF NOT EXISTS public.account_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    account_id UUID NOT NULL,
    account_role TEXT NOT NULL DEFAULT 'member',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, account_id)
);

-- Таблица billing_customers (информация о биллинге клиентов)
CREATE TABLE IF NOT EXISTS public.billing_customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL UNIQUE,
    stripe_customer_id TEXT,
    active BOOLEAN DEFAULT true,
    subscription_status TEXT DEFAULT 'active',
    plan_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_account_user_user_id ON public.account_user(user_id);
CREATE INDEX IF NOT EXISTS idx_account_user_account_id ON public.account_user(account_id);
CREATE INDEX IF NOT EXISTS idx_billing_customers_account_id ON public.billing_customers(account_id);
CREATE INDEX IF NOT EXISTS idx_billing_customers_stripe_id ON public.billing_customers(stripe_customer_id);

-- Вставим тестовые данные для нашего пользователя (используем правильные UUID)
INSERT INTO public.account_user (user_id, account_id, account_role) 
VALUES (
    '550e8400-e29b-41d4-a716-446655440000'::uuid, 
    '550e8400-e29b-41d4-a716-446655440001'::uuid, 
    'owner'
) ON CONFLICT (user_id, account_id) DO NOTHING;

INSERT INTO public.billing_customers (account_id, active, subscription_status, plan_id)
VALUES (
    '550e8400-e29b-41d4-a716-446655440001'::uuid,
    true,
    'active',
    'free'
) ON CONFLICT (account_id) DO NOTHING;