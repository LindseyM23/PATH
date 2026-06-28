from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Category]:
    return (
        db.query(Category)
        .filter(Category.user_id == current_user.id, Category.is_archived.is_(False))
        .order_by(Category.sort_order)
        .all()
    )


# Add/edit/delete category endpoints are a Feature 2+ extension point — not needed
# for the Feature 1 (Payday Setup) slice this pass covers.
