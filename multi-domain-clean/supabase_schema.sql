-- Multi-Domain Clean: Supabase/PostgreSQL schema
-- Run this in Supabase Dashboard → SQL Editor if the app cannot connect directly (e.g. DNS error).
-- Or use: python scripts/init_supabase_tables.py (uses SUPABASE_DB_URL if set).

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    is_admin SMALLINT DEFAULT 0,
    is_active SMALLINT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "groups" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    parent_group_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    FOREIGN KEY (parent_group_id) REFERENCES "groups"(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS domains (
    id SERIAL PRIMARY KEY,
    domain_url TEXT NOT NULL,
    domain_name VARCHAR(255) NOT NULL,
    group_id INT,
    domain_index INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    FOREIGN KEY (group_id) REFERENCES "groups"(id)
);

CREATE TABLE IF NOT EXISTS user_api_keys (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    openai_api_key TEXT,
    openai_model VARCHAR(255),
    openrouter_api_key TEXT,
    openrouter_model VARCHAR(255),
    midjourney_api_token TEXT,
    midjourney_channel_id VARCHAR(255),
    r2_account_id VARCHAR(255),
    r2_access_key_id VARCHAR(255),
    r2_secret_access_key TEXT,
    r2_bucket_name VARCHAR(255),
    r2_public_url TEXT,
    cloudflare_account_id VARCHAR(255),
    cloudflare_api_token TEXT,
    local_api_url TEXT,
    local_models TEXT,
    default_categories TEXT,
    cloned_from_user_id INT,
    cloned_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id)
);

CREATE TABLE IF NOT EXISTS user_domains (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    domain_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
    UNIQUE (user_id, domain_id)
);

CREATE TABLE IF NOT EXISTS user_groups (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    group_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES "groups"(id) ON DELETE CASCADE,
    UNIQUE (user_id, group_id)
);

CREATE TABLE IF NOT EXISTS titles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    domain_id INT,
    group_id INT,
    user_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain_id) REFERENCES domains(id),
    FOREIGN KEY (group_id) REFERENCES "groups"(id)
);

CREATE TABLE IF NOT EXISTS article_content (
    id SERIAL PRIMARY KEY,
    title_id INT NOT NULL,
    language_code VARCHAR(10) DEFAULT 'en',
    recipe TEXT,
    prompt TEXT,
    content TEXT,
    article TEXT,
    prompt_image_ingredients TEXT,
    recipe_title_pin TEXT,
    pinterest_title TEXT,
    pinterest_description TEXT,
    pinterest_keywords TEXT,
    focus_keyphrase TEXT,
    meta_description TEXT,
    keyphrase_synonyms TEXT,
    main_image TEXT,
    ingredient_image TEXT,
    article_css TEXT,
    pin_image TEXT,
    writer TEXT,
    writer_avatar TEXT,
    top_image TEXT,
    bottom_image TEXT,
    avatar_image TEXT,
    article_html TEXT,
    model_used VARCHAR(255),
    generated_at TIMESTAMP,
    generation_time_seconds INT,
    validated SMALLINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (title_id) REFERENCES titles(id)
);

CREATE TABLE IF NOT EXISTS domain_templates (
    id SERIAL PRIMARY KEY,
    domain_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    template_json TEXT NOT NULL,
    sort_order INT DEFAULT 0,
    preview_image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain_id) REFERENCES domains(id)
);

CREATE TABLE IF NOT EXISTS domain_template_assignments (
    id SERIAL PRIMARY KEY,
    domain_id INT NOT NULL,
    template_id INT NOT NULL,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES domain_templates(id) ON DELETE CASCADE,
    UNIQUE (domain_id, template_id)
);

ALTER TABLE domains ADD COLUMN IF NOT EXISTS website_template TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS categories_list TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS last_pin_template_index TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS article_template_config TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS article_template_preview_url TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS article_html_snippets TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS article_template_name TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS domain_colors TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS domain_fonts TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS writers TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS last_writer_index TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS header_template TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS footer_template TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS side_article_template TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS category_page_template TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS writer_template TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS index_template TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS article_card_template TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS domain_page_about_us TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS domain_page_terms_of_use TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS domain_page_privacy_policy TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS domain_page_gdpr_policy TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS domain_page_cookie_policy TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS domain_page_copyright_policy TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS domain_page_disclaimer TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS domain_page_contact_us TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS cloudflare_info TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS pinterest_board_id TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS pinterest_access_token TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS pinterest_refresh_token TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS pinterest_app_id TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS pinterest_app_secret TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS visual_customizations TEXT;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS pinterest_mode TEXT;

CREATE TABLE IF NOT EXISTS pinterest_schedule (
    id SERIAL PRIMARY KEY,
    title_id INT NOT NULL,
    scheduled_at TIMESTAMP NOT NULL,
    status VARCHAR(32) DEFAULT 'pending',
    posted_at TIMESTAMP,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_pinterest_schedule_status ON pinterest_schedule(status);
CREATE INDEX IF NOT EXISTS idx_pinterest_schedule_scheduled_at ON pinterest_schedule(scheduled_at);

CREATE TABLE IF NOT EXISTS app_logs (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    log_type VARCHAR(64) NOT NULL,
    application VARCHAR(64) DEFAULT 'multi-domain',
    success SMALLINT DEFAULT 0,
    title_id INT,
    domain_id INT,
    group_id INT,
    job_id VARCHAR(128),
    message TEXT,
    reason TEXT,
    details TEXT
);
CREATE INDEX IF NOT EXISTS idx_log_type ON app_logs(log_type);
CREATE INDEX IF NOT EXISTS idx_application ON app_logs(application);
CREATE INDEX IF NOT EXISTS idx_success ON app_logs(success);
CREATE INDEX IF NOT EXISTS idx_title_id ON app_logs(title_id);
CREATE INDEX IF NOT EXISTS idx_domain_id ON app_logs(domain_id);
CREATE INDEX IF NOT EXISTS idx_job_id ON app_logs(job_id);
CREATE INDEX IF NOT EXISTS idx_created_at ON app_logs(created_at);
