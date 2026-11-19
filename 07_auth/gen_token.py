"""签发一把演示用的 RSA JWT。私钥只留在进程里，公钥和 token 写到 .local/。"""

import json
from pathlib import Path

from fastmcp.server.auth.providers.jwt import RSAKeyPair

OUT = Path(__file__).resolve().parent / ".local"
ISSUER = "https://auth.example.com"
AUDIENCE = "http://127.0.0.1:8765/mcp"


def issue(scopes: list[str], subject: str, dept: str) -> dict:
    key_pair = RSAKeyPair.generate()
    token = key_pair.create_token(
        subject=subject,
        issuer=ISSUER,
        audience=AUDIENCE,
        scopes=scopes,
        expires_in_seconds=3600,
        additional_claims={"dept": dept},
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "public.pem").write_text(key_pair.public_key)
    (OUT / "token.txt").write_text(token)
    meta = {
        "issuer": ISSUER,
        "audience": AUDIENCE,
        "subject": subject,
        "dept": dept,
        "scopes": scopes,
    }
    (OUT / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    return meta


if __name__ == "__main__":
    print(issue(["employee:read", "budget:read"], subject="E001", dept="技术部"))
