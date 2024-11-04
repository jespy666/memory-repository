from fastapi.routing import APIRouter

from .google import google_router


oauth2_router = APIRouter(prefix="/oauth2")

# extend oauth router with providers
oauth2_router.include_router(google_router)


__all__ = ('oauth2_router',)
