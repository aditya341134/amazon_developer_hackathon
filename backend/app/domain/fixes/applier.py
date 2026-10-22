from __future__ import annotations

from typing import Any


def apply_patch(existing_patches: list[dict[str, Any]], patch: dict[str, Any]) -> list[dict[str, Any]]:
    # MVP: append patch; later you can de-duplicate by patch type.
    return [*existing_patches, patch]