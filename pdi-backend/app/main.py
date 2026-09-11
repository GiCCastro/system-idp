from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Imports estritos de todos os ROUTERS organizados nas novas subpastas
from app.routers.auth import auth
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

""" class EvaluationSchema(BaseModel):
    competence_id: int
    expected_level: int
    self_score: int
    manager_score: int

@app.get("/")
def raiz():
    return {"message": "API do Sistema de PDI funcionando com sucesso!"}

@app.post("/calcular gap", summary="Calcula a lacuna de competência entre o nível esperado e o nível atual do colaborador (gap)")

def calculate_gap(data: EvaluationSchema):

    average_score = (data.self_score + data.manager_score)/2

    gap = data.expected_level - average_score

    final_gap = max(0.0, gap)

    return {
        "competence_id": data.competence_id,
        "expected_level": data.expected_level,
        "self_score": data.self_score,
        "manager_score": data.manager_score,
        "average_score": average_score,
        "gap": "Necessita de PDI" if final_gap > 0 else "Competência Atendida"
    } """