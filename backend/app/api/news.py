"""News API: CRUD for admin, read for all authenticated users."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func

from app.api.deps import CurrentUser, require_admin
from app.db.session import get_session
from app.models.news import News
from app.schemas.news import NewsCreate, NewsUpdate, NewsResponse, NewsListResponse

router = APIRouter(prefix="/news", tags=["news"])


# ===== Public endpoints (for authenticated users) =====

@router.get("", response_model=NewsListResponse)
def list_news(
    current_user: CurrentUser,
    session: Session = Depends(get_session),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    """Get list of published news. Available to all authenticated users."""
    query = select(News).where(News.is_published == True).order_by(News.created_at.desc())
    
    total = session.exec(select(func.count()).select_from(query.subquery())).one()
    news = session.exec(query.offset(offset).limit(limit)).all()
    
    return NewsListResponse(
        news=[NewsResponse.model_validate(n) for n in news],
        total=total
    )


@router.get("/{news_id}", response_model=NewsResponse)
def get_news(
    news_id: int,
    current_user: CurrentUser,
    session: Session = Depends(get_session),
):
    """Get single news item by ID."""
    news = session.get(News, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Non-admin can only see published news
    if current_user.role != "admin" and not news.is_published:
        raise HTTPException(status_code=404, detail="News not found")
    
    return NewsResponse.model_validate(news)


# ===== Admin endpoints =====

@router.get("/admin/all", response_model=NewsListResponse)
def list_all_news_admin(
    current_user: CurrentUser,
    session: Session = Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get all news including unpublished. Admin only."""
    require_admin(current_user)
    
    query = select(News).order_by(News.created_at.desc())
    total = session.exec(select(func.count()).select_from(query.subquery())).one()
    news = session.exec(query.offset(offset).limit(limit)).all()
    
    return NewsListResponse(
        news=[NewsResponse.model_validate(n) for n in news],
        total=total
    )


def _detect_media(url: str | None) -> tuple[str | None, str | None]:
    """Return (media_url, media_type) based on raw URL."""
    if not url:
        return None, None
    lower = url.lower()
    if "youtube.com" in lower or "youtu.be" in lower:
        return url, "youtube"
    # naive image detection by extension; still optional on frontend
    if lower.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
        return url, "image"
    # fallback: treat as image for arbitrary image URLs
    return url, "image"


@router.post("", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
def create_news(
    body: NewsCreate,
    current_user: CurrentUser,
    session: Session = Depends(get_session),
):
    """Create new news item. Admin only."""
    require_admin(current_user)
    
    # Determine effective media from provided fields (prefer media_url, then video/image)
    raw_url = body.media_url or body.video_url or body.image_url
    media_url, media_type = _detect_media(raw_url)

    # Backwards-compatible: also populate legacy video_url/image_url
    legacy_video_url: str | None = None
    legacy_image_url: str | None = None
    if media_type == "youtube":
        legacy_video_url = media_url
    elif media_type == "image":
        legacy_image_url = media_url

    news = News(
        title_ru=body.title_ru,
        title_kz=body.title_kz,
        content_ru=body.content_ru,
        content_kz=body.content_kz,
        video_url=legacy_video_url,
        image_url=legacy_image_url,
        media_url=media_url,
        media_type=media_type,
        is_published=body.is_published,
        author_id=current_user.id,
    )
    session.add(news)
    session.commit()
    session.refresh(news)
    
    return NewsResponse.model_validate(news)


@router.patch("/{news_id}", response_model=NewsResponse)
def update_news(
    news_id: int,
    body: NewsUpdate,
    current_user: CurrentUser,
    session: Session = Depends(get_session),
):
    """Update news item. Admin only."""
    require_admin(current_user)
    
    news = session.get(News, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    if body.title_ru is not None:
        news.title_ru = body.title_ru
    if body.title_kz is not None:
        news.title_kz = body.title_kz
    if body.content_ru is not None:
        news.content_ru = body.content_ru
    if body.content_kz is not None:
        news.content_kz = body.content_kz

    # Media update: prefer explicit media_url, otherwise fall back to legacy fields for compatibility
    new_raw_url: str | None = None
    if body.media_url is not None:
        # empty string should clear media
        new_raw_url = body.media_url or None
    elif body.video_url is not None or body.image_url is not None:
        # if legacy fields come in, combine them
        new_raw_url = body.video_url or body.image_url

    if new_raw_url is not None:
        media_url, media_type = _detect_media(new_raw_url)
        news.media_url = media_url
        news.media_type = media_type
        # keep legacy columns in sync for old clients
        news.video_url = media_url if media_type == "youtube" else None
        news.image_url = media_url if media_type == "image" else None

    if body.is_published is not None:
        news.is_published = body.is_published
    
    news.updated_at = datetime.utcnow()
    session.add(news)
    session.commit()
    session.refresh(news)
    
    return NewsResponse.model_validate(news)


@router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news(
    news_id: int,
    current_user: CurrentUser,
    session: Session = Depends(get_session),
):
    """Delete news item. Admin only."""
    require_admin(current_user)
    
    news = session.get(News, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    session.delete(news)
    session.commit()
