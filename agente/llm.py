"""
Conexion al modelo de lenguaje (LLM) via Ollama.
"""

from langchain_ollama import ChatOllama

llm = ChatOllama(model="gemma4:31b-cloud", temperature=0)


if __name__ == "__main__":
    respuesta = llm.invoke("Responde unicamente: 'Modelo conectado.' y nada mas.")
    print(respuesta.content)