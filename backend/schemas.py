from datetime import datetime

from pydantic import BaseModel, field_validator


# ── Auth ──

class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── User ──

class UserResponse(BaseModel):
    id: int
    username: str
    avatar: str
    bio: str
    github_url: str
    is_admin: bool
    topic_count: int = 0
    comment_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    avatar: str | None = None
    bio: str | None = None
    github_url: str | None = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


# ── Tag ──

class TagResponse(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


# ── Topic ──

class TopicCreate(BaseModel):
    title: str
    content: str = ""
    tags: list[str] = []


class TopicUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None


# ── Comment ──

class CommentCreate(BaseModel):
    content: str
    topic_id: int
    parent_id: int | None = None


class CommentResponse(BaseModel):
    id: int
    content: str
    topic_id: int
    user_id: int
    username: str
    parent_id: int | None = None
    created_at: datetime
    replies: list["CommentResponse"] = []

    model_config = {"from_attributes": True}

    @field_validator("username", mode="before")
    @classmethod
    def extract_username(cls, v):
        return getattr(v, "username", v)


# ── Topic responses ──

class AuthorInfo(BaseModel):
    id: int
    username: str
    avatar: str

    model_config = {"from_attributes": True}


class TopicListResponse(BaseModel):
    id: int
    title: str
    author: AuthorInfo | None = None
    view_count: int = 0
    comment_count: int = 0
    likes_count: int = 0
    last_comment_at: datetime | None = None
    created_at: datetime
    tags: list[TagResponse] = []
    is_pinned: bool = False
    is_featured: bool = False

    model_config = {"from_attributes": True}


class TopicDetailResponse(BaseModel):
    id: int
    title: str
    content: str
    author: AuthorInfo | None = None
    view_count: int = 0
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    is_liked: bool = False
    comments: list[CommentResponse] = []
    tags: list[TagResponse] = []
    is_pinned: bool = False
    is_featured: bool = False

    model_config = {"from_attributes": True}


# ── User profile ──

class UserProfileResponse(BaseModel):
    id: int
    username: str
    avatar: str
    bio: str
    github_url: str
    topic_count: int = 0
    comment_count: int = 0
    created_at: datetime
    topics: list[TopicListResponse] = []

    model_config = {"from_attributes": True}


# ── Notification ──

class NotificationResponse(BaseModel):
    id: int
    type: str
    topic_id: int | None = None
    comment_id: int | None = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Message ──

class MessageCreate(BaseModel):
    receiver: str
    content: str


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    username: str
    avatar: str
    last_message: str
    last_message_at: datetime
    unread_count: int
