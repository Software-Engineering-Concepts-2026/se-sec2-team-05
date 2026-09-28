from datetime import datetime, timezone
from .models import Comment


class CommentStorage:

    def __init__(self):
        self.comments: list[Comment] = []
        self.next_id = 1

    def create(
        self,
        note_id: int,
        user_id: int,
        content: str
    ) -> Comment:

        comment = Comment(
            id=self.next_id,
            note_id=note_id,
            user_id=user_id,
            content=content,
            created_at=datetime.now(timezone.utc)
        )

        self.comments.append(comment)
        self.next_id += 1

        return comment

    def get_by_note(self, note_id: int) -> list[Comment]:

        comments = [
            comment
            for comment in self.comments
            if comment.note_id == note_id
        ]

        # ล่าสุดอยู่ด้านบน
        comments.sort(
            key=lambda comment: comment.created_at,
            reverse=True
        )

        return comments

    def get_by_id(self, comment_id: int) -> Comment | None:

        for comment in self.comments:
            if comment.id == comment_id:
                return comment

        return None

    def delete(self, comment_id: int) -> bool:

        comment = self.get_by_id(comment_id)

        if comment is None:
            return False

        self.comments.remove(comment)

        return True