def validate_comment(content: str) -> str:
    if content is None:
        raise ValueError("Comment content is required")

    content = content.strip()

    if len(content) == 0:
        raise ValueError("Comment cannot be empty")

    if len(content) > 1000:
        raise ValueError("Comment must not exceed 1000 characters")

    return content