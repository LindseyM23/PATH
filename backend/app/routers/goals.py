import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.goal import Goal
from app.models.user import User
from app.schemas.goal import ContributeRequest, GoalCreate, GoalOut

router = APIRouter(prefix="/goals", tags=["goals"])


def _get_owned_goal(db: Session, user_id: uuid.UUID, goal_id: uuid.UUID) -> Goal:
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
    if goal is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Goal not found")
    return goal


@router.post("", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Goal:
    goal = Goal(
        user_id=current_user.id,
        name=payload.name,
        target_amount=payload.target_amount,
        icon=payload.icon,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("", response_model=list[GoalOut])
def list_goals(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[Goal]:
    return (
        db.query(Goal)
        .filter(Goal.user_id == current_user.id)
        .order_by(Goal.created_at)
        .all()
    )


@router.post("/{goal_id}/contribute", response_model=GoalOut)
def contribute_to_goal(
    goal_id: uuid.UUID,
    payload: ContributeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Goal:
    goal = _get_owned_goal(db, current_user.id, goal_id)
    goal.current_amount += payload.amount
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    goal = _get_owned_goal(db, current_user.id, goal_id)
    db.delete(goal)
    db.commit()
