# ============================================================
# Issue #16 - View Own Note Stats
# ============================================================

from models import NoteStats


class StatsStorage:

    def __init__(self):
        self.stats: list[NoteStats] = []

    # --------------------------------------------------------
    # Issue #16 - Get statistics for a note
    # --------------------------------------------------------

    def get_by_note(self, note_id: int) -> NoteStats | None:

        for stat in self.stats:
            if stat.note_id == note_id:
                return stat

        return None

    # --------------------------------------------------------
    # Issue #16 - Create statistics for a note
    # --------------------------------------------------------

    def create(
        self,
        note_id: int,
        owner_id: int
    ) -> NoteStats:

        stat = NoteStats(
            note_id=note_id,
            owner_id=owner_id,
            views=0,
            downloads=0
        )

        self.stats.append(stat)

        return stat

    # --------------------------------------------------------
    # Issue #16 - Add view count
    # --------------------------------------------------------

    def add_view(self, note_id: int) -> NoteStats | None:

        stat = self.get_by_note(note_id)

        if stat is None:
            return None

        stat.views += 1

        return stat

    # --------------------------------------------------------
    # Issue #16 - Add download count
    # --------------------------------------------------------

    def add_download(self, note_id: int) -> NoteStats | None:

        stat = self.get_by_note(note_id)

        if stat is None:
            return None

        stat.downloads += 1

        return stat