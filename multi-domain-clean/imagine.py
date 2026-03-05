"""Midjourney image generation via UseAPI. Inspired by C1-MultiDomain A.3-IMAGINE."""
import os
import time
import uuid
import requests
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    Image = None

from config import (
    MIDJOURNEY_API_TOKEN,
    MIDJOURNEY_CHANNEL_ID,
    USEAPI_BASE_URL,
    R2_ACCOUNT_ID,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME,
    R2_PUBLIC_URL,
)
import r2_upload

IMAGINE_ENDPOINT = f"{USEAPI_BASE_URL.rstrip('/')}/jobs/imagine"
JOB_STATUS_ENDPOINT = f"{USEAPI_BASE_URL.rstrip('/')}/jobs"
HEADERS = {"Authorization": f"Bearer {MIDJOURNEY_API_TOKEN}", "Content-Type": "application/json"}
MAX_JOB_SECONDS = 900
POLL_DELAY_S = 5


def _normalize_prompt(p: str) -> str:
    if not p or not str(p).strip():
        return ""
    s = str(p).replace("\r", " ").replace("\n", " ").strip()
    return " ".join(s.split())


def download_image(url: str):
    if not Image:
        raise RuntimeError("Pillow not installed")
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    img = Image.open(BytesIO(resp.content)).convert("RGB")
    return img


def split_midjourney_grid(image) -> list:
    """Split 2x2 grid into 4 images: TL, TR, BL, BR -> [img1, img2, img3, img4]."""
    w, h = image.size
    if w != h:
        raise ValueError(f"Expected square image, got {w}x{h}")
    half = w // 2
    return [
        image.crop((0, 0, half, half)),
        image.crop((half, 0, w, half)),
        image.crop((0, half, half, h)),
        image.crop((half, half, w, h)),
    ]


def _r2_put(image, key_prefix: str, user_config: dict = None) -> str:
    buf = BytesIO()
    image.save(buf, format="PNG")
    return r2_upload.upload_bytes_to_r2(buf.getvalue(), key_prefix, "image/png", user_config=user_config)


def flip_image_vertical_and_upload(image_url: str, key_prefix: str = "bottom_image", user_config: dict = None) -> str:
    """Download image from URL, flip horizontally (mirror left-right), upload to R2. Returns public URL."""
    if not Image:
        raise RuntimeError("Pillow required for flip_image_vertical_and_upload")
    img = download_image(image_url)
    flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
    return _r2_put(flipped, key_prefix, user_config=user_config)


def _append_ar(prompt: str, ar: str = "1:1") -> str:
    suffix = f" --ar {ar.strip()}"
    return prompt if suffix in prompt else (prompt + suffix)


def create_imagine_task(prompt: str, user_config: dict = None) -> tuple:
    """Start Midjourney job. Returns (jobid, error_or_None)."""
    user_config = user_config or {}
    mj_token = user_config.get("midjourney_api_token") or MIDJOURNEY_API_TOKEN
    mj_channel = user_config.get("midjourney_channel_id") or MIDJOURNEY_CHANNEL_ID
    
    prompt = _normalize_prompt(prompt)
    if len(prompt) < 10:
        return None, "Prompt too short"
    prompt = _append_ar(prompt)
    if not mj_token or not mj_channel:
        return None, "Midjourney not configured in user profile"
    body = {"prompt": prompt, "channel": mj_channel, "stream": False}
    headers = {"Authorization": f"Bearer {mj_token}", "Content-Type": "application/json"}
    try:
        resp = requests.post(IMAGINE_ENDPOINT, headers=headers, json=body, timeout=60)
        if resp.status_code == 201:
            data = resp.json()
            jobid = data.get("jobid") or data.get("job_id") or data.get("id")
            if jobid:
                return jobid, None
        return None, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return None, str(e)


def poll_job(jobid: str, user_config: dict = None) -> tuple:
    """Poll job status. Returns (status, data). status in completed, failed, pending."""
    user_config = user_config or {}
    mj_token = user_config.get("midjourney_api_token") or MIDJOURNEY_API_TOKEN
    
    try:
        resp = requests.get(
            f"{JOB_STATUS_ENDPOINT}/{jobid}",
            headers={"Authorization": f"Bearer {mj_token}"},
            timeout=30,
        )
        if resp.status_code != 200:
            return "error", {"error": resp.text[:200]}
        data = resp.json()
        status = (data.get("status") or "").lower()
        if status in ("completed", "done", "success"):
            return "completed", data
        if status in ("failed", "error", "moderated"):
            return "failed", data
        return "pending", data
    except Exception as e:
        return "error", {"error": str(e)}


