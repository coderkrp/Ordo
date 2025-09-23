from fastapi import FastAPI
from ordo.security.authentication import authentication_middleware

app = FastAPI()

app.middleware("http")(authentication_middleware)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/protected")
async def protected_route():
    return {"message": "You have accessed a protected route."}
