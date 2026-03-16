# Supabase Connection Troubleshooting

If you cannot connect to Supabase, try these steps:

## 1. Use the Connection Pooler (most reliable fix)

The direct connection (`db.xxx.supabase.co:5432`) often fails due to DNS, firewall, or network restrictions. Use the **Connection Pooler** instead:

1. Open your [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to **Project Settings** → **Database**
4. Scroll to **Connection string** → **Connection pooling**
5. Choose **Session mode** (port 6543)
6. Copy the **URI** format
7. Add to `.env`:
   ```
   SUPABASE_POOLER_URL=postgresql://postgres.[PROJECT_REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```

The app will try `SUPABASE_DB_URL` first, then `SUPABASE_POOLER_URL` if the first fails.

## 2. Use the correct database password

- Use your **database password** (the one you set when creating the project), NOT the anon/service key
- If you forgot it: Dashboard → Project Settings → Database → Reset database password

## 3. Set DB_BACKEND

Make sure you have in `.env`:
```
DB_BACKEND=supabase
```

## 4. Verify tables exist

Run the schema if this is a new Supabase project:
```bash
python scripts/init_supabase_tables.py
```

Or paste `supabase_schema.sql` into Supabase Dashboard → SQL Editor and run it.
