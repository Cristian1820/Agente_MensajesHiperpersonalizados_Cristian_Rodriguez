"""
Explicacion de las reglas de segmentacion que se tomara en cuenta para la generacion de mensajes hiperpersonalizados.

Reglas del ciclo de cobranza (definidas con el cliente del proyecto):
    Dia 0           -> factura emitida.
    Dias 1-29       -> cliente en mora, servicio activo.
    Dia 30          -> corte automatico del servicio.
    Dias 0-59       -> cortado, contrato todavia vigente (se puede recuperar pagando).
    Dia 60+ cortado -> cancelacion definitiva administrativa del contrato (fuera de alcance).


    Segmento y Regla 
    
    Preventivo: dias_mora 1–15 (servicio activo)
    Moderado: dias_mora 16–29 (servicio activo, se acerca el corte)
    Emergente: dias_mora ≥30 y tiempo_cortado_dias 0–29 (ya servicio cortado)
    Ultima_oportunidad: tiempo_cortado_dias 30–59 (a punto de cumplir 60 días cortado)
"""

# Dias de mora a partir del cual el servicio ya esta cortado.
DIAS_MORA_PARA_CORTE = 30

# Dias cortado a partir del cual el contrato se cancela de forma definitiva.
DIAS_CORTADO_PARA_CANCELACION = 60

# Catalogo de segmentos: etiqueta visible + tono que debe usar el speech.
SEGMENTOS = {
    "preventivo": {
        "etiqueta": "Preventivo",
        "tono": "Recordatorio amable, sin presionar al cliente.",
    },
    "moderado": {
        "etiqueta": "Moderado",
        "tono": "Firme pero empatico, avisa que el corte esta cerca.",
    },
    "emergente": {
        "etiqueta": "Emergente",
        "tono": "Urgente, riesgo de cancelacion si no reacciona.",
    },
    "ultima_oportunidad": {
        "etiqueta": "Ultima oportunidad",
        "tono": "Maxima urgencia, oferta especial de pago o reconexion.",
    },
}


def segmentar_cliente(dias_mora: int, tiempo_cortado_dias: int) -> str | None:
    """
    Determina el segmento de cobranza de un cliente segun sus dias de mora
    y los dias que lleva cortado.

    Devuelve None si el cliente esta fuera de alcance (contrato ya cancelado
    de forma definitiva, no se genera speech de cobranza).
    """
    if tiempo_cortado_dias >= DIAS_CORTADO_PARA_CANCELACION:
        return None

    if dias_mora >= DIAS_MORA_PARA_CORTE:
        if tiempo_cortado_dias >= 30:
            return "ultima_oportunidad"
        return "emergente"

    if dias_mora >= 16:
        return "moderado"

    if dias_mora >= 1:
        return "preventivo"

    return None


def justificar_segmento(segmento: str, dias_mora: int, tiempo_cortado_dias: int) -> str:
    """Devuelve una justificacion legible de por que se asigno ese segmento."""
    if segmento == "preventivo":
        return f"{dias_mora} dias de mora, servicio aun activo: aviso preventivo."
    if segmento == "moderado":
        return f"{dias_mora} dias de mora, se acerca el corte automatico (dia {DIAS_MORA_PARA_CORTE})."
    if segmento == "emergente":
        return (
            f"{dias_mora} dias de mora y servicio ya cortado "
            f"({tiempo_cortado_dias} dias cortado): riesgo de cancelacion."
        )
    if segmento == "ultima_oportunidad":
        dias_restantes = DIAS_CORTADO_PARA_CANCELACION - tiempo_cortado_dias
        return (
            f"Lleva {tiempo_cortado_dias} dias cortado, a {dias_restantes} dias "
            "de la cancelacion definitiva del contrato."
        )
    return "Sin justificacion disponible."


def analizar_cliente(datos: dict) -> dict:
    """
    Punto de entrada principal de este modulo.

    Recibe un dict con la forma de la cartera de ejemplo:
        {'cliente': str, 'deuda': float, 'tiempo_cortado_dias': int,
         'plan_internet': float, 'dias_mora': int}

    Devuelve un dict con el segmento asignado, el tono recomendado y
    la justificacion del por que.
    """
    cliente = datos["cliente"]
    deuda = datos["deuda"]
    tiempo_cortado_dias = datos["tiempo_cortado_dias"]
    plan_internet = datos["plan_internet"]
    dias_mora = datos["dias_mora"]

    segmento = segmentar_cliente(dias_mora, tiempo_cortado_dias)

    if segmento is None:
        return {
            "cliente": cliente,
            "segmento": None,
            "fuera_de_alcance": True,
            "motivo": (
                f"{tiempo_cortado_dias} dias cortado (>= {DIAS_CORTADO_PARA_CANCELACION}). "
                "Contrato cancelado de forma definitiva, no se genera speech de cobranza."
            ),
        }

    info = SEGMENTOS[segmento]
    return {
        "cliente": cliente,
        "segmento": segmento,
        "etiqueta": info["etiqueta"],
        "tono": info["tono"],
        "deuda": deuda,
        "dias_mora": dias_mora,
        "tiempo_cortado_dias": tiempo_cortado_dias,
        "plan_internet": plan_internet,
        "fuera_de_alcance": False,
        "motivo": justificar_segmento(segmento, dias_mora, tiempo_cortado_dias),
    }

# Lista de clientes ficticios, uno por cada segmento posible.
if __name__ == "__main__":
    
    clientes_prueba = [
    {"cliente": "ana torres", "deuda": 15.00, "tiempo_cortado_dias": 0, "plan_internet": 200, "dias_mora": 5},
    {"cliente": "luis vera", "deuda": 35.00, "tiempo_cortado_dias": 0, "plan_internet": 400, "dias_mora": 20},
    {"cliente": "maria sanchez", "deuda": 60.00, "tiempo_cortado_dias": 10, "plan_internet": 550, "dias_mora": 40},
    {"cliente": "pedro gomez", "deuda": 90.00, "tiempo_cortado_dias": 38, "plan_internet": 850, "dias_mora": 68},
    {"cliente": "rosa flores", "deuda": 120.00, "tiempo_cortado_dias": 50, "plan_internet": 1200, "dias_mora": 80},
    {"cliente": "carlos ruiz", "deuda": 150.00, "tiempo_cortado_dias": 65, "plan_internet": 1000, "dias_mora": 95},
]

    for datos_cliente in clientes_prueba:
        resultado = analizar_cliente(datos_cliente)
        print(resultado)
        print("---" * 50)                 