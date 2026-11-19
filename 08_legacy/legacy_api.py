"""一个故意不好用的老订单接口：cookie 登录，分页叫 pageNo，金额是分。"""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ORDERS = [
    {"ordId": "ORD-001", "sts": 3, "amt": 29900},
    {"ordId": "ORD-002", "sts": 2, "amt": 59900},
    {"ordId": "ORD-003", "sts": 1, "amt": 129900},
    {"ordId": "ORD-004", "sts": 3, "amt": 2900},
]
SESSIONS = {"svc-token": "order-bot"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def _json(self, code: int, body: dict) -> None:
        raw = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self) -> None:
        if self.path != "/login":
            self._json(404, {"code": 404})
            return
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        if payload.get("username") != "order-bot":
            self._json(401, {"code": 401, "msg": "login failed"})
            return
        self.send_response(200)
        self.send_header("Set-Cookie", "sid=svc-token; Path=/")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"code":0}')

    def do_GET(self) -> None:
        cookie = self.headers.get("Cookie", "")
        if "sid=svc-token" not in cookie:
            self._json(401, {"code": 401, "msg": "no session"})
            return
        if not self.path.startswith("/api/orders"):
            self._json(404, {"code": 404})
            return
        from urllib.parse import parse_qs, urlparse

        query = parse_qs(urlparse(self.path).query)
        page_no = int(query.get("pageNo", ["1"])[0])
        page_size = int(query.get("pageSize", ["2"])[0])
        status = query.get("sts")
        rows = ORDERS
        if status:
            rows = [row for row in rows if row["sts"] == int(status[0])]
        start = (page_no - 1) * page_size
        self._json(200, {"code": 0, "data": {"total": len(rows), "rows": rows[start : start + page_size]}})


def serve(port: int = 8090) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    return server


if __name__ == "__main__":
    serve().serve_forever()
