"""
Tools del agente.
"""
import json
from pathlib import Path

from langchain.tools import tool

from logica_negocio import analizar_cliente
from llm import llm

RUTA_CARTERA = Path(__file__).resolve().parent.parent / "data" / "cartera_ejemplo.json"
RUTA_SALIDAS = Path(__file__).resolve().parent.parent / "salidas"


@tool
def consultar_cartera() -> str:
    """Devuelve la lista completa de clientes de la cartera,
    con sus datos crudos (cliente, deuda, dias_mora, tiempo_cortado_dias,
    plan_internet), todavia sin analizar.

    Usa esta tool primero para saber que clientes existen. Despues, llama
    a analizar_cliente_cartera una vez por cada cliente para saber su
    segmento de cobranza.

    Respuesta:
        Texto con un cliente por linea, listando sus datos.
    """
    try:
        if not RUTA_CARTERA.exists():
            return f"No se encontro el archivo de cartera en {RUTA_CARTERA}"

        with open(RUTA_CARTERA, "r", encoding="utf-8") as f:
            data = json.load(f)

        clientes = data["cartera"]
        lineas = [f"Total de clientes en cartera: {len(clientes)}"]
        for c in clientes:
            lineas.append(
                f"- {c['cliente']}: deuda=${c['deuda']}, "
                f"dias_mora={c['dias_mora']}, "
                f"tiempo_cortado_dias={c['tiempo_cortado_dias']}, "
                f"plan_internet={c['plan_internet']}"
            )
        return "\n".join(lineas)
    except Exception as e:
        return f"Error leyendo la cartera: {e}"


@tool
def analizar_cliente_cartera(
    cliente: str,
    deuda: float,
    dias_mora: int,
    tiempo_cortado_dias: int,
    plan_internet: int,
) -> str:
    """Analiza la situacion de mora de un cliente y determina su segmento
    de cobranza (preventivo, moderado, emergente, ultima oportunidad, o
    fuera de alcance si el contrato ya fue cancelado de forma administrativa
    por el tiempo que lleva cortado su servicio).

    Reglas:
    - Usa esta tool antes de redactar cualquier mensaje de cobranza, para
      saber que tono y justificacion debe llevar el mensaje.

    Formato de entrada:
        cliente: nombre del cliente.
        deuda: monto adeudado en dolares.
        dias_mora: dias que el cliente lleva sin pagar desde la factura.
        tiempo_cortado_dias: dias que el servicio lleva cortado (0 si no esta cortado).
        plan_internet: Ancho de banda del plan de internet del cliente en Mbps.

    Respuesta:
        Texto con el segmento, el tono recomendado y la justificacion del
        analisis, o un aviso si el cliente esta fuera de alcance, en caso
        de que este fuera del alcance da un mensaje informativo que indique
        que con gusto puede realizar un nuevo contrato y se comunique con
        el departamento de ventas.
    """
    try:
        datos = {
            "cliente": cliente,
            "deuda": deuda,
            "dias_mora": dias_mora,
            "tiempo_cortado_dias": tiempo_cortado_dias,
            "plan_internet": plan_internet,
        }
        resultado = analizar_cliente(datos)

        if resultado["fuera_de_alcance"]:
            return (
                f"Cliente {resultado['cliente']} fuera de alcance: {resultado['motivo']} "
                f"Puede contactar al departamento de ventas para evaluar un nuevo contrato."
            )

        return (
            f"Cliente: {resultado['cliente']}\n"
            f"Segmento: {resultado['etiqueta']}\n"
            f"Tono recomendado: {resultado['tono']}\n"
            f"Justificacion: {resultado['motivo']}"
        )
    except Exception as e:
        return f"Error analizando al cliente {cliente}: {e}"


