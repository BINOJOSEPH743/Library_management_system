import re


def validate_password(password: str) -> str:
    """
    Validates the password based on specific rules.
    Returns "Valid" if the password passes all checks; otherwise, returns an error message.
    """
    if len(password) < 8 or len(password) > 20:
        return "Password must be 8–20 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must include at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must include at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return "Password must include at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must include at least one special character."
    if re.search(r"\s", password):
        return "Password must not contain whitespace."
    return "Valid"







