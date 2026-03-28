"""Midjourney image generation via UseAPI. Inspired by C1-MultiDomain A.3-IMAGINE."""
import os
import time
import uuid
import logging
import threading
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
)
import r2_upload

IMAGINE_ENDPOINT = f"{USEAPI_BASE_URL.rstrip('/')}/jobs/imagine"
JOB_STATUS_ENDPOINT = f"{USEAPI_BASE_URL.rstrip('/')}/jobs"
HEADERS = {"Authorization": f"Bearer {MIDJOURNEY_API_TOKEN}", "Content-Type": "application/json"}
MAX_JOB_SECONDS = 900
POLL_DELAY_S = 5

log = logging.getLogger(__name__)

# ── Multi-channel cooldown tracker ──────────────────────────────────────
# When a channel errors, it is "cooled down" for CHANNEL_COOLDOWN_ROUNDS
# successful uses of OTHER channels before it is tried again.
CHANNEL_COOLDOWN_ROUNDS = 3
_channel_cooldown_lock = threading.Lock()
# {channel_id: remaining_cooldown_count}
_channel_cooldowns: dict[str, int] = {}


def _sleep_before_imagine_request(user_config=None, image_delay_sec_override=None):
    """Pause immediately before sending a Midjourney /imagine job (profile setting or bulk-run override)."""
    user_config = user_config or {}
    if image_delay_sec_override is not None:
        d = max(0, min(180, int(image_delay_sec_override)))
    else:
        try:
            d = max(0, int(user_config.get("image_request_delay_sec", 15)))
        except (TypeError, ValueError):
            d = 15
    if d > 0:
        time.sleep(d)


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


def flip_image_horizontal_and_upload(image_url: str, key_prefix: str = "sibling_image", user_config: dict = None) -> str:
    """Download image from URL, flip horizontally (mirror left-right), upload to R2. Returns public URL. Use for sibling-domain pin images."""
    if not Image:
        raise RuntimeError("Pillow required for flip_image_horizontal_and_upload")
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
        # Extract structured error from UseAPI response
        err_detail = ""
        try:
            err_json = resp.json()
            err_detail = err_json.get("error", "")
        except Exception:
            err_detail = resp.text[:200]
        # Map HTTP status codes to user-friendly context
        code = resp.status_code
        if code == 429:
            return None, f"HTTP 429 Rate Limit: {err_detail}"
        elif code == 402:
            return None, f"HTTP 402 Payment Required: {err_detail}"
        elif code == 596:
            return None, f"HTTP 596 Moderation/CAPTCHA: {err_detail}"
        elif code == 401:
            return None, f"HTTP 401 Unauthorized: {err_detail}"
        elif code == 400:
            return None, f"HTTP 400 Bad Request: {err_detail}"
        return None, f"HTTP {code}: {err_detail}"
    except requests.exceptions.Timeout:
        return None, "Connection timeout: UseAPI did not respond within 60s"
    except requests.exceptions.ConnectionError as e:
        return None, f"Connection error: {str(e)[:150]}"
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
            return "error", {"error": f"Poll HTTP {resp.status_code}: {resp.text[:200]}"}
        data = resp.json()
        status = (data.get("status") or "").lower()
        if status in ("completed", "done", "success"):
            return "completed", data
        if status in ("failed", "error", "moderated"):
            # Extract detailed error from response content or job data
            fail_reason = ""
            resp_obj = data.get("response") or {}
            if isinstance(resp_obj, dict):
                fail_reason = resp_obj.get("content", "") or resp_obj.get("error", "")
            if not fail_reason:
                fail_reason = data.get("error", "") or data.get("content", "")
            data["error"] = f"Job {status}: {fail_reason[:200]}" if fail_reason else f"Job {status}"
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
    """Download grid, split into 4, upload to R2 or local hosted storage. Returns ([url1, url2, url3, url4], error_or_None)."""
    user_config = user_config or {}
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


def generate_4_images(
    prompt: str,
    key_prefix: str = "multi-domain",
    cancel_check=None,
    user_config: dict = None,
    image_delay_sec_override=None,
) -> tuple:
    """
    Create Midjourney job, poll until done, get 4 images, upload to R2 or local hosted storage.
    Returns ([url1, url2, url3, url4], error_or_None).
    Image 1 -> A, 2 -> B, 3 -> C, 4 -> D.
    cancel_check: optional callable; if it returns True, abort and return ([], "Cancelled").
    """
    user_config = user_config or {}
    _sleep_before_imagine_request(user_config, image_delay_sec_override)
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
            err_msg = data.get("error", "Job failed")
            return [], f"{err_msg}"
        if cancel_check and cancel_check():
            return [], "Cancelled"
        time.sleep(POLL_DELAY_S)
    elapsed_min = int((time.time() - start) / 60)
    return [], f"Job timed out after {elapsed_min} minutes - no response from Discord"


