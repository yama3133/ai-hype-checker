"""AgentCore Gateway 経由の Web 検索ツール。

Gateway (AWS_IAM 認可) の MCP エンドポイントに SigV4 署名付きで
tools/call を投げ、Web Search コネクタ (web-search) の結果を返す。
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

DEFAULT_GATEWAY_URL = (
    "https://ai-hype-checker-gw-rfmipak2bb.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
)
TOOL_NAME = "web-search-tool___WebSearch"
# コスト増幅攻撃対策: プロンプトで誘導されてもコード側で件数を制限する
MAX_RESULTS_CAP = 5


def _post_signed(payload: dict) -> dict:
    url = os.environ.get("WEB_SEARCH_GATEWAY_URL", DEFAULT_GATEWAY_URL)
    region = os.environ.get("AWS_REGION", "us-east-1")
    body = json.dumps(payload).encode()
    creds = boto3.Session().get_credentials().get_frozen_credentials()
    req = AWSRequest(
        method="POST",
        url=url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    SigV4Auth(creds, "bedrock-agentcore", region).add_auth(req)
    http_req = urllib.request.Request(url, data=body, headers=dict(req.headers), method="POST")
    with urllib.request.urlopen(http_req, timeout=60) as resp:
        raw = resp.read().decode()
    # Gateway は Accept 次第で SSE を返すことがあるので data: 行にも対応する
    for line in raw.splitlines():
        if line.startswith("data:"):
            return json.loads(line[5:].strip())
    return json.loads(raw)


def search(query: str, max_results: int = 3) -> dict:
    """GatewayのWebSearchツールを呼び、title/url/text/published_dateのリストを返す。"""
    query = (query or "").strip()[:200]
    if not query:
        return {"error": "query is empty", "results": []}
    max_results = max(1, min(int(max_results), MAX_RESULTS_CAP))
    try:
        rpc = _post_signed(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": TOOL_NAME,
                    "arguments": {"query": query, "maxResults": max_results},
                },
            }
        )
    except (urllib.error.URLError, OSError, ValueError):
        return {"error": "web search failed", "results": []}

    result = rpc.get("result", {})
    if result.get("isError"):
        return {"error": "web search returned an error", "results": []}
    items = []
    for content in result.get("content", []):
        if content.get("type") != "text":
            continue
        try:
            data = json.loads(content["text"])
        except (ValueError, TypeError):
            continue
        for r in data.get("results", []):
            items.append(
                {
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "text": (r.get("text") or "")[:500],
                    "published_date": r.get("publishedDate"),
                }
            )
    return {"results": items}
