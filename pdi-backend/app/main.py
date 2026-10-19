from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Imports estritos de todos os ROUTERS organizados nas novas subpastas
from app.routers.auth import auth
from app.routers.user import user
from app.routers.competence import competence, position, position_competence
from app.routers.evaluation import (
    evaluation,
    evaluation_question,
    evaluation_answer,
    form_question,
)
from app.routers.development import development, development_plan
app = FastAPI(
    title="Sistema de Apoio ao Plano de Desenvolvimento Individual",
    version="1.0.0",
    description="API RESTful para gestão de competências, cálculo de gaps e geração de PDI via Google Gemini."
)

origins = [
    "http://127.0.0.1:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(competence.router)
app.include_router(position.router)
app.include_router(position_competence.router)
app.include_router(form_question.router)
app.include_router(evaluation.router)
app.include_router(evaluation_question.router)
app.include_router(evaluation_answer.router)
app.include_router(development.router)
app.include_router(development_plan.router)


@app.get("/", tags=["Home"])
def raiz():
    return {"message": "API do Sistema de PDI funcionando com sucesso!"}
