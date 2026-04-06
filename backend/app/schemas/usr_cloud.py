from typing import Any

from pydantic import BaseModel


class UsrCloudAuthStatus(BaseModel):
    enabled: bool
    configured: bool
    api_base_url: str
    account_configured: bool
    app_key_configured: bool
    token_cached: bool
    token_expires_at: str | None = None


class UsrCloudLoginResult(BaseModel):
    success: bool
    api_base_url: str
    uid: int | None = None
    token_cached: bool
    token_expires_at: str | None = None
    message: str


class UsrCloudDeviceListResult(BaseModel):
    success: bool
    path_used: str
    total: int | None = None
    items: list[dict[str, Any]]
    raw: dict[str, Any]
    message: str


class UsrCloudDeviceDetailResult(BaseModel):
    success: bool
    path_used: str
    item: dict[str, Any]
    raw: dict[str, Any]
    message: str
