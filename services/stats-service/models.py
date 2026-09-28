# ============================================================
# Issue #16 - View Own Note Stats
# ============================================================

from pydantic import BaseModel


class NoteStats(BaseModel):
    note_id: int
    owner_id: int
    views: int = 0
    downloads: int = 0