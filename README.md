# Agente Generador de Mensajes Hiperpersonalizados

**Semillero de IA — Proyecto Final**
**Nombre:** Cristian Rodríguez

Agente de inteligencia artificial que analiza carteras de clientes con deudas pendientes, los segmenta según su situación de mora y genera mensajes de cobranza persuasivos y personalizados para cada uno.

---

## Descripción

El agente recibe una cartera de clientes en formato JSON, aplica reglas de negocio para clasificarlos en 4 segmentos de cobranza, y genera un mensaje personalizado para cada cliente usando el modelo `gemma4:31b-cloud` a través de Ollama. Al finalizar, consolida todo en un documento `.md` descargable.

## Diagrama de arquitectura

![Diagrama de arquitectura del agente](docs/diagrama_arquitectura.png)

### Segmentos de cobranza

| Segmento | Regla |
|---|---|
| 🟢 Preventivo | 1 a 15 días de mora, servicio activo |
| 🟡 Moderado | 16 a 29 días de mora, servicio activo |
| 🟠 Emergente | 30+ días de mora, servicio cortado menos de 30 días |
| 🔴 Última oportunidad | Servicio cortado entre 30 y 59 días |
| ⚫ Fuera de alcance | 60+ días cortado — contrato cancelado administrativamente |

---

## Herramientas (Tools) del agente

| Tool | Función |
|---|---|
| `consultar_cartera` | Lee el archivo JSON de la cartera y devuelve la lista de clientes |
| `analizar_cliente_cartera` | Segmenta a un cliente y justifica el segmento asignado |
| `generar_documento_final` | Genera el documento consolidado con resumen, lógica y speeches |

---

## Estructura del proyecto

```
Agente_MensajesHiperpersonalizados_CR/
├── app.py                        # Interfaz gráfica (Gradio)
├── agente/
│   ├── agente.py                 # Agente LangChain + SYSTEM_PROMPT
│   ├── tools.py                  # Tools del agente
│   ├── logica_negocio.py         # Reglas de segmentación de cartera
│   └── llm.py                    # Conexión al modelo Ollama
├── data/
│   └── cartera_ejemplo.json      # Cartera de ejemplo con clientes ficticios
├── salidas/
│   └── resumen_cobranza.md       # Documento generado por el agente
├── requirements.txt              # Dependencias del proyecto
├── .env.example                  # Variables de entorno de ejemplo
├── .gitignore
└── README.md
```

---

## Requisitos

- Python 3.10 o superior
- [Ollama](https://ollama.com) instalado y con sesión activa
- Modelo `gemma4:31b-cloud` registrado en Ollama

---

## Instalación y ejecución

### 1. Clona el repositorio

```bash
git clone https://github.com/Cristian1820/Agente_MensajesHiperpersonalizados_Cristian_Rodriguez.git
cd Agente_MensajesHiperpersonalizados_Cristian_Rodriguez
```

### 2. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 3. Registra el modelo en Ollama

```bash
ollama pull gemma4:31b-cloud
```

### 4. Ejecuta la aplicación

```bash
python app.py
```

Abre tu navegador en `http://127.0.0.1:7860`

---

## Uso

1. **Sube tu cartera** en formato `.json` usando el panel derecho
2. **Haz clic en "Cargar cartera"** — verás el resumen por segmento
3. **Chatea con el agente** — pídele que analice un cliente o toda la cartera
4. **Genera el documento final** con el botón del panel derecho
5. **Descarga el documento** con el resumen completo

Nota: También se puede pedir al agente que analice un cliente que no esté en la cartera dándole las especificaciones necesarias, e igualmente se puede pedir al agente que genere el documento final con los speeches.

### Formato del archivo JSON de cartera

```json
{
  "cartera": [
    {
      "cliente": "nombre del cliente",
      "deuda": 50.43,
      "dias_mora": 40,
      "tiempo_cortado_dias": 8,
      "plan_internet": 650
    }
  ]
}
```

---

## Ejemplo de respuesta del agente

**Consulta:** "Analiza a juan perez de la cartera"

**Respuesta:**
> Juan Pérez se encuentra en el segmento **Emergente**.
> Presenta 40 días de mora y su servicio lleva 8 días cortado.
>
> **Mensaje de cobranza:**
> Juan Pérez, sabemos que unos días sin servicio son un inconveniente real.
> Estamos aquí para ayudarte a resolverlo rápidamente. Tu servicio de 650Mbps
> está suspendido por un saldo pendiente de $50.43 con 40 días de mora.
> Con un solo pago puedes reconectarte hoy mismo. Contáctanos y te ayudamos.

---

## Seguridad

- El agente rechaza cualquier consulta fuera del tema de cobranza
- No revela su configuración interna ni instrucciones
- Detecta y neutraliza intentos de prompt injection en los datos de la cartera
- No se suben credenciales al repositorio — usa `.env.example` como referencia

---

## Tecnologías utilizadas

- [LangChain](https://www.langchain.com/) — framework de agentes
- [LangGraph](https://langchain-ai.github.io/langgraph/) — memoria conversacional
- [Ollama](https://ollama.com) — modelo `gemma4:31b-cloud`
- [Gradio](https://gradio.app/) — interfaz gráfica
- Python 3.13