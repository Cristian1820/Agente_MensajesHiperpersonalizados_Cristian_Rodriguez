import sys
import json
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "agente"))

import gradio as gr
from agente import crear_agente, consultar
from tools import generar_documento_final
from logica_negocio import analizar_cliente

RUTA_DOC = Path(__file__).resolve().parent / "salidas" / "resumen_cobranza.md"
RUTA_CARTERA = Path(__file__).resolve().parent / "data" / "cartera_ejemplo.json"

agente = crear_agente()


def cargar_cartera(archivo):
    if archivo is None:
        return "No se subio ningun archivo.", "Sin cartera cargada", ""
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
        clientes = data["cartera"]

        conteo = {"preventivo": 0, "moderado": 0, "emergente": 0,
                  "ultima_oportunidad": 0, "fuera_de_alcance": 0}
        for c in clientes:
            r = analizar_cliente(c)
            if r["fuera_de_alcance"]:
                conteo["fuera_de_alcance"] += 1
            else:
                conteo[r["segmento"]] += 1

        resumen = (
            f"**Total:** {len(clientes)} clientes\n\n"
            f"🟢 Preventivo: {conteo['preventivo']}\n\n"
            f"🟡 Moderado: {conteo['moderado']}\n\n"
            f"🟠 Emergente: {conteo['emergente']}\n\n"
            f"🔴 Última oportunidad: {conteo['ultima_oportunidad']}\n\n"
            f"⚫ Fuera de alcance: {conteo['fuera_de_alcance']}"
        )

        shutil.copy(archivo, RUTA_CARTERA)
        return "Cartera cargada correctamente.", resumen, ""
    except Exception as e:
        return f"Error cargando la cartera: {e}", "Error", ""


def chatear(mensaje, historial_chat):
    if not mensaje.strip():
        return historial_chat, ""
    respuesta = consultar(agente, mensaje)
    historial_chat.append({"role": "user", "content": mensaje})
    historial_chat.append({"role": "assistant", "content": respuesta})
    return historial_chat, ""


