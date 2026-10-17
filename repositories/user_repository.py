"""Resolve authenticated identities and load user profiles."""

import uuid
from datetime import datetime, timezone

from database.models import User, UserProfile
from sqlalchemy import select


class UserRepository:
    def __init__(self, sf):
        self.sf = sf

    def resolve(self, identity):
        with self.sf() as s:
            u = s.scalar(
                select(User).where(
                    User.provider == "google",
                    User.issuer == identity.issuer,
                    User.provider_subject == identity.subject,
                )
            )
            if not u:
                u = User(
                    provider="google",
                    issuer=identity.issuer,
                    provider_subject=identity.subject,
                    email=identity.email,
                    display_name=identity.name,
                    picture_url=identity.picture,
                )
                s.add(u)
                s.flush()
                s.add(UserProfile(user_id=u.id))
            else:
                u.email = identity.email
                u.display_name = identity.name
                u.picture_url = identity.picture
                u.last_login_at = datetime.now(timezone.utc)
            s.commit()
            s.refresh(u)
            return u

    def profile(self, user_id):
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        with self.sf() as s:
            return s.get(UserProfile, user_id)
