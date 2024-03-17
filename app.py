from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from modules.produtos import router as produtos_router

app = FastAPI()

# Middleware CORS para permitir solicitações de origens diferentes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Adicionar o roteador de produtos ao aplicativo
app.include_router(produtos_router)


