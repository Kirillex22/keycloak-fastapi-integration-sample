from fastapi import APIRouter, Depends, HTTPException
from src.orm import Post
from src.schemas import PostCreate, PostView
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from src.dependencies import get_db, get_current_user

posts_router = APIRouter()

@posts_router.post("/create", response_model=PostView)
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    owner_id = current_user.get("sub") if isinstance(current_user, dict) else getattr(current_user, "id", None)
    if not owner_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    new_post = Post(
        id=str(uuid4()),
        title=post.title,
        content=post.content,
        owner_id=owner_id
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return PostView.from_orm(new_post)

@posts_router.get("/{post_id}", response_model=PostView)
async def read_post(
    post_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.get(Post, post_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostView.from_orm(result)

@posts_router.delete("/{post_id}")
async def delete_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    post = await db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    owner_id = current_user.get("sub") if isinstance(current_user, dict) else getattr(current_user, "id", None)
    if post.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    await db.delete(post)
    await db.commit()
    return {"message": "Post deleted successfully"}