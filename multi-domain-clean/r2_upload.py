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
) -> str:
    """
    Upload raw bytes to R2; returns public URL.
    key_prefix: e.g. "pin_image" or "multi-domain".
    Set R2_SSL_VERIFY=false in .env to skip SSL certificate verification (e.g. corporate proxy).
    """
    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_PUBLIC_URL]):
        raise RuntimeError("R2 not configured (missing env: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_PUBLIC_URL)")
    ssl_verify = os.environ.get("R2_SSL_VERIFY", "true").strip().lower() not in ("0", "false", "no", "off")
    ext = "png" if content_type == "image/png" else "bin"
    fname = f"{uuid.uuid4().hex[:11]}.{ext}"
    key = f"{key_prefix}/{fname}".lstrip("/")
    import boto3
    r2 = boto3.client(
        service_name="s3",
        endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
        verify=ssl_verify,
    )
    r2.put_object(
        Bucket=R2_BUCKET_NAME,
        Key=key,
        Body=data,
        ContentType=content_type,
        ContentDisposition="inline",
    )
    return f"{R2_PUBLIC_URL.rstrip('/')}/{quote(key)}"
