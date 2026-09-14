import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_form_questions_ai(position_name: str, competences: list[dict]) -> list[dict]:
    prompt = f"""
    Você é um especialista em desenvolvimento de carreira e avaliação de desempenho corporativo.
    Cargo avaliado: {position_name}
    Competências e níveis esperados: {json.dumps(competences, ensure_ascii=False)}

    Para CADA competência, elabore exatamente 2 afirmativas/critérios observáveis para serem pontuados em uma escala de 1 a 5 (onde 1 = Não demonstra / Nunca, e 5 = Domina com excelência / Sempre).    Retorne EXCLUSIVAMENTE um array JSON no seguinte formato:
    
    DIRETRIZES:
    - NÃO faça perguntas abertas (evite começar com 'Como', 'Por que', 'O que').
    - Escreva frases afirmativas, diretas e práticas focadas em comportamento ou aplicação técnica observável.
    - Exemplo de boa afirmativa: "Aplica de forma autônoma técnicas de otimização de desempenho e lazy loading no desenvolvimento de interfaces."
    
    Retorne ESTRITAMENTE o array JSON:
    [
      {{"competence_id": 1, "question_text": "Texto da afirmativa observável"}}
    ]
    """
    
    print(f"\n[AI] Solicitando perguntas para o cargo: {position_name}...")
    
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    
    print("[AI] Perguntas geradas com sucesso pelo Gemini!")
    return json.loads(response.text)