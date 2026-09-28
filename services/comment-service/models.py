from dataclasses import dataclass
from datetime import datetime


@dataclass
class Comment:
    id: int
    note_id: int
    user_id: int
    content: str
    created_at: datetime