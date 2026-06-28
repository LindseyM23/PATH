import uuid

from sqlalchemy.orm import Session

from app.models.category import Category, CategoryGroup

DEFAULT_CATEGORIES: list[tuple[str, CategoryGroup, str]] = [
    ("Rent", CategoryGroup.ESSENTIALS, "🏠"),
    ("Groceries", CategoryGroup.ESSENTIALS, "🛒"),
    ("Electricity", CategoryGroup.ESSENTIALS, "💡"),
    ("Water", CategoryGroup.ESSENTIALS, "💧"),
    ("Transport", CategoryGroup.ESSENTIALS, "🚕"),
    ("Laundry", CategoryGroup.ESSENTIALS, "🧺"),
    ("Hair", CategoryGroup.PERSONAL_CARE, "💇"),
    ("Nails", CategoryGroup.PERSONAL_CARE, "💅"),
    ("Beauty", CategoryGroup.PERSONAL_CARE, "💄"),
    ("Software", CategoryGroup.CAREER, "💻"),
    ("Courses", CategoryGroup.CAREER, "📚"),
    ("Subscriptions", CategoryGroup.CAREER, "🔁"),
    ("Entertainment", CategoryGroup.LIFESTYLE, "🎉"),
    ("Eating Out", CategoryGroup.LIFESTYLE, "🍽️"),
    ("Shopping", CategoryGroup.LIFESTYLE, "🛍️"),
    ("Gifts", CategoryGroup.LIFESTYLE, "🎁"),
    ("Emergency Fund", CategoryGroup.WEALTH, "🛟"),
    ("Car Fund", CategoryGroup.WEALTH, "🚗"),
    ("Home Fund", CategoryGroup.WEALTH, "🏡"),
    ("Investments", CategoryGroup.WEALTH, "📈"),
    ("Other", CategoryGroup.MISC, "📦"),
]


def seed_default_categories(db: Session, user_id: uuid.UUID) -> None:
    categories = [
        Category(
            user_id=user_id,
            name=name,
            group=group,
            icon=icon,
            is_default=True,
            sort_order=index,
        )
        for index, (name, group, icon) in enumerate(DEFAULT_CATEGORIES)
    ]
    db.add_all(categories)