def _get_grid_url(job_data: dict) -> str:
    """Get grid URL from response. UseAPI v3: attachments[0].proxy_url or .url = full grid."""
    resp = job_data.get("response") or {}
    if isinstance(resp, dict):
        for key in ("proxy_grid_url", "grid_proxy_url", "grid_url", "url"):
            u = resp.get(key)
            if u and isinstance(u, str) and u.startswith("http"):
                return u
        for att in resp.get("attachments") or []:
            if isinstance(att, dict):
                u = att.get("proxy_url") or att.get("url")
                if u and str(u).startswith("http"):
                    return str(u)
    return ""


def _extract_useapi_urls(job_data: dict) -> list:
    """
    Extract image URLs from UseAPI v3 response.
    - response.imageUx: [{id:1, url:...}, {id:2, url:...}, ...] = 4 separate grid cells (preferred)
    - response.attachments: grid image (proxy_url/url)
    - response.grid_url, image_urls (legacy)
    """
    urls = []
    resp = job_data.get("response") or {}
    if isinstance(resp, dict):
        image_ux = resp.get("imageUx") or resp.get("image_ux")
        if isinstance(image_ux, list) and len(image_ux) >= 4:
            sorted_ux = sorted(image_ux, key=lambda x: x.get("id", 0) if isinstance(x, dict) else 0)
            for item in sorted_ux[:4]:
                if isinstance(item, dict):
                    u = item.get("url")
                    if u and str(u).startswith("http"):
                        urls.append(str(u))
            if len(urls) == 4:
                return urls
        for att in resp.get("attachments") or []:
            if isinstance(att, dict):
                u = att.get("proxy_url") or att.get("url")
                if u and str(u).startswith("http"):
                    urls.append(str(u))
        for key in ("grid_url", "proxy_grid_url", "grid_proxy_url", "url"):
            u = resp.get(key)
            if u and str(u).startswith("http"):
                urls.append(str(u))
    for u in job_data.get("image_urls") or []:
        if u and str(u).startswith("http"):
            urls.append(str(u))
    seen, unique = set(), []
    for u in urls:
        if u not in seen:
            unique.append(u)
            seen.add(u)
    return unique


def process_grid_to_r2(grid_url: str, key_prefix: str, user_config: dict = None) -> tuple:
    """Download grid, split into 4, upload to R2. Returns ([url1, url2, url3, url4], error_or_None)."""
    user_config = user_config or {}
    account_id = user_config.get("r2_account_id") or R2_ACCOUNT_ID
    access_key = user_config.get("r2_access_key_id") or R2_ACCESS_KEY_ID
    secret_key = user_config.get("r2_secret_access_key") or R2_SECRET_ACCESS_KEY
    bucket_name = user_config.get("r2_bucket_name") or R2_BUCKET_NAME
    public_url = user_config.get("r2_public_url") or R2_PUBLIC_URL
    if not account_id or not access_key or not secret_key or not bucket_name or not public_url:
        return [], "R2 not configured in user profile"
    try:
        img = download_image(grid_url)
        splits = split_midjourney_grid(img)
        prefix = f"{key_prefix}/{uuid.uuid4().hex[:8]}"
        urls = []
        for i, s in enumerate(splits):
            url = _r2_put(s, prefix, user_config=user_config)
            urls.append(url)
        return urls, None
    except Exception as e:
        return [], str(e)


def generate_4_images(prompt: str, key_prefix: str = "multi-domain", cancel_check=None, user_config: dict = None) -> tuple:
    """
    Create Midjourney job, poll until done, get 4 images, upload to R2.
    Returns ([url1, url2, url3, url4], error_or_None).
    Image 1 -> A, 2 -> B, 3 -> C, 4 -> D.
    cancel_check: optional callable; if it returns True, abort and return ([], "Cancelled").
    """
    jobid, err = create_imagine_task(prompt, user_config=user_config)
    if err:
        return [], err
    start = time.time()
    while time.time() - start < MAX_JOB_SECONDS:
        if cancel_check and cancel_check():
            return [], "Cancelled"
        status, data = poll_job(jobid, user_config=user_config)
        if status == "completed":
            grid_url = _get_grid_url(data)
            if grid_url:
                return process_grid_to_r2(grid_url, key_prefix, user_config=user_config)
            urls = _extract_useapi_urls(data)
            if len(urls) >= 4:
                try:
                    result = []
                    for i in range(4):
                        img = download_image(urls[i])
                        prefix = f"{key_prefix}/{uuid.uuid4().hex[:8]}"
                        url = _r2_put(img, prefix, user_config=user_config)
                        result.append(url)
                    return result, None
                except Exception as e:
                    return [], str(e)
            if len(urls) == 1:
                return process_grid_to_r2(urls[0], key_prefix, user_config=user_config)
            if len(urls) > 0:
                return [], f"Expected grid (1 URL) or 4 images, got {len(urls)}"
            return [], "No grid or image URLs in response"
        if status in ("failed", "error"):
            return [], data.get("error", "Job failed")
        if cancel_check and cancel_check():
            return [], "Cancelled"
        time.sleep(POLL_DELAY_S)
    return [], "Timeout waiting for job"
