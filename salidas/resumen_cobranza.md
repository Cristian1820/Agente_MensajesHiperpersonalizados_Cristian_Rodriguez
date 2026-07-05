# Resumen de campana de cobranza

## 1. Resumen de la cartera

- **Total de clientes:** 5
- **Preventivo:** 1
- **Moderado:** 1
- **Emergente:** 1
- **Ultima oportunidad:** 1
- **Fuera de alcance:** 1

## 2. Logica de negocio

Los clientes se segmentan segun dias de mora y dias de servicio cortado:

- **Preventivo:** 1 a 15 dias de mora, servicio activo. Aviso amable para evitar el atraso.
- **Moderado:** 16 a 29 dias de mora, servicio activo. El corte automatico se activa al dia 30.
- **Emergente:** 30 o mas dias de mora, servicio cortado menos de 30 dias. El cliente puede reconectarse pagando.
- **Ultima oportunidad:** Servicio cortado entre 30 y 59 dias. A dias de la cancelacion definitiva del contrato.
- **Fuera de alcance:** 60 o mas dias cortado. Contrato cancelado administrativamente. Se deriva al departamento de ventas para nuevo contrato.

## 3. Mensajes por cliente

### Gabriela Mendoza — Preventivo

**Justificacion:** 10 dias de mora, servicio aun activo: aviso preventivo.

**Tono:** Recordatorio amable, sin presionar al cliente.

**Mensaje:**

Esperamos que te encuentres muy bien, Gabriela Mendoza. Nos comunicamos contigo porque te valoramos como cliente y queremos que sigas disfrutando tu servicio de 300Mbps sin interrupciones. Hemos notado que tienes un saldo pendiente de $45.0 con 10 dias de atraso. Aun estas a tiempo de regularizar tu pago sin ningun inconveniente adicional. Puedes realizar tu pago a traves de nuestros canales habituales. Gracias por tu confianza.

### Roberto Silva — Moderado

**Justificacion:** 25 dias de mora, se acerca el corte automatico (dia 30).

**Tono:** Firme pero empatico, avisa que el corte esta cerca.

**Mensaje:**

Esperamos que estes bien, Roberto Silva. Nos ponemos en contacto contigo porque notamos un saldo pendiente de $78.5 con 25 dias de atraso en tu plan de 600Mbps, y queremos ayudarte a evitar el corte de tu servicio. En pocos dias tu servicio podria suspenderse automaticamente si no se regulariza el pago. Aun estas a tiempo de evitarlo. Te invitamos a gestionar tu pago lo antes posible.

### Patricia Leon — Emergente

**Justificacion:** 45 dias de mora y servicio ya cortado (15 dias cortado): riesgo de cancelacion.

**Tono:** Urgente, riesgo de cancelacion si no reacciona.

**Mensaje:**

Hola, Patricia Leon. Nos comunicamos contigo porque tu situación requiere atención inmediata para evitar la pérdida definitiva de tu servicio. Tu plan de 800Mbps se encuentra suspendido desde hace 15 días debido a un saldo pendiente de $120.0 con 45 días de mora. Es fundamental que regularices tu pago a la brevedad, ya que tu contrato se encuentra en riesgo de cancelación definitiva si no hay una reacción inmediata. Contactanos hoy mismo para resolverlo y evitar la baja total de tu cuenta.

### Andres Castillo — Ultima oportunidad

**Justificacion:** Lleva 42 dias cortado, a 18 dias de la cancelacion definitiva del contrato.

**Tono:** Maxima urgencia, oferta especial de pago o reconexion.

**Mensaje:**

Hola, Andres Castillo. Nos dirigimos a ti porque tu situación requiere atención inmediata y queremos encontrar una solución juntos antes de que sea tarde. Tu plan de 500Mbps se encuentra suspendido desde hace 42 días y presentas una deuda de $95.0 con 72 días de mora. Esta es tu última oportunidad para regularizar tu saldo y evitar la cancelación definitiva de tu contrato. Contáctanos hoy mismo para aprovechar una oferta especial de pago y reconexión inmediata. Es el último momento para salvar tu servicio.

### Lucia Herrera — Fuera de alcance

**Motivo:** 62 dias cortado (>= 60). Contrato cancelado de forma definitiva, no se genera speech de cobranza.

**Nota:** Este cliente no recibe speech de cobranza. Puede contactar al departamento de ventas para evaluar un nuevo contrato.

