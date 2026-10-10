import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_form_questions_ai(
  position_name: str, 
  competences: list[dict]
  ) -> list[dict]:
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
  
def generate_pdi_suggestions_ai(
  position_name: str,
  gaps: list[dict],
  available_mentors: list[dict] | None = None
  ) -> list[dict]:
  mentors_text = json.dumps(available_mentors or [], ensure_ascii=False)
    
  prompt = f"""
    Você é um especialista em desenvolvimento de carreira e avaliação de desempenho corporativo.
    Cargo avaliado: {position_name}
    Gaps identificados e observações e mentores qualificados: {json.dumps(gaps, ensure_ascii=False)}
    
    DIRETRIZES DE PERSONALIZAÇÃO:
    - Analise com atenção o campo 'comments' de cada competência. O plano de ação DEVE abordar diretamente os problemas específicos ou pontos levantados pelos avaliadores nas observações.
    - Analise o campo 'suggested_mentors' de CADA competência:
      * Se houver pessoas na lista, cite nominalmente um dos mentores e o cargo dele na ação de 20% (Troca/Mentoria).
      * Se a lista 'suggested_mentors' estiver vazia, sugira ações de benchmark externo, participação em meetups ou comunidades técnicas
    
    Para CADA competência da lista, gere as ações no framework 70-20-10:
    - 70% (Prática/Experiência): Tarefa prática real baseada nas observações relatadas.
    - 20% (Social/Mentoria): Ação de mentoria/pair programming com o mentor sugerido ou troca com pares.
    - 10% (Educação Formal): Sugira conteúdos concretos (documentações oficiais, livros ou cursos conceituados).

    Retorne ESTRITAMENTE o array JSON:
    [
      {{
        "competence_id": 1,
        "action_70": "Texto da ação prática personalizada",
        "action_20": "Texto da mentoria/troca",
        "action_10": "Texto do estudo/conteúdo"
      }}
    ]
    """
    
  response = client.models.generate_content(
      model="gemini-flash-lite-latest",
      contents=prompt,
      config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
        
  return json.loads(response.text)