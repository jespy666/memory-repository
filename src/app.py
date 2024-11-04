import uvicorn

from fastapi import FastAPI

from .users.routes import user_router
from .auth.routes import auth_router


app = FastAPI()

app.include_router(user_router)
app.include_router(auth_router)


if __name__ == '__main__':
    uvicorn.run(
        'src.app:app',
        host='localhost',
        port=8000,
        reload=True
    )