with gr.Blocks(title="Agente de Cobranza", theme=gr.themes.Soft()) as app:

    gr.HTML("""
    <div style="text-align:center; padding: 20px 0 10px 0;">
        <div style="font-size: 48px; margin-bottom: 8px;">💼</div>
        <h1 style="font-size: 28px; font-weight: 700; margin: 0 0 6px 0;">
            Agente de Cobranza Hiperpersonalizada
        </h1>
        <p style="font-size: 15px; color: #888; margin: 0;">
            Segmenta tu cartera y genera mensajes persuasivos con inteligencia artificial
        </p>
        <div style="margin-top: 12px; display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">
            <span style="background:#1a472a; color:#4ade80; padding:4px 12px; border-radius:20px; font-size:13px;">🟢 Preventivo</span>
            <span style="background:#713f12; color:#fbbf24; padding:4px 12px; border-radius:20px; font-size:13px;">🟡 Moderado</span>
            <span style="background:#7c2d12; color:#fb923c; padding:4px 12px; border-radius:20px; font-size:13px;">🟠 Emergente</span>
            <span style="background:#450a0a; color:#f87171; padding:4px 12px; border-radius:20px; font-size:13px;">🔴 Última oportunidad</span>
        </div>
    </div>
    """)

    with gr.Row():

        with gr.Column(scale=3):
            gr.HTML("""
            <div style="background:#1e3a2f; border-radius:10px; padding:10px 14px; margin-bottom:8px;">
                <p style="color:#4ade80; margin:0; font-size:13px;">
                    💬 Puedes consultar cualquier cliente de tu cartera
                    directamente aquí.
                </p>
            </div>
            """)
            chat = gr.Chatbot(
                label="Chat con el agente",
                height=420,
            )
            with gr.Row():
                entrada = gr.Textbox(
                    placeholder="Escribe tu mensaje aquí...",
                    show_label=False,
                    scale=5,
                )
                btn_enviar = gr.Button("Enviar ↗", scale=1, variant="primary")

        with gr.Column(scale=2):

            gr.HTML("""
            <div style="background:#1e3a5f; border-radius:10px; padding:10px 14px; margin-bottom:8px;">
                <p style="color:#60a5fa; margin:0; font-size:13px; font-weight:600;">
                    📂 Paso 1 — Carga tu cartera de clientes
                </p>
                <p style="color:#93c5fd; margin:4px 0 0 0; font-size:12px;">
                    Sube un archivo .json con el listado de clientes a gestionar.
                </p>
            </div>
            """)

            archivo = gr.File(
                label="Haz clic aquí o arrastra tu archivo .json",
                file_types=[".json"],
                file_count="single",
            )
            with gr.Row():
                btn_cargar = gr.Button("📂 Cargar cartera", variant="primary", scale=2)
                btn_nueva = gr.Button("🔄 Nueva cartera", scale=1)
            estado_carga = gr.HTML("")
            resumen_cartera = gr.HTML("")

            gr.HTML("<hr style='margin:12px 0; border-color:#333;'>")

            gr.HTML("""
            <div style="background:#2d1b4e; border-radius:10px; padding:10px 14px; margin-bottom:8px;">
                <p style="color:#c084fc; margin:0; font-size:13px; font-weight:600;">
                    📄 Paso 2 — Genera el documento final
                </p>
                <p style="color:#d8b4fe; margin:4px 0 0 0; font-size:12px;">
                    Genera el resumen consolidado con todos los mensajes de cobranza de la cartera subida.
                </p>
            </div>
            """)

            btn_generar = gr.Button("📄 Generar documento final", variant="secondary")
            estado_doc = gr.HTML("")
            btn_descargar = gr.DownloadButton(
                label="⬇️ Descargar resumen_cobranza.md",
                visible=False,
            )

    # --- Eventos ---
    btn_enviar.click(
        fn=chatear,
        inputs=[entrada, chat],
        outputs=[chat, entrada],
    )
    entrada.submit(
        fn=chatear,
        inputs=[entrada, chat],
        outputs=[chat, entrada],
    )

    def cargar_con_feedback(archivo):
        if archivo is None:
            return (
                '<p style="color:#f87171;">⚠️ No seleccionaste ningún archivo.</p>',
                "",
                ""
            )
        estado, resumen, _ = cargar_cartera(archivo)
        if "correctamente" in estado:
            estado_html = '<p style="color:#4ade80; font-weight:600;">✅ Cartera cargada correctamente.</p>'
            lineas = resumen.strip().split("\n\n")
            colores = {
                "Preventivo":         ("#1a472a", "#4ade80", "🟢"),
                "Moderado":           ("#713f12", "#fbbf24", "🟡"),
                "Emergente":          ("#7c2d12", "#fb923c", "🟠"),
                "Última oportunidad": ("#450a0a", "#f87171", "🔴"),
                "Fuera de alcance":   ("#1a1a1a", "#888888", "⚫"),
            }
            total_line = ""
            items_html = ""
            for linea in lineas:
                linea = linea.strip()
                if "Total" in linea:
                    total_line = linea.replace("**Total:**", "").strip()
                else:
                    for nombre, (bg, color, emoji) in colores.items():
                        if nombre in linea:
                            numero = linea.split(":")[-1].strip()
                            items_html += f"""
                            <div style="display:flex;justify-content:space-between;
                                 align-items:center;padding:6px 10px;margin:4px 0;
                                 background:{bg};border-radius:8px;">
                                <span style="color:{color};font-size:13px;">
                                    {emoji} {nombre}
                                </span>
                                <span style="color:{color};font-weight:700;
                                      font-size:16px;">{numero}</span>
                            </div>
                            """
            resumen_html = f"""
            <div style="background:#111827;border-radius:12px;padding:14px;
                        margin-top:8px;border:1px solid #374151;">
                <p style="color:#9ca3af;font-size:11px;margin:0 0 4px 0;
                          text-transform:uppercase;letter-spacing:1px;">
                    Resumen de cartera
                </p>
                <p style="color:#f9fafb;font-size:22px;font-weight:700;
                          margin:0 0 10px 0;">
                    {total_line}
                </p>
                {items_html}
                <div style="margin-top:12px;padding-top:10px;
                            border-top:1px solid #374151;">
                    <p style="color:#6b7280;font-size:11px;margin:0;line-height:1.6;">
                        💬 Consulta cualquier cliente desde el chat<br>
                        📄 Genera el documento final con el botón de abajo
                    </p>
                </div>
            </div>
            """
        else:
            estado_html = f'<p style="color:#f87171;">❌ {estado}</p>'
            resumen_html = ""
        return estado_html, resumen_html, ""

    btn_cargar.click(
        fn=cargar_con_feedback,
        inputs=[archivo],
        outputs=[estado_carga, resumen_cartera, estado_doc],
    )

    def generar_y_mostrar():
        resultado = generar_documento_final.invoke({})
        if RUTA_DOC.exists():
            estado_html = f'<p style="color:#4ade80; font-weight:600;">✅ Documento generado correctamente.</p>'
            return estado_html, gr.update(visible=True, value=str(RUTA_DOC))
        estado_html = f'<p style="color:#f87171;">❌ {resultado}</p>'
        return estado_html, gr.update(visible=False)

    btn_generar.click(
        fn=generar_y_mostrar,
        outputs=[estado_doc, btn_descargar],
    )

    def limpiar_cartera():
        return None, "", ""

    btn_nueva.click(
        fn=limpiar_cartera,
        outputs=[archivo, estado_carga, resumen_cartera],
    )

if __name__ == "__main__":
    app.launch()
   