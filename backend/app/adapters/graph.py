from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx


class GraphError(RuntimeError):
    """A sanitized The Graph transport or GraphQL error."""


class GraphClient:
    def __init__(
        self,
        api_key: str,
        subgraph_id: str,
        timeout: float = 30.0,
    ) -> None:
        if not api_key:
            raise ValueError("GRAPH_API_KEY is missing")

        if not subgraph_id:
            raise ValueError("AAVE_V3_SUBGRAPH_ID is missing")

        self.url = f"https://gateway.thegraph.com/api/subgraphs/id/{subgraph_id}"
        self._api_key = api_key
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        self.timeout = timeout

    def query(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            response = httpx.post(
                self.url,
                headers=self._headers,
                json={"query": query, "variables": variables or {}},
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            raise GraphError(f"The Graph request failed: {self._sanitize(str(exc))}") from exc

        if response.status_code >= 400:
            raise GraphError(
                self._sanitize(f"The Graph HTTP {response.status_code}\nResponse: {response.text}")
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise GraphError(
                self._sanitize(f"The Graph returned invalid JSON: {response.text}")
            ) from exc

        if not isinstance(payload, Mapping):
            raise GraphError("The Graph returned a non-object JSON response")

        if payload.get("errors"):
            raise GraphError(
                self._sanitize(f"The Graph GraphQL error:\n{payload['errors']}")
            )

        data = payload.get("data")
        if not isinstance(data, dict):
            raise GraphError(self._sanitize(f"The Graph returned no data:\n{payload}"))

        return data

    def indexed_block(self) -> int:
        query = """
        query {
          _meta {
            block {
              number
              hash
            }
          }
        }
        """

        data = self.query(query)

        meta = data.get("_meta")
        if not isinstance(meta, dict) or not isinstance(meta.get("block"), dict):
            raise GraphError("Could not determine The Graph indexed block")
        try:
            return int(meta["block"]["number"])
        except (KeyError, TypeError, ValueError) as exc:
            raise GraphError("The Graph indexed block number is invalid") from exc

    def _sanitize(self, message: str) -> str:
        return message.replace(self._api_key, "[REDACTED]")