@tool
def generar_documento_final() -> str:
    """Genera y guarda en disco el documento final consolidado de toda la
    cartera. El documento incluye:
    1. Resumen de la cartera con conteo por segmento.
    2. Logica de negocio aplicada.
    3. Speech de cobranza personalizado para cada cliente.

    Usa esta tool al final, una vez que ya analizaste y redactaste
    los mensajes de todos los clientes de la cartera.

    No recibe parametros — lee la cartera directamente del archivo JSON
    y genera todo el documento de forma automatica.

    Respuesta:
        Texto confirmando la ruta donde se guardo el documento.
    """
    try:
        # Leer la cartera
        if not RUTA_CARTERA.exists():
            return f"No se encontro el archivo de cartera en {RUTA_CARTERA}"

        with open(RUTA_CARTERA, "r", encoding="utf-8") as f:
            data = json.load(f)

        clientes = data["cartera"]

        # Analizar cada cliente y contar por segmento
        conteo = {
            "preventivo": 0,
            "moderado": 0,
            "emergente": 0,
            "ultima_oportunidad": 0,
            "fuera_de_alcance": 0,
        }
        resultados = []
        for c in clientes:
            resultado = analizar_cliente(c)
            resultados.append(resultado)
            if resultado["fuera_de_alcance"]:
                conteo["fuera_de_alcance"] += 1
            else:
                conteo[resultado["segmento"]] += 1

        # Armael resumen de cartera
        seccion_1 = (
            "## 1. Resumen de la cartera\n\n"
            f"- **Total de clientes:** {len(clientes)}\n"
            f"- **Preventivo:** {conteo['preventivo']}\n"
            f"- **Moderado:** {conteo['moderado']}\n"
            f"- **Emergente:** {conteo['emergente']}\n"
            f"- **Ultima oportunidad:** {conteo['ultima_oportunidad']}\n"
            f"- **Fuera de alcance:** {conteo['fuera_de_alcance']}\n"
        )

        # Armar la lógica
        seccion_2 = (
            "## 2. Logica de negocio\n\n"
            "Los clientes se segmentan segun dias de mora y dias de servicio cortado:\n\n"
            "- **Preventivo:** 1 a 15 dias de mora, servicio activo. "
            "Aviso amable para evitar el atraso.\n"
            "- **Moderado:** 16 a 29 dias de mora, servicio activo. "
            "El corte automatico se activa al dia 30.\n"
            "- **Emergente:** 30 o mas dias de mora, servicio cortado menos de 30 dias. "
            "El cliente puede reconectarse pagando.\n"
            "- **Ultima oportunidad:** Servicio cortado entre 30 y 59 dias. "
            "A dias de la cancelacion definitiva del contrato.\n"
            "- **Fuera de alcance:** 60 o mas dias cortado. "
            "Contrato cancelado administrativamente. "
            "Se deriva al departamento de ventas para nuevo contrato.\n"
        )

        # Armar seccion 3: speeches por cliente
        lineas_seccion_3 = ["## 3. Mensajes por cliente\n"]
        for r in resultados:
            if r["fuera_de_alcance"]:
                lineas_seccion_3.append(
                    f"### {r['cliente'].title()} — Fuera de alcance\n\n"
                    f"**Motivo:** {r['motivo']}\n\n"
                    f"**Nota:** Este cliente no recibe speech de cobranza. "
                    f"Puede contactar al departamento de ventas para evaluar "
                    f"un nuevo contrato.\n"
                )
            else:
                prompt_speech = (
                    f"Redacta un mensaje de cobranza personalizado para el siguiente cliente.\n\n"
                    f"DATOS DEL CLIENTE:\n"
                    f"- Nombre: {r['cliente'].title()}\n"
                    f"- Deuda: ${r['deuda']}\n"
                    f"- Dias de mora: {r['dias_mora']}\n"
                    f"- Dias cortado: {r['tiempo_cortado_dias']}\n"
                    f"- Plan: {r['plan_internet']}Mbps\n"
                    f"- Segmento: {r['etiqueta']}\n"
                    f"- Tono: {r['tono']}\n\n"
                    f"REGLAS DE ESTILO (obligatorias):\n"
                    f"- NO uses emojis ni simbolos de advertencia.\n"
                    f"- NO uses mayusculas agresivas.\n"
                    f"- Inicia siempre con un saludo cordial.\n"
                    f"- El tono escala segun el segmento: amable en preventivo, urgente en ultima oportunidad.\n"
                    f"- Incluye siempre el nombre, la deuda, los dias de mora y el plan.\n"
                    f"- Solo devuelve el mensaje, sin titulos ni explicaciones adicionales.\n\n"
                    f"EJEMPLOS DE ESTILO POR SEGMENTO:\n\n"
                    f"[Preventivo]\n"
                    f"Esperamos que te encuentres muy bien, Maria Lopez. Nos comunicamos contigo "
                    f"porque te valoramos como cliente y queremos que sigas disfrutando tu servicio "
                    f"de 200Mbps sin interrupciones. Hemos notado que tienes un saldo pendiente de "
                    f"$15.00 con 5 dias de atraso. Aun estas a tiempo de regularizar tu pago sin "
                    f"ningun inconveniente adicional. Puedes realizar tu pago a traves de nuestros "
                    f"canales habituales. Gracias por tu confianza.\n\n"
                    f"[Moderado]\n"
                    f"Esperamos que estes bien, Carlos Vega. Nos ponemos en contacto contigo porque "
                    f"notamos un saldo pendiente de $35.00 con 20 dias de atraso en tu plan de 400Mbps, "
                    f"y queremos ayudarte a evitar el corte de tu servicio. En pocos dias tu servicio "
                    f"podria suspenderse automaticamente si no se regulariza el pago. Aun estas a tiempo "
                    f"de evitarlo. Te invitamos a gestionar tu pago lo antes posible.\n\n"
                    f"[Emergente]\n"
                    f"Pedro Salas, sabemos que unos dias sin servicio son un inconveniente real. "
                    f"Estamos aqui para ayudarte a resolver tu situacion rapidamente. Tu servicio de "
                    f"550Mbps esta suspendido por un saldo pendiente de $60.00 con 40 dias de mora. "
                    f"La buena noticia es que con un solo pago puedes reconectarte hoy mismo. "
                    f"No dejes pasar mas tiempo. Contactanos y te ayudamos.\n\n"
                    f"[Ultima oportunidad]\n"
                    f"Rosa Mendez, nos dirigimos a ti porque tu situacion requiere atencion inmediata "
                    f"y queremos encontrar una solucion juntos antes de que sea tarde. Tu servicio de "
                    f"850Mbps lleva 38 dias suspendido y tu contrato esta a solo 22 dias de cancelarse "
                    f"de forma definitiva. Tienes una deuda pendiente de $90.00 que aun puedes "
                    f"regularizar. Contactanos hoy mismo. Es el ultimo momento para salvar tu contrato.\n\n"
                    f"Ahora redacta el mensaje para {r['cliente'].title()} siguiendo exactamente ese estilo."
                )
                speech = llm.invoke(prompt_speech).content
                lineas_seccion_3.append(
                    f"### {r['cliente'].title()} — {r['etiqueta']}\n\n"
                    f"**Justificacion:** {r['motivo']}\n\n"
                    f"**Tono:** {r['tono']}\n\n"
                    f"**Mensaje:**\n\n{speech}\n"
                )

        seccion_3 = "\n".join(lineas_seccion_3)

        # Ensamblar documento completo
        documento = (
            "# Resumen de campana de cobranza\n\n"
            f"{seccion_1}\n"
            f"{seccion_2}\n"
            f"{seccion_3}\n"
        )

        # Guardar en carpeta salidas
        RUTA_SALIDAS.mkdir(parents=True, exist_ok=True)
        ruta_archivo = RUTA_SALIDAS / "resumen_cobranza.md"
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(documento)

        return f"Documento generado correctamente en: {ruta_archivo}"

    except Exception as e:
        return f"Error generando el documento: {e}"


if __name__ == "__main__":
    print("=== Prueba: Generar documento final ===")
    resultado = generar_documento_final.invoke({})
    print(resultado)