"""Establish the Phase 1A migration history without creating domain tables.

Revision ID: 0001_phase1a_baseline
Revises:
Create Date: 2026-11-06
"""

from typing import Sequence

from alembic import op

revision: str = "0001_phase1a_baseline"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the baseline revision; Phase 1 entities arrive in later milestones."""


def downgrade() -> None:
    """Remove the baseline revision; no domain schema is present yet."""
