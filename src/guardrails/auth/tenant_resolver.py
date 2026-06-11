"""Tenant extraction from token"""

from __future__ import annotations

from typing import Optional

import jwt
from jwt import InvalidTokenError, ExpiredSignatureError


class TenantResolver:
    """Extract tenant from authentication token"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        tenant_claim: str = "tenant_id",
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.tenant_claim = tenant_claim

    def resolve(self, token: str) -> str:
        """Get tenant ID from token"""

        if not token:
            raise ValueError("Authentication token is required")

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                },
            )

            tenant_id: Optional[str] = payload.get(
                self.tenant_claim
            )

            if not tenant_id:
                raise PermissionError(
                    f"Missing '{self.tenant_claim}' claim"
                )

            return str(tenant_id)

        except ExpiredSignatureError as exc:
            raise PermissionError(
                "Authentication token has expired"
            ) from exc

        except InvalidTokenError as exc:
            raise PermissionError(
                f"Invalid authentication token: {exc}"
            ) from exc