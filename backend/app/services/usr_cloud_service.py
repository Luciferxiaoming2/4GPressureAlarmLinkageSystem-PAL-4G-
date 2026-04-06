import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.core.config import settings


class UsrCloudConfigurationError(ValueError):
    pass


class UsrCloudLoginError(RuntimeError):
    pass


class UsrCloudRequestError(RuntimeError):
    pass


@dataclass
class UsrCloudTokenState:
    token: str
    uid: int | None
    sign_code: str | None
    expires_at: datetime


class UsrCloudService:
    def __init__(self) -> None:
        self._token_state: UsrCloudTokenState | None = None

    def _login_url(self) -> str:
        return f"{settings.USR_CLOUD_API_BASE_URL.rstrip('/')}/usrCloud/user/login"

    def _build_url(self, path: str) -> str:
        return f"{settings.USR_CLOUD_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"

    def _is_configured(self) -> bool:
        return bool(settings.USR_CLOUD_ACCOUNT and settings.USR_CLOUD_PASSWORD)

    @staticmethod
    def _extract_data(body: dict[str, Any]) -> Any:
        if isinstance(body.get("data"), (dict, list)):
            return body["data"]
        return body

    @staticmethod
    def _extract_items(body: dict[str, Any]) -> tuple[list[dict[str, Any]], int | None]:
        data = UsrCloudService._extract_data(body)
        total: int | None = None

        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)], len(data)

        if isinstance(data, dict):
            for total_key in ["total", "count", "size", "recordsTotal"]:
                total_raw = data.get(total_key)
                if total_raw is not None:
                    try:
                        total = int(total_raw)
                    except (TypeError, ValueError):
                        total = None
                    break

            for list_key in [
                "list",
                "rows",
                "items",
                "devices",
                "deviceList",
                "result",
                "records",
            ]:
                items = data.get(list_key)
                if isinstance(items, list):
                    return [item for item in items if isinstance(item, dict)], total

        return [], total

    @staticmethod
    def _extract_item(body: dict[str, Any]) -> dict[str, Any]:
        data = UsrCloudService._extract_data(body)
        if isinstance(data, dict):
            for item_key in ["item", "device", "detail", "info", "result"]:
                item = data.get(item_key)
                if isinstance(item, dict):
                    return item
            return data
        raise UsrCloudRequestError("USR cloud detail response does not contain a device object")

    @staticmethod
    def _build_detail_payload(
        dev_id: str | None = None,
        device_id: str | None = None,
        device_no: str | None = None,
        cusdevice_no: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if dev_id:
            payload["devId"] = dev_id
        if device_id:
            payload["deviceId"] = device_id
            payload.setdefault("id", device_id)
        if device_no:
            payload["deviceNo"] = device_no
        if cusdevice_no:
            payload["cusdeviceNo"] = cusdevice_no
        return payload

    def _device_list_paths(self) -> list[str]:
        return list(
            dict.fromkeys(
                [
                    settings.USR_CLOUD_DEVICE_LIST_PATH,
                    "/usrCloud/device/list",
                    "/usrCloud/device/getList",
                    "/usrCloud/device/getDeviceList",
                    "/usrCloud/device/queryList",
                ]
            )
        )

    def _device_detail_paths(self) -> list[str]:
        return list(
            dict.fromkeys(
                [
                    settings.USR_CLOUD_DEVICE_DETAIL_PATH,
                    "/usrCloud/device/info",
                    "/usrCloud/device/getInfo",
                    "/usrCloud/device/getDeviceInfo",
                    "/usrCloud/device/detail",
                ]
            )
        )

    def status(self) -> dict[str, Any]:
        token_cached = self._token_state is not None and self._token_state.expires_at > datetime.now(
            timezone.utc
        )
        return {
            "enabled": settings.USR_CLOUD_ENABLED,
            "configured": self._is_configured(),
            "api_base_url": settings.USR_CLOUD_API_BASE_URL,
            "account_configured": bool(settings.USR_CLOUD_ACCOUNT),
            "app_key_configured": bool(settings.USR_CLOUD_APP_KEY),
            "token_cached": token_cached,
            "token_expires_at": (
                self._token_state.expires_at.isoformat() if token_cached and self._token_state else None
            ),
        }

    async def login(self, force_refresh: bool = False) -> UsrCloudTokenState:
        now = datetime.now(timezone.utc)
        if (
            not force_refresh
            and self._token_state is not None
            and self._token_state.expires_at > now + timedelta(seconds=30)
        ):
            return self._token_state

        if not self._is_configured():
            raise UsrCloudConfigurationError(
                "USR cloud account or password is not configured"
            )

        password_md5 = hashlib.md5(settings.USR_CLOUD_PASSWORD.encode("utf-8")).hexdigest()
        payload = {
            "account": settings.USR_CLOUD_ACCOUNT,
            "password": password_md5,
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(self._login_url(), json=payload)
        except httpx.HTTPError as exc:
            raise UsrCloudLoginError(f"USR cloud login request failed: {exc}") from exc

        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise UsrCloudLoginError(f"USR cloud login failed with HTTP {response.status_code}") from exc

        try:
            body = response.json()
        except ValueError as exc:
            raise UsrCloudLoginError("USR cloud login returned non-JSON response") from exc

        if not isinstance(body, dict):
            raise UsrCloudLoginError(
                f"USR cloud login returned unexpected JSON type: {type(body).__name__}"
            )

        data = body.get("data")
        data_dict = data if isinstance(data, dict) else {}

        token = body.get("token") or data_dict.get("token")
        uid_raw = body.get("uid") or data_dict.get("uid")
        sign_code = body.get("signCode") or data_dict.get("signCode")
        if not token:
            message = body.get("msg") or body.get("message") or response.text[:500] or "USR cloud login returned no token"
            raise UsrCloudLoginError(message)

        try:
            uid = int(uid_raw) if uid_raw is not None else None
        except (TypeError, ValueError):
            uid = None

        expires_at = now + timedelta(seconds=settings.USR_CLOUD_TOKEN_EXPIRE_SECONDS)
        self._token_state = UsrCloudTokenState(
            token=token,
            uid=uid,
            sign_code=sign_code,
            expires_at=expires_at,
        )
        return self._token_state

    async def authenticated_post(
        self,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        token_state = await self.login()
        url = f"{settings.USR_CLOUD_API_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                url,
                json=payload or {},
                headers={"token": token_state.token},
            )
        response.raise_for_status()
        return response.json()

    async def _try_authenticated_posts(
        self,
        paths: list[str],
        payload: dict[str, Any] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        last_error: Exception | None = None
        for path in paths:
            try:
                body = await self.authenticated_post(path=path, payload=payload)
                return path, body
            except httpx.HTTPStatusError as exc:
                last_error = exc
                # 404/405 更像路径不匹配，继续尝试候选路径。
                if exc.response.status_code in {404, 405}:
                    continue
                raise UsrCloudRequestError(
                    f"USR cloud request failed for {path} with HTTP {exc.response.status_code}"
                ) from exc
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                continue

        if last_error is None:
            raise UsrCloudRequestError("USR cloud request failed before any path was attempted")
        raise UsrCloudRequestError(
            "USR cloud request failed for all candidate paths"
        ) from last_error

    async def list_devices(
        self,
        page: int | None = None,
        page_size: int | None = None,
        project_id: str | None = None,
    ) -> tuple[str, dict[str, Any], list[dict[str, Any]], int | None]:
        payload: dict[str, Any] = {}
        if page is not None:
            payload["page"] = page
        if page_size is not None:
            payload["pageSize"] = page_size
        effective_project_id = project_id or settings.USR_CLOUD_PROJECT_ID
        if effective_project_id:
            payload["projectId"] = effective_project_id

        path_used, body = await self._try_authenticated_posts(self._device_list_paths(), payload)
        items, total = self._extract_items(body)
        return path_used, body, items, total

    async def get_device_detail(
        self,
        dev_id: str | None = None,
        device_id: str | None = None,
        device_no: str | None = None,
        cusdevice_no: str | None = None,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        payload = self._build_detail_payload(
            dev_id=dev_id or settings.USR_CLOUD_GATEWAY_ID,
            device_id=device_id or settings.USR_CLOUD_DEVICE_ID,
            device_no=device_no or settings.USR_CLOUD_DEVICE_NO,
            cusdevice_no=cusdevice_no or settings.USR_CLOUD_CUSDEVICE_NO,
        )
        if not payload:
            raise UsrCloudConfigurationError(
                "USR cloud detail query requires dev_id, device_id, device_no, or cusdevice_no"
            )

        path_used, body = await self._try_authenticated_posts(self._device_detail_paths(), payload)
        item = self._extract_item(body)
        return path_used, body, item


usr_cloud_service = UsrCloudService()
