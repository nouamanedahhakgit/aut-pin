"""Upload bytes to Cloudflare R2; return public URL. No dependency on Pinterest or imagine."""
import os
import uuid
from urllib.parse import quote

from config import (
    R2_ACCOUNT_ID,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME,
    R2_PUBLIC_URL,
)


def upload_bytes_to_r2(
    data: bytes,
    key_prefix: str,
    content_type: str = "image/png",
    user_config: dict = None,
) -> str:
    """
    Upload raw bytes to R2; returns public URL.
    key_prefix: e.g. "pin_image" or "multi-domain".
    Set R2_SSL_VERIFY=false in .env to skip SSL certificate verification (e.g. corporate proxy).
    """
    if user_config is None:
        user_config = {}
        
    account_id = user_config.get("r2_account_id") or R2_ACCOUNT_ID
    access_key = user_config.get("r2_access_key_id") or R2_ACCESS_KEY_ID
    secret_key = user_config.get("r2_secret_access_key") or R2_SECRET_ACCESS_KEY
    bucket_name = user_config.get("r2_bucket_name") or R2_BUCKET_NAME
    public_url = user_config.get("r2_public_url") or R2_PUBLIC_URL

    if not all([account_id, access_key, secret_key, bucket_name, public_url]):
        raise RuntimeError("R2 not configured (missing keys in user profile or environment)")
        
    ssl_verify = os.environ.get("R2_SSL_VERIFY", "true").strip().lower() not in ("0", "false", "no", "off")
    ext = "png" if content_type == "image/png" else "bin"
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
