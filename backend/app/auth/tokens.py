# Stub for later (auth is not enforced yet).
# We keep this file because Alexa+ QuickStart expects OAuth flow eventually.

from __future__ import annotations

from dataclasses import dataclass
from time import time
from typing import Any
from app.util.ids import new_id


@dataclass
class AccessToken:
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    issued_at: int = int(time())


def mint_token() -> AccessToken:
    return AccessToken(access_token=new_id("tok"))