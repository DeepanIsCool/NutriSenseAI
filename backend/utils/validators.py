"""
Input validation and sanitisation utilities.

Called by every route handler before data reaches Gemini or Firestore
(Security pillar — validate and sanitize ALL user inputs).
"""

import re
from fastapi import HTTPException

_USER_ID_RE = re.compile(r"^[a-zA-Z0-9_\-]{1,128}$")
_DANGEROUS_PATTERNS = re.compile(
    r"(<script|javascript:|data:|vbscript:|on\w+=)", re.IGNORECASE
)


def validate_user_id(user_id: str) -> None:
    """
    Assert that a user ID matches the expected Firebase UID format.

    Args:
        user_id: Raw user ID string from the request.

    Raises:
        HTTPException 400 if the user ID is malformed.
    """
    if not _USER_ID_RE.match(user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id format.")


def sanitize_string(value: str) -> str:
    """
    Strip dangerous patterns from user-supplied text.

    Removes HTML/JS injection vectors before the value is embedded
    in Gemini prompts or stored in Firestore.

    Args:
        value: Raw user-supplied string.

    Returns:
        Sanitized string with dangerous content removed.
    """
    sanitized = _DANGEROUS_PATTERNS.sub("", value)
    # Collapse excessive whitespace
    return " ".join(sanitized.split())


def validate_image_size(size_bytes: int, max_mb: int = 5) -> None:
    """
    Assert that an image file does not exceed the maximum allowed size.

    Args:
        size_bytes: File size in bytes.
        max_mb: Maximum allowed size in megabytes (default 5).

    Raises:
        HTTPException 413 if the file is too large.
    """
    if size_bytes > max_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413, detail=f"File exceeds {max_mb}MB limit."
        )


def validate_calorie_range(calories: int) -> None:
    """
    Assert that a calorie value is within a physiologically plausible range.

    Args:
        calories: Daily calorie target.

    Raises:
        HTTPException 400 if out of range.
    """
    if not 800 <= calories <= 5000:
        raise HTTPException(status_code=400, detail="Calories must be between 800 and 5000.")
