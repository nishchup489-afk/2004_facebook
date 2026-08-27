from .auth import router as auth_router
from .profile import router as profile_router
from .university import router as university_router
from .me import router as me_router
from .search import router as search_router
from .friends import router as friends_router
from .courses import router as courses_router


routers = (
    university_router,
    auth_router,
    profile_router,
    me_router,
    search_router,
    friends_router,
    courses_router
)
