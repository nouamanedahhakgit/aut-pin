"""
Pinterest API v5 integration for uploading pins.

Creates pins via POST https://api.pinterest.com/v5/pins
OAuth: exchange code for token, create board automatically
"""
import base64
import logging
import os
import urllib.parse

import requests

log = logging.getLogger(__name__)

PINTEREST_API_BASE = "https://api.pinterest.com/v5"
PINTEREST_OAUTH_URL = "https://www.pinterest.com/oauth/"
PINTEREST_TOKEN_URL = "https://api.pinterest.com/v5/oauth/token"
SCOPES = "pins:write,boards:read,boards:write,user_accounts:read"


def _get_access_token(domain_value=None):
    """Get Pinterest access token from domain config or env."""
    token = (domain_value or "").strip() if domain_value else None
    if not token:
        token = os.environ.get("PINTEREST_ACCESS_TOKEN", "").strip()
    return token or None


def _get_board_id(domain_value=None):
    """Get Pinterest board ID from domain config or env."""
    board = (domain_value or "").strip() if domain_value else None
    if not board:
        board = os.environ.get("PINTEREST_BOARD_ID", "").strip()
    return board or None


def _build_article_url(domain_url, title_id):
    """Build full article URL for Pinterest link. Uses article/{id}.html structure."""
    base = (domain_url or "").strip()
    if not base:
        return None
    if not base.startswith("http"):
        base = "https://" + base
    base = base.rstrip("/")
    return f"{base}/article/{title_id}.html"


def create_pin(
    *,
    image_url,
    title,
    description,
    link=None,
    board_id=None,
    access_token=None,
):
    """
    Create a pin on Pinterest via API v5.

    Args:
        image_url: Public URL of the pin image (e.g. from R2).
        title: Pin title (max 100 chars).
        description: Pin description (max 800 chars).
        link: Optional URL the pin links to (article URL).
        board_id: Pinterest board ID (required).
        access_token: Pinterest OAuth access token (required).

    Returns:
        dict with keys: success (bool), pin_id (str or None), error (str or None).
    """
    token = _get_access_token(access_token)
    board = board_id or _get_board_id()
    if not token:
        return {"success": False, "pin_id": None, "error": "Pinterest access token not configured (PINTEREST_ACCESS_TOKEN or domain)"}
    if not board:
        return {"success": False, "pin_id": None, "error": "Pinterest board ID not configured (PINTEREST_BOARD_ID or domain)"}
    if not image_url or not str(image_url).startswith("http"):
        return {"success": False, "pin_id": None, "error": "Valid image_url (public HTTP URL) required"}

    title_clean = (title or "")[:100]
    desc_clean = (description or "")[:800]
    link_clean = (link or "").strip() if link and str(link).startswith("http") else None

    payload = {
        "board_id": board,
        "title": title_clean or "Recipe",
        "description": desc_clean or title_clean,
        "media_source": {
            "source_type": "image_url",
            "url": str(image_url).strip(),
        },
    }
    if link_clean:
        payload["link"] = link_clean

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        r = requests.post(
            f"{PINTEREST_API_BASE}/pins",
            json=payload,
            headers=headers,
            timeout=30,
        )
        body = r.json() if r.text else {}
        if r.status_code in (200, 201):
            pin_id = body.get("id") or body.get("pin_id")
            log.info("[pinterest] Pin created: %s", pin_id)
            return {"success": True, "pin_id": pin_id, "error": None}
        err_msg = body.get("message") or body.get("error") or r.text[:500]
        log.warning("[pinterest] Create pin failed %s: %s", r.status_code, err_msg)
        return {"success": False, "pin_id": None, "error": f"Pinterest API {r.status_code}: {err_msg}"}
    except requests.RequestException as e:
        log.exception("[pinterest] Request failed: %s", e)
        return {"success": False, "pin_id": None, "error": str(e)}


def is_configured(access_token=None, board_id=None):
    """Check if Pinterest posting is configured."""
    return bool(_get_access_token(access_token) and _get_board_id(board_id))


def get_oauth_auth_url(redirect_uri, client_id, state):
    """Build Pinterest OAuth authorization URL. User is redirected here to log in and approve."""
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
    }
    return PINTEREST_OAUTH_URL + "?" + urllib.parse.urlencode(params)


def exchange_code_for_token(code, redirect_uri, client_id, client_secret):
    """
    Exchange OAuth authorization code for access_token and refresh_token.
    Returns: { success, access_token, refresh_token, expires_in, error }
    """
    if not all([code, redirect_uri, client_id, client_secret]):
        return {"success": False, "access_token": None, "refresh_token": None, "error": "Missing code, redirect_uri, client_id or client_secret"}
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }
    try:
        r = requests.post(PINTEREST_TOKEN_URL, headers=headers, data=data, timeout=30)
        body = r.json() if r.text else {}
        if r.status_code in (200, 201):
            return {
                "success": True,
                "access_token": body.get("access_token"),
                "refresh_token": body.get("refresh_token"),
                "expires_in": body.get("expires_in"),
                "error": None,
            }
        err = body.get("message") or body.get("error") or r.text[:300]
        return {"success": False, "access_token": None, "refresh_token": None, "error": err}
    except requests.RequestException as e:
        log.exception("[pinterest] Token exchange failed: %s", e)
        return {"success": False, "access_token": None, "refresh_token": None, "error": str(e)}


def create_board(access_token, name, description=None, privacy="PUBLIC"):
    """
    Create a board via API. Returns { success, board_id, error }.
    Requires access_token with boards:write scope.
    """
    if not access_token or not name:
        return {"success": False, "board_id": None, "error": "access_token and name required"}
    payload = {"name": (name or "Pins")[:100]}
    if description:
        payload["description"] = (description or "")[:500]
    payload["privacy"] = privacy if privacy in ("PUBLIC", "SECRET") else "PUBLIC"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    try:
        r = requests.post(f"{PINTEREST_API_BASE}/boards", json=payload, headers=headers, timeout=30)
        body = r.json() if r.text else {}
        if r.status_code in (200, 201):
            bid = body.get("id")
            log.info("[pinterest] Board created: %s", bid)
            return {"success": True, "board_id": bid, "error": None}
        err = body.get("message") or body.get("error") or r.text[:300]
        return {"success": False, "board_id": None, "error": err}
    except requests.RequestException as e:
        log.exception("[pinterest] Create board failed: %s", e)
        return {"success": False, "board_id": None, "error": str(e)}
