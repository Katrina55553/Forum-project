from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session, joinedload

from auth import hash_password
from models import Comment, Message, Notification, Tag, Topic, User, likes, topic_tags


# ── User ──

def create_user(db: Session, username: str, password: str) -> User:
    user = User(username=username, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter_by(username=username).first()


def update_user(db: Session, user: User, data: dict) -> User:
    for field in ("avatar", "bio", "github_url"):
        if data.get(field) is not None:
            setattr(user, field, data[field])
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, new_password: str) -> None:
    user.password_hash = hash_password(new_password)
    db.commit()


# ── Tag ──

def get_or_create_tags(db: Session, tag_names: list[str]) -> list[Tag]:
    """获取或创建标签，返回 Tag 对象列表"""
    tags = []
    for name in tag_names:
        name = name.strip()
        if not name:
            continue
        slug = name.lower().replace(" ", "-")
        tag = db.query(Tag).filter_by(slug=slug).first()
        if not tag:
            tag = Tag(name=name, slug=slug)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


def get_all_tags(db: Session) -> list[dict]:
    """获取所有标签及其帖子数量"""
    rows = (
        db.query(Tag, func.count(topic_tags.c.topic_id).label("count"))
        .outerjoin(topic_tags, Tag.id == topic_tags.c.tag_id)
        .group_by(Tag.id)
        .order_by(func.count(topic_tags.c.topic_id).desc())
        .all()
    )
    return [{"id": t.id, "name": t.name, "slug": t.slug, "count": c} for t, c in rows]


# ── Topic ──

def create_topic(db: Session, author_id: int, title: str, content: str, tag_names: list[str] = None) -> Topic:
    topic = Topic(title=title, content=content, author_id=author_id)
    db.add(topic)
    if tag_names:
        tags = get_or_create_tags(db, tag_names)
        topic.tags = tags
    db.query(User).filter_by(id=author_id).update({"topic_count": User.topic_count + 1})
    db.commit()
    db.refresh(topic)
    return topic


