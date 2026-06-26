"""MassRelay queue — one assisted job per signer (v1 scaffold)."""

from dataclasses import dataclass


@dataclass
class MassRelayJob:
    petition_id: int
    user_id: int
    issue_id: int


async def enqueue_mass_relay(ctx, petition_id: int, signer_user_ids: list[int]) -> int:
    """ARQ worker entry — notify each signer to confirm submit on gorod.mos.ru."""
    count = 0
    for uid in signer_user_ids:
        # v1: push notification / email
        count += 1
    return count
