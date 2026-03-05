# User Authentication System

## Overview

The multi-domain system now includes a complete user authentication and authorization system. Each user has their own:
- **Domains**: Users can only access domains assigned to them
- **Groups**: Users can only see groups containing their domains
- **API Keys**: Each user has their own API keys for OpenAI, OpenRouter, Local AI, Midjourney, R2, and Cloudflare

## Features

### 1. User Management
- **Login/Logout**: Secure session-based authentication
- **Registration**: New users can register (admin approval recommended)
- **User Profiles**: Each user can manage their API keys
- **Admin Panel**: Admins can manage users and assign domains

### 2. API Key Management
Each user configures their own API keys in `/profile`:
- **OpenAI**: API key and model selection
- **OpenRouter**: API key and default model
- **Local AI**: API URL and available models (Ollama/LM Studio)
- **Midjourney**: API token and channel ID
- **Cloudflare R2**: Account ID, access keys, bucket name, public URL
- **Cloudflare**: Account ID and API token

### 3. Domain Access Control
- Users can only see and manage domains assigned to them
- Admin users have access to all domains
- Domain assignment is managed through `/admin/users`

### 4. Data Isolation
- All queries are filtered by user's accessible domains
- Users cannot access titles, articles, or content from other users' domains
- Group visibility is based on domain ownership

## Getting Started

### First Time Setup

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Register the first user**:
   - Navigate to `http://localhost:5001/register`
   - Create an account
   - The first user should be made admin manually in the database

3. **Make first user admin** (in MySQL):
   ```sql
   UPDATE users SET is_admin = 1 WHERE id = 1;
   ```

4. **Configure API keys**:
   - Login and go to `/profile`
   - Add your API keys for the services you use
   - Save the configuration

5. **Assign domains** (admin only):
   - Go to `/admin/users`
   - Click "Domains" for a user
   - Assign domains to the user

### For Regular Users

1. **Login**: Navigate to `http://localhost:5001/login`
2. **Configure API Keys**: Go to `/profile` and add your API keys
3. **Access Your Domains**: Go to `/admin/domains` to see your assigned domains
4. **Generate Content**: Use the content generation features with your API keys

### For Administrators

1. **Manage Users**: Go to `/admin/users`
   - View all users
   - Activate/deactivate users
   - Assign domains to users

2. **Assign Domains**:
   - Click "Domains" button for a user
   - Add domains from the dropdown
   - Remove domains as needed

## API Key Priority

When generating content, the system uses API keys in this order:
1. **User's API keys** (from their profile)
2. **System default keys** (from .env file)

This allows:
- Users to use their own API keys and quotas
- Fallback to system keys if user hasn't configured their own
- Different users to use different AI providers

## Security Features

- **Password hashing**: SHA-256 hashing for passwords
- **Session management**: Secure session-based authentication
- **Access control**: Users can only access their assigned domains
- **API key encryption**: API keys stored in database (consider encryption in production)
- **Route protection**: All sensitive routes require authentication

## Database Schema

### users
- `id`: Primary key
- `username`: Unique username
- `password_hash`: SHA-256 hashed password
- `email`: Optional email
- `is_admin`: Admin flag (0/1)
- `is_active`: Active status (0/1)
- `created_at`: Timestamp

### user_api_keys
- `user_id`: Foreign key to users
- `openai_api_key`: OpenAI API key
- `openai_model`: Default OpenAI model
- `openrouter_api_key`: OpenRouter API key
- `openrouter_model`: Default OpenRouter model
- `local_api_url`: Local AI API URL
- `local_models`: Comma-separated local models
- `midjourney_api_token`: Midjourney token
- `midjourney_channel_id`: Midjourney channel
- `r2_account_id`: R2 account ID
- `r2_access_key_id`: R2 access key
- `r2_secret_access_key`: R2 secret key
- `r2_bucket_name`: R2 bucket name
- `r2_public_url`: R2 public URL
- `cloudflare_account_id`: Cloudflare account ID
- `cloudflare_api_token`: Cloudflare API token

### user_domains
- `user_id`: Foreign key to users
- `domain_id`: Foreign key to domains
- Unique constraint on (user_id, domain_id)

## Routes

### Public Routes
- `/login` - Login page
- `/register` - Registration page

### User Routes (require login)
- `/profile` - User profile and API key management
- `/logout` - Logout
- `/admin/domains` - View user's domains
- `/admin/groups` - View user's groups
- `/admin/titles` - View user's titles

### Admin Routes (require admin)
- `/admin/users` - User management
- `/api/users/<id>/domains` - Manage user domains
- `/api/users/<id>/status` - Activate/deactivate users

## Important Notes

1. **No API Keys = No Access**: Users must configure API keys to generate content
2. **Admin Access**: Admins see all domains and can manage all users
3. **Domain Assignment**: New domains must be assigned to users by admins
4. **Session Security**: Sessions are stored server-side; logout clears the session
5. **Password Security**: Use strong passwords; consider adding password requirements in production

## Troubleshooting

### "No domains assigned to your account"
- Contact your administrator to assign domains to your user

### "No AI provider API keys configured"
- Go to `/profile` and add at least one AI provider's API keys

### "Access denied to this title"
- You don't have access to the domain containing this title
- Contact your administrator

### "Admin access required"
- This feature is only available to admin users
- Contact your administrator if you need admin access

## Future Enhancements

Consider adding:
- Password reset functionality
- Email verification
- Two-factor authentication
- API key encryption at rest
- Audit logging for admin actions
- User groups/roles
- Domain sharing between users
- API rate limiting per user
