import uuid

from sqlalchemy.orm import Session

from app.models.category import Category, CategoryGroup

DEFAULT_CATEGORIES: list[tuple[str, CategoryGroup, str]] = [
    ("Rent", CategoryGroup.ESSENTIALS, "lucideHouse"),
    ("Groceries", CategoryGroup.ESSENTIALS, "lucideShoppingCart"),
    ("Electricity", CategoryGroup.ESSENTIALS, "lucideZap"),
    ("Water", CategoryGroup.ESSENTIALS, "lucideDroplet"),
    ("Transport", CategoryGroup.ESSENTIALS, "lucideBus"),
    ("Laundry", CategoryGroup.ESSENTIALS, "lucideShirt"),
    ("Hair", CategoryGroup.PERSONAL_CARE, "lucideScissors"),
    ("Nails", CategoryGroup.PERSONAL_CARE, "lucideGem"),
    ("Beauty", CategoryGroup.PERSONAL_CARE, "lucideSparkles"),
    ("Software", CategoryGroup.CAREER, "lucideLaptop"),
    ("Courses", CategoryGroup.CAREER, "lucideGraduationCap"),
    ("Subscriptions", CategoryGroup.CAREER, "lucideRepeat"),
    ("Entertainment", CategoryGroup.LIFESTYLE, "lucideClapperboard"),
    ("Eating Out", CategoryGroup.LIFESTYLE, "lucideUtensils"),
    ("Shopping", CategoryGroup.LIFESTYLE, "lucideShoppingBag"),
    ("Gifts", CategoryGroup.LIFESTYLE, "lucideGift"),
    ("Emergency Fund", CategoryGroup.WEALTH, "lucideLifeBuoy"),
    ("Car Fund", CategoryGroup.WEALTH, "lucideCar"),
    ("Home Fund", CategoryGroup.WEALTH, "lucideWarehouse"),
    ("Investments", CategoryGroup.WEALTH, "lucideTrendingUp"),
    ("Other", CategoryGroup.MISC, "lucidePackage"),
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
