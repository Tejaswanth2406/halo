"""JWT identity resolution"""

from __future__ import annotations

from typing import Dict, Any, Optional
from datetime import datetime, timezone

import jwt
from jwt import (
    ExpiredSignatureError,
    InvalidTokenError,
    InvalidSignatureError,
)


class IdentityResolver:
    """Validate and resolve JWT tokens"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        issuer: Optional[str] = None,
        audience: Optional[str] = None,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.issuer = issuer
        self.audience = audience

    def resolve(self, token: str) -> Dict[str, Any]:
        """Resolve user identity from JWT"""

        if not token:
            raise ValueError("JWT token is required")

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience,
                options={
                    "require": ["exp", "iat", "sub"],
                    "verify_signature": True,
                    "verify_exp": True,
                },
            )

            return {
                "user_id": payload["sub"],
                "email": payload.get("email"),
                "name": payload.get("name"),
                "roles": payload.get("roles", []),
                "tenant_id": payload.get("tenant_id"),
                "issued_at": payload.get("iat"),
                "expires_at": payload.get("exp"),
                "authenticated": True,
                "token_valid": True,
                "resolved_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                "claims": payload,
            }

        except ExpiredSignatureError as exc:
            raise PermissionError(
                "JWT token has expired"
            ) from exc

        except InvalidSignatureError as exc:
            raise PermissionError(
                "JWT signature validation failed"
            ) from exc

        except InvalidTokenError as exc:
            raise PermissionError(
                f"Invalid JWT token: {exc}"
            ) from exc