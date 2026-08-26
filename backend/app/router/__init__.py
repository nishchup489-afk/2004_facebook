from .auth import router as auth_router
from .profile import router as profile_router
from .university import router as university_router


routers = (
    university_router,
    auth_router,
    profile_router,
)