def _parse_channel_ids(user_config: dict) -> list[str]:
    """Parse channel IDs from user_config. Supports comma/newline separated values."""
    raw = user_config.get("midjourney_channel_id") or MIDJOURNEY_CHANNEL_ID or ""
    channels = []
    for part in str(raw).replace("\n", ",").split(","):
        ch = part.strip()
        if ch:
            channels.append(ch)
    return channels


def _mark_channel_cooldown(channel_id: str):
    """Mark a channel as cooled down after an error."""
    with _channel_cooldown_lock:
        _channel_cooldowns[channel_id] = CHANNEL_COOLDOWN_ROUNDS
        log.info("[imagine] Channel %s cooled down for %d rounds", channel_id, CHANNEL_COOLDOWN_ROUNDS)


def _tick_channel_success(channel_id: str):
    """After a successful use of a channel, decrement cooldown counters of OTHER channels."""
    with _channel_cooldown_lock:
        to_remove = []
        for ch, remaining in _channel_cooldowns.items():
            if ch != channel_id:
                new_val = remaining - 1
                if new_val <= 0:
                    to_remove.append(ch)
                    log.info("[imagine] Channel %s cooldown expired, available again", ch)
                else:
                    _channel_cooldowns[ch] = new_val
        for ch in to_remove:
            del _channel_cooldowns[ch]


def _get_available_channels(channel_ids: list[str]) -> list[str]:
    """Return channels that are not currently in cooldown."""
    with _channel_cooldown_lock:
        return [ch for ch in channel_ids if ch not in _channel_cooldowns]


def generate_4_images_multi_channel(
    prompt: str,
    key_prefix: str = "multi-domain",
    cancel_check=None,
    user_config: dict = None,
    image_delay_sec_override=None,
) -> tuple:
    """
    Like generate_4_images but rotates through multiple Discord channels.
    If a channel errors, it is skipped for CHANNEL_COOLDOWN_ROUNDS successful
    uses of other channels before being retried.

    Before each channel attempt, waits image_request_delay_sec from user_config (or
    image_delay_sec_override when set by bulk group runs), then sends /imagine.

    Returns ([url1, url2, url3, url4], error_or_None, used_channel_id_or_None).
    """
    user_config = user_config or {}
    all_channels = _parse_channel_ids(user_config)

    if not all_channels:
        return [], "No Midjourney channel IDs configured", None

    # Get available (non-cooled-down) channels
    available = _get_available_channels(all_channels)
    if not available:
        # All channels in cooldown — reset all and try from scratch
        log.warning("[imagine] All %d channels in cooldown, resetting all cooldowns", len(all_channels))
        with _channel_cooldown_lock:
            _channel_cooldowns.clear()
        available = list(all_channels)

    channel_errors = []  # accumulate errors from ALL channels tried
    tried_channel = None
    channels_tried = 0

    for channel_id in available:
        if cancel_check and cancel_check():
            return [], "Cancelled", None

        # Build a config copy with this specific channel
        cfg = dict(user_config)
        cfg["midjourney_channel_id"] = channel_id
        tried_channel = channel_id
        channels_tried += 1

        log.info("[imagine] Trying channel ..%s (%d/%d available, %d total)",
                 channel_id[-4:], channels_tried, len(available), len(all_channels))

        urls, err = generate_4_images(
            prompt,
            key_prefix,
            cancel_check,
            cfg,
            image_delay_sec_override=image_delay_sec_override,
        )

        if not err:
            # Success — tick cooldowns for other channels
            _tick_channel_success(channel_id)
            log.info("[imagine] Channel ..%s succeeded on try %d/%d",
                     channel_id[-4:], channels_tried, len(available))
            return urls, None, channel_id

        if err == "Cancelled":
            return [], "Cancelled", None

        # Error — cool down this channel and try next
        short_err = str(err)[:150]
        log.warning("[imagine] Channel ..%s failed (%d/%d): %s",
                    channel_id[-4:], channels_tried, len(available), short_err)
        _mark_channel_cooldown(channel_id)
        channel_errors.append(f"ch..{channel_id[-4:]}: {short_err}")

    # All channels failed
    if len(channel_errors) == 1:
        combined = channel_errors[0]
    else:
        combined = " | ".join(channel_errors)
    total_info = f"[{channels_tried}/{len(all_channels)} ch tried] "
    return [], total_info + combined, tried_channel