def _escape_like(s: str) -> str:
    """转义 LIKE/ILIKE 的特殊字符 % 和 _"""
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def get_topics(db: Session, page: int = 1, size: int = 10, q: str = "", tag: str = ""):
    # 先用简单查询计数（避免 joinedload 导致 count 膨胀）
    count_query = db.query(Topic)
    if q:
        escaped_q = _escape_like(q)
        count_query = count_query.filter(
            or_(
                Topic.title.ilike(f"%{escaped_q}%", escape="\\"),
                Topic.content.ilike(f"%{escaped_q}%", escape="\\"),
            )
        )
    if tag:
        count_query = count_query.filter(Topic.tags.any(Tag.slug == tag))
    total = count_query.count()

    # 再用 joinedload 查询实际数据
    query = db.query(Topic).options(joinedload(Topic.author), joinedload(Topic.tags))
    if q:
        escaped_q = _escape_like(q)
        query = query.filter(
            or_(
                Topic.title.ilike(f"%{escaped_q}%", escape="\\"),
                Topic.content.ilike(f"%{escaped_q}%", escape="\\"),
            )
        )
    if tag:
        query = query.filter(Topic.tags.any(Tag.slug == tag))
    topics = (
        query.order_by(Topic.is_pinned.desc(), Topic.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    result = []
    for t in topics:
        comment_count = db.query(func.count(Comment.id)).filter_by(topic_id=t.id).scalar()
        like_count = db.query(func.count(likes.c.user_id)).filter(likes.c.topic_id == t.id).scalar()
        last_comment = (
            db.query(Comment).filter_by(topic_id=t.id).order_by(Comment.created_at.desc()).first()
        )
        result.append({
            "id": t.id,
            "title": t.title,
            "author": {"id": t.author.id, "username": t.author.username, "avatar": t.author.avatar} if t.author else None,
            "view_count": t.view_count,
            "comment_count": comment_count,
            "likes_count": like_count,
            "last_comment_at": last_comment.created_at if last_comment else None,
            "tags": [{"id": tag.id, "name": tag.name, "slug": tag.slug} for tag in t.tags],
            "created_at": t.created_at,
            "is_pinned": t.is_pinned,
            "is_featured": t.is_featured,
        })
    return result, total


def get_topic_by_id(db: Session, topic_id: int) -> Topic | None:
    return (
        db.query(Topic)
        .options(
            joinedload(Topic.author),
            joinedload(Topic.comments).joinedload(Comment.author),
            joinedload(Topic.likes),
            joinedload(Topic.tags),
        )
        .filter_by(id=topic_id)
        .first()
    )


def get_topic_for_edit(db: Session, topic_id: int) -> Topic | None:
    return db.query(Topic).options(joinedload(Topic.author)).filter_by(id=topic_id).first()


def get_topics_by_user(db: Session, user_id: int, page: int = 1, size: int = 10):
    query = db.query(Topic).options(joinedload(Topic.author)).filter_by(author_id=user_id)
    total = query.count()
    topics = (
        query.order_by(Topic.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    result = []
    for t in topics:
        comment_count = db.query(func.count(Comment.id)).filter_by(topic_id=t.id).scalar()
        like_count = db.query(func.count(likes.c.user_id)).filter(likes.c.topic_id == t.id).scalar()
        result.append({
            "id": t.id,
            "title": t.title,
            "author": {"id": t.author.id, "username": t.author.username, "avatar": t.author.avatar} if t.author else None,
            "view_count": t.view_count,
            "comment_count": comment_count,
            "likes_count": like_count,
            "last_comment_at": None,
            "created_at": t.created_at,
        })
    return result, total


def update_topic(db: Session, topic: Topic, data: dict) -> Topic:
    for field in ("title", "content"):
        if data.get(field) is not None:
            setattr(topic, field, data[field])
    if "tags" in data and data["tags"] is not None:
        tags = get_or_create_tags(db, data["tags"])
        topic.tags = tags
    db.commit()
    db.refresh(topic)
    return topic


def delete_topic(db: Session, topic: Topic) -> None:
    user_id = topic.author_id
    db.delete(topic)
    db.query(User).filter_by(id=user_id).update(
        {"topic_count": case((User.topic_count > 0, User.topic_count - 1), else_=0)}
    )
    db.commit()


def increment_view_count(db: Session, topic: Topic) -> None:
    db.query(Topic).filter_by(id=topic.id).update(
        {"view_count": Topic.view_count + 1}
    )
    db.commit()


def toggle_topic_pin(db: Session, topic: Topic) -> Topic:
    topic.is_pinned = not topic.is_pinned
    db.commit()
    db.refresh(topic)
    return topic


def toggle_topic_featured(db: Session, topic: Topic) -> Topic:
    topic.is_featured = not topic.is_featured
    db.commit()
    db.refresh(topic)
    return topic


# ── Like ──

def like_topic(db: Session, user_id: int, topic_id: int) -> dict:
    from sqlalchemy.exc import IntegrityError
    try:
        db.execute(likes.insert().values(user_id=user_id, topic_id=topic_id))
        db.commit()
    except IntegrityError:
        db.rollback()
    count = db.query(func.count(likes.c.user_id)).filter(likes.c.topic_id == topic_id).scalar()
    return {"liked": True, "likes_count": count}


def unlike_topic(db: Session, user_id: int, topic_id: int) -> dict:
    db.execute(likes.delete().where(likes.c.user_id == user_id, likes.c.topic_id == topic_id))
    db.commit()
    count = db.query(func.count(likes.c.user_id)).filter(likes.c.topic_id == topic_id).scalar()
    return {"liked": False, "likes_count": count}


# ── Comment ──

def create_comment(db: Session, user_id: int, topic_id: int, content: str, parent_id: int | None = None) -> Comment:
    if parent_id:
        parent = db.query(Comment).filter_by(id=parent_id, topic_id=topic_id).first()
        if not parent:
            raise ValueError("Parent comment not found under this topic")
    comment = Comment(content=content, topic_id=topic_id, user_id=user_id, parent_id=parent_id)
    db.add(comment)
    db.query(User).filter_by(id=user_id).update({"comment_count": User.comment_count + 1})

    # Notify topic author (don't self-notify)
    topic = db.query(Topic).filter_by(id=topic_id).first()
    if topic and topic.author_id != user_id:
        notif = Notification(
            user_id=topic.author_id,
            type="reply",
            topic_id=topic_id,
            comment_id=comment.id,
        )
        db.add(notif)

    # Notify parent comment author (don't self-notify, don't double-notify topic author)
    if parent_id and parent and parent.user_id != user_id and parent.user_id != topic.author_id:
        notif = Notification(
            user_id=parent.user_id,
            type="reply",
            topic_id=topic_id,
            comment_id=comment.id,
        )
        db.add(notif)

    # 单事务提交，保证评论与通知的原子性
    db.commit()
    db.refresh(comment)
    return comment


def get_comment_by_id(db: Session, comment_id: int) -> Comment | None:
    return db.query(Comment).filter_by(id=comment_id).first()


def delete_comment(db: Session, comment: Comment) -> None:
    # 收集所有子评论（包括嵌套的）
    def _collect_replies(c):
        result = [c]
        # 确保 replies 已加载
        for r in (c.replies or []):
            result.extend(_collect_replies(r))
        return result

    # 预加载 replies 关系
    db.refresh(comment)
    all_comments = _collect_replies(comment)

    # 为每个评论作者减少计数
    for c in all_comments:
        db.query(User).filter_by(id=c.user_id).update(
            {"comment_count": case((User.comment_count > 0, User.comment_count - 1), else_=0)}
        )
    db.delete(comment)
    db.commit()


def build_comment_tree(comments: list[Comment]) -> list[dict]:
    lookup = {}
    roots = []
    for c in comments:
        node = {
            "id": c.id,
            "content": c.content,
            "topic_id": c.topic_id,
            "user_id": c.user_id,
            "username": c.username,
            "parent_id": c.parent_id,
            "created_at": c.created_at,
            "replies": [],
        }
        lookup[c.id] = node

    for node in lookup.values():
        pid = node["parent_id"]
        if pid and pid in lookup:
            lookup[pid]["replies"].append(node)
        else:
            roots.append(node)

    return roots


# ── User Profile ──

def get_user_profile(db: Session, username: str) -> dict | None:
    user = db.query(User).filter_by(username=username).first()
    if not user:
        return None
    topics, _ = get_topics_by_user(db, user.id, page=1, size=20)
    return {"user": user, "topics": topics}


# ── Notification ──

def get_notifications(db: Session, user_id: int, page: int = 1, size: int = 20):
    query = db.query(Notification).filter_by(user_id=user_id)
    total = query.count()
    items = (
        query.order_by(Notification.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return items, total


def get_unread_notification_count(db: Session, user_id: int) -> int:
    return db.query(func.count(Notification.id)).filter_by(user_id=user_id, is_read=False).scalar()


def mark_notification_read(db: Session, notif_id: int, user_id: int) -> None:
    db.query(Notification).filter_by(id=notif_id, user_id=user_id).update({"is_read": True})
    db.commit()


def mark_all_notifications_read(db: Session, user_id: int) -> None:
    db.query(Notification).filter_by(user_id=user_id, is_read=False).update({"is_read": True})
    db.commit()


# ── Message ──

def send_message(db: Session, sender_id: int, receiver_username: str, content: str) -> Message | None:
    receiver = db.query(User).filter_by(username=receiver_username).first()
    if not receiver or receiver.id == sender_id:
        return None
    message = Message(sender_id=sender_id, receiver_id=receiver.id, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_conversations(db: Session, user_id: int) -> list[dict]:
    """获取会话列表（按最后消息时间排序）"""
    # 子查询：获取每个对话用户的最新消息 ID
    latest_sq = (
        db.query(
            case(
                (Message.sender_id == user_id, Message.receiver_id),
                else_=Message.sender_id
            ).label("other_id"),
            func.max(Message.id).label("last_msg_id"),
        )
        .filter(or_(Message.sender_id == user_id, Message.receiver_id == user_id))
        .group_by("other_id")
        .subquery()
    )

    # 子查询：每个对话用户的未读消息数
    unread_sq = (
        db.query(
            Message.sender_id.label("other_id"),
            func.count(Message.id).label("cnt"),
        )
        .filter(Message.receiver_id == user_id, Message.is_read == False)
        .group_by(Message.sender_id)
        .subquery()
    )

    # 主查询：最新消息 + 用户信息 + 未读数
    rows = (
        db.query(
            User.username,
            User.avatar,
            Message.content,
            Message.created_at,
            func.coalesce(unread_sq.c.cnt, 0).label("unread_count"),
        )
        .join(latest_sq, User.id == latest_sq.c.other_id)
        .join(Message, Message.id == latest_sq.c.last_msg_id)
        .outerjoin(unread_sq, unread_sq.c.other_id == User.id)
        .order_by(Message.created_at.desc())
        .all()
    )

    return [
        {
            "username": r.username,
            "avatar": r.avatar or "",
            "last_message": (r.content or "")[:50],
            "last_message_at": r.created_at.isoformat() if r.created_at else "",
            "unread_count": r.unread_count or 0,
        }
        for r in rows
    ]


def get_messages_with_user(db: Session, user_id: int, other_username: str, page: int = 1, size: int = 50) -> dict | None:
    other_user = db.query(User).filter_by(username=other_username).first()
    if not other_user:
        return None

    query = db.query(Message).filter(
        or_(
            (Message.sender_id == user_id) & (Message.receiver_id == other_user.id),
            (Message.sender_id == other_user.id) & (Message.receiver_id == user_id),
        )
    )
    total = query.count()
    messages = (
        query.order_by(Message.created_at.asc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return {
        "messages": [
            {
                "id": msg.id,
                "sender_id": msg.sender_id,
                "receiver_id": msg.receiver_id,
                "content": msg.content,
                "is_read": msg.is_read,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ],
        "other_user": {"id": other_user.id, "username": other_user.username, "avatar": other_user.avatar or ""},
        "total": total,
    }


def mark_messages_read(db: Session, user_id: int, other_username: str) -> None:
    other_user = db.query(User).filter_by(username=other_username).first()
    if other_user:
        db.query(Message).filter(
            Message.sender_id == other_user.id,
            Message.receiver_id == user_id,
            Message.is_read == False,
        ).update({"is_read": True})
        db.commit()


def get_unread_message_count(db: Session, user_id: int) -> int:
    return db.query(func.count(Message.id)).filter(
        Message.receiver_id == user_id,
        Message.is_read == False,
    ).scalar()
