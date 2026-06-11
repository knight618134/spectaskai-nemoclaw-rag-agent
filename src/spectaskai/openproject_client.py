from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class OpenProjectClient:
    """Minimal OpenProject API v3 boundary for future agent tools."""

    def __init__(self, host: str | None = None, api_token: str | None = None) -> None:
        self.host = (host or os.environ.get("OPENPROJECT_HOST") or "").rstrip("/")
        self.api_token = api_token or os.environ.get("OPENPROJECT_API_TOKEN")

    @property
    def configured(self) -> bool:
        return bool(self.host and self.api_token)

    def list_projects(self) -> dict[str, Any]:
        return self._request("GET", "/api/v3/projects")

    def list_work_packages(self, project_identifier: str, page_size: int = 10) -> dict[str, Any]:
        path = f"/api/v3/projects/{urllib.parse.quote(project_identifier)}/work_packages?pageSize={page_size}"
        return self._request("GET", path)

    def create_work_package(
        self,
        project_identifier: str,
        subject: str,
        description: str,
        type_href: str = "/api/v3/types/1",
    ) -> dict[str, Any]:
        payload = {
            "subject": subject,
            "description": {"format": "markdown", "raw": description},
            "_links": {"type": {"href": type_href}},
        }
        return self._request("POST", f"/api/v3/projects/{urllib.parse.quote(project_identifier)}/work_packages", payload)

    def add_comment(self, work_package_id: int | str, comment: str) -> dict[str, Any]:
        payload = {"comment": {"format": "markdown", "raw": comment}}
        return self._request("POST", f"/api/v3/work_packages/{work_package_id}/activities", payload)

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.configured:
            raise RuntimeError("OpenProject client is not configured. Set OPENPROJECT_HOST and OPENPROJECT_API_TOKEN.")

        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        token = base64.b64encode(f"apikey:{self.api_token}".encode("utf-8")).decode("ascii")
        request = urllib.request.Request(
            f"{self.host}{path}",
            data=data,
            method=method,
            headers={
                "Authorization": f"Basic {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenProject API returned HTTP {error.code}: {body}") from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"OpenProject request failed: {error.reason}") from error
