# ============================================================
# Issue #14 - Comment on a Note
# User Story:
# ในฐานะสมาชิก ฉันต้องการแสดงความคิดเห็นใต้โน้ต
# เพื่อสอบถามหรือเสริมข้อมูลกับเจ้าของโน้ต
#
# Acceptance Criteria:
# 1. แสดงความคิดเห็นใต้โน้ตได้เมื่อเข้าสู่ระบบแล้ว
# 2. แสดงรายการความคิดเห็นเรียงตามเวลาล่าสุด
# 3. ลบความคิดเห็นของตัวเองได้
# ============================================================


from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

from .storage import CommentStorage
from .validation import validate_comment
from .identity import get_current_user


app = FastAPI(
    title="Comment Service",
    version="1.0.0"
)

storage = CommentStorage()


# -------------------------
# Request Model
# -------------------------

class CreateCommentRequest(BaseModel):
    content: str


# -------------------------
# Create Comment
# -------------------------

@app.post("/notes/{note_id}/comments", status_code=201)
def create_comment(
    note_id: int,
    request: CreateCommentRequest,
    user_id: int = Depends(get_current_user)
):
    try:
        content = validate_comment(request.content)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    comment = storage.create(
        note_id=note_id,
        user_id=user_id,
        content=content
    )

    return {
        "id": comment.id,
        "note_id": comment.note_id,
        "user_id": comment.user_id,
        "content": comment.content,
        "created_at": comment.created_at
    }


# -------------------------
# Get Comments
# -------------------------

@app.get("/notes/{note_id}/comments")
def get_comments(note_id: int):

    comments = storage.get_by_note(note_id)

    return {
        "comments": [
            {
                "id": comment.id,
                "note_id": comment.note_id,
                "user_id": comment.user_id,
                "content": comment.content,
                "created_at": comment.created_at
            }
            for comment in comments
        ]
    }


# -------------------------
# Delete Comment
# -------------------------

@app.delete(
    "/notes/{note_id}/comments/{comment_id}",
    status_code=204
)
def delete_comment(
    note_id: int,
    comment_id: int,
    user_id: int = Depends(get_current_user)
):

    comment = storage.get_by_id(comment_id)

    # ไม่พบ comment
    if comment is None or comment.note_id != note_id:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    # ตรวจว่าเป็นเจ้าของ comment หรือไม่
    if comment.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own comment"
        )

    storage.delete(comment_id)

    return None