"""
Database module for the Fake News Detector API.

This module provides functions for interacting with the database.
"""

import json
import os
import uuid
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from passlib.context import CryptContext

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database paths
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db")
USERS_FILE = os.path.join(DB_DIR, "users.json")
ANALYSES_FILE = os.path.join(DB_DIR, "analyses.json")
RESET_TOKENS_FILE = os.path.join(DB_DIR, "reset_tokens.json")

# Create database directory if it doesn't exist
os.makedirs(DB_DIR, exist_ok=True)

# Initialize database files if they don't exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(ANALYSES_FILE):
    with open(ANALYSES_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(RESET_TOKENS_FILE):
    with open(RESET_TOKENS_FILE, "w") as f:
        json.dump({}, f)


def get_password_hash(password: str) -> str:
    """
    Hash a password.

    Args:
        password: The password to hash

    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: The plain text password
        hashed_password: The hashed password

    Returns:
        bool: True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_users() -> Dict[str, Dict[str, Any]]:
    """
    Get all users.

    Returns:
        Dict: The users
    """
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by email.

    Args:
        email: The email of the user

    Returns:
        Dict: The user, or None if not found
    """
    users = get_users()
    for user_id, user in users.items():
        if user["email"] == email:
            user["id"] = user_id
            return user
    return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by ID.

    Args:
        user_id: The ID of the user

    Returns:
        Dict: The user, or None if not found
    """
    users = get_users()
    if user_id in users:
        user = users[user_id]
        user["id"] = user_id
        return user
    return None


def create_user(email: str, username: str, password: str, full_name: str, is_google_user: bool = False) -> Dict[str, Any]:
    """
    Create a new user.

    Args:
        email: The email of the user
        username: The username of the user
        password: The password of the user
        full_name: The full name of the user
        is_google_user: Whether the user is a Google user (default: False)

    Returns:
        Dict: The created user
    """
    users = get_users()

    # Check if email already exists
    for user in users.values():
        if user["email"] == email:
            raise ValueError("Email already registered")

    # Create user
    user_id = str(uuid.uuid4())
    user = {
        "email": email,
        "username": username,
        "hashed_password": get_password_hash(password),
        "full_name": full_name,
        "is_google_user": is_google_user,
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "is_active": True,
        "is_admin": False  # Default to non-admin
    }

    # Save user
    users[user_id] = user
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

    # Return user with ID
    user["id"] = user_id
    return user


def update_user_last_login(user_id: str) -> None:
    """
    Update a user's last login time.

    Args:
        user_id: The ID of the user
    """
    users = get_users()
    if user_id in users:
        users[user_id]["last_login"] = datetime.now().isoformat()
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)


def get_analyses() -> Dict[str, Dict[str, Any]]:
    """
    Get all analyses.

    Returns:
        Dict: The analyses
    """
    with open(ANALYSES_FILE, "r") as f:
        return json.load(f)


def get_analysis_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
    """
    Get an analysis by ID.

    Args:
        analysis_id: The ID of the analysis

    Returns:
        Dict: The analysis, or None if not found
    """
    analyses = get_analyses()
    if analysis_id in analyses:
        analysis = analyses[analysis_id]
        analysis["id"] = analysis_id
        return analysis
    return None


def get_analyses_by_user(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all analyses for a user.

    Args:
        user_id: The ID of the user

    Returns:
        List: The analyses
    """
    analyses = get_analyses()
    user_analyses = []

    for analysis_id, analysis in analyses.items():
        if analysis["user_id"] == user_id:
            analysis["id"] = analysis_id
            user_analyses.append(analysis)

    # Sort by created_at (newest first)
    user_analyses.sort(key=lambda x: x["created_at"], reverse=True)

    return user_analyses


def create_analysis(
    user_id: str,
    content_type: str,
    content: str,
    title: Optional[str],
    url: Optional[str],
    prediction: str,
    confidence: float,
    trust_score: float,
    trust_level: str,
    factors: Dict[str, Any],
    details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new analysis.

    Args:
        user_id: The ID of the user
        content_type: The type of content ("text" or "url")
        content: The content
        title: The title (for URLs)
        url: The URL (for URLs)
        prediction: The prediction
        confidence: The confidence
        trust_score: The trust score
        trust_level: The trust level
        factors: The factors
        details: The details

    Returns:
        Dict: The created analysis
    """
    analyses = get_analyses()

    # Create analysis
    analysis_id = str(uuid.uuid4())
    analysis = {
        "user_id": user_id,
        "content_type": content_type,
        "content": content,
        "title": title,
        "url": url,
        "prediction": prediction,
        "confidence": confidence,
        "trust_score": trust_score,
        "trust_level": trust_level,
        "factors": factors,
        "details": details,
        "created_at": datetime.now().isoformat()
    }

    # Save analysis
    analyses[analysis_id] = analysis
    with open(ANALYSES_FILE, "w") as f:
        json.dump(analyses, f, indent=2)

    # Return analysis with ID
    analysis["id"] = analysis_id
    return analysis


def get_user_profile(user_id: str) -> Dict[str, Any]:
    """
    Get a user's profile.

    Args:
        user_id: The ID of the user

    Returns:
        Dict: The user profile
    """
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")

    analyses = get_analyses_by_user(user_id)

    # Calculate average trust score
    if analyses:
        average_trust_score = sum(a["trust_score"] for a in analyses) / len(analyses)
    else:
        average_trust_score = 0

    return {
        "user": user,
        "analysis_count": len(analyses),
        "recent_analyses": analyses[:5],  # Get 5 most recent analyses
        "average_trust_score": average_trust_score
    }


def create_password_reset_token(email: str) -> Optional[str]:
    """
    Create a password reset token for a user.

    Args:
        email: The email of the user

    Returns:
        str: The reset token, or None if the user was not found
    """
    user = get_user_by_email(email)
    if not user:
        return None

    # Generate a secure token
    token = secrets.token_urlsafe(32)

    # Load existing tokens
    with open(RESET_TOKENS_FILE, "r") as f:
        tokens = json.load(f)

    # Add the new token with expiration (24 hours from now)
    tokens[token] = {
        "user_id": user["id"],
        "email": email,
        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
    }

    # Save tokens
    with open(RESET_TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

    return token


def verify_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token.

    Args:
        token: The reset token

    Returns:
        str: The user ID if the token is valid, None otherwise
    """
    # Load tokens
    with open(RESET_TOKENS_FILE, "r") as f:
        tokens = json.load(f)

    # Check if token exists
    if token not in tokens:
        return None

    token_data = tokens[token]

    # Check if token has expired
    expires_at = datetime.fromisoformat(token_data["expires_at"])
    if datetime.now() > expires_at:
        # Remove expired token
        del tokens[token]
        with open(RESET_TOKENS_FILE, "w") as f:
            json.dump(tokens, f, indent=2)
        return None

    return token_data["user_id"]


def reset_password(token: str, new_password: str) -> bool:
    """
    Reset a user's password using a reset token.

    Args:
        token: The reset token
        new_password: The new password

    Returns:
        bool: True if the password was reset, False otherwise
    """
    user_id = verify_reset_token(token)
    if not user_id:
        return False

    # Load users
    users = get_users()

    # Update password
    if user_id in users:
        users[user_id]["hashed_password"] = get_password_hash(new_password)

        # Save users
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)

        # Remove the used token
        with open(RESET_TOKENS_FILE, "r") as f:
            tokens = json.load(f)

        if token in tokens:
            del tokens[token]

            with open(RESET_TOKENS_FILE, "w") as f:
                json.dump(tokens, f, indent=2)

        return True

    return False
