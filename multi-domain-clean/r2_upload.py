"""Upload image bytes to Cloudflare R2, or fall back to local disk + /api/hosted-images/ URL."""
import os
import re
import uuid
from urllib.parse import quote

from config import (
    R2_ACCOUNT_ID,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME,
    R2_PUBLIC_URL,
    HOSTED_IMAGES_DIR,
    PUBLIC_BASE_URL,
)

_SAFE_PREFIX_RE = re.compile(r"[^a-zA-Z0-9_-]+")


def _sanitize_prefix(key_prefix: str) -> str:
    s = _SAFE_PREFIX_RE.sub("_", (key_prefix or "img").strip())[:80]
    return s or "img"


def is_r2_configured(user_config: dict = None) -> bool:
    if user_config is None:
        user_config = {}
    account_id = user_config.get("r2_account_id") or R2_ACCOUNT_ID
    access_key = user_config.get("r2_access_key_id") or R2_ACCESS_KEY_ID
    secret_key = user_config.get("r2_secret_access_key") or R2_SECRET_ACCESS_KEY
    bucket_name = user_config.get("r2_bucket_name") or R2_BUCKET_NAME
    public_url = user_config.get("r2_public_url") or R2_PUBLIC_URL
    return bool(
        str(account_id or "").strip()
        and str(access_key or "").strip()
        and str(secret_key or "").strip()
        and str(bucket_name or "").strip()
        and str(public_url or "").strip()
    )


def _ext_for_content_type(content_type: str) -> str:
    ct = (content_type or "").lower()
    if "png" in ct:
        return "png"
    if "jpeg" in ct or "jpg" in ct:
        return "jpg"
    if "webp" in ct:
        return "webp"
    return "bin"


def _local_public_url(safe_prefix: str, fname: str, public_base_url: str) -> str:
    path = f"/api/hosted-images/{safe_prefix}/{fname}"
    base = (public_base_url or "").strip().rstrip("/")
    if base:
        return f"{base}{path}"
    return path


def save_bytes_local(
    data: bytes,
    key_prefix: str,
    content_type: str = "image/png",
    public_base_url: str = "",
) -> str:
    """Write bytes under HOSTED_IMAGES_DIR; return public URL (absolute if public_base_url set)."""
    safe_p = _sanitize_prefix(key_prefix)
    ext = _ext_for_content_type(content_type)
    fname = f"{uuid.uuid4().hex[:16]}.{ext}"
    root = os.path.abspath(HOSTED_IMAGES_DIR)
    dest_dir = os.path.join(root, safe_p)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, fname)
    with open(dest_path, "wb") as f:
        f.write(data)
    return _local_public_url(safe_p, fname, public_base_url)


def _resolve_public_base_url(explicit):
    """explicit None → use PUBLIC_BASE_URL env only; explicit str → use that (may be empty for relative URLs)."""
    if explicit is not None:
        return (explicit or "").strip().rstrip("/")
    return (PUBLIC_BASE_URL or "").strip().rstrip("/")


def upload_bytes_to_r2(
    data: bytes,
    key_prefix: str,
    content_type: str = "image/png",
    user_config: dict = None,
    public_base_url=None,
) -> str:
    """
    If R2 credentials + bucket + public URL are set → upload to R2 and return public object URL.
    Otherwise → store on local disk; return URL under /api/hosted-images/... (optionally prefixed by
    public_base_url or PUBLIC_BASE_URL in .env for Pinterest / external clients).

    public_base_url: pass request.url_root.rstrip('/') from Flask when handling a request, else None.
    """
    if user_config is None:
        user_config = {}

    if is_r2_configured(user_config):
        account_id = user_config.get("r2_account_id") or R2_ACCOUNT_ID
        access_key = user_config.get("r2_access_key_id") or R2_ACCESS_KEY_ID
        secret_key = user_config.get("r2_secret_access_key") or R2_SECRET_ACCESS_KEY
        bucket_name = user_config.get("r2_bucket_name") or R2_BUCKET_NAME
        public_url = user_config.get("r2_public_url") or R2_PUBLIC_URL

        ssl_verify = os.environ.get("R2_SSL_VERIFY", "true").strip().lower() not in ("0", "false", "no", "off")
        ext = _ext_for_content_type(content_type)
        fname = f"{uuid.uuid4().hex[:11]}.{ext}"
        key = f"{key_prefix}/{fname}".lstrip("/")
        import boto3

        r2 = boto3.client(
            service_name="s3",
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="auto",
            verify=ssl_verify,
        )
        r2.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=data,
            ContentType=content_type,
            ContentDisposition="inline",
        )
        return f"{public_url.rstrip('/')}/{quote(key)}"

    base = _resolve_public_base_url(public_base_url)
    return save_bytes_local(data, key_prefix, content_type, base)
