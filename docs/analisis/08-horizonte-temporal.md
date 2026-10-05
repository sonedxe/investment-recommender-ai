# 08 · El horizonte temporal: concepto y modelado difuso

Qué es el horizonte temporal, de qué teoría viene y cómo lo usa el sistema como el conjunto difuso "en el fitness".

## 1. Qué es

El **horizonte temporal de inversión** es cuánto tiempo puede pasar el usuario **sin necesitar** el dinero que invierte. Si alguien dice "no voy a tocar esta plata en unos 3 años", su horizonte es de unos 3 años.

## 2. De qué teoría viene

Intervienen dos teorías distintas, y conviene no mezclarlas.

### 2.1. El concepto: finanzas

En finanzas personales, el horizonte es una de las variables básicas para perfilar a un inversionista, junto con la tolerancia al riesgo y la situación económica. Los cuestionarios de perfil de bancos y fondos casi siempre lo preguntan.

La idea:

- Las inversiones riesgosas (p. ej. acciones) **suben y bajan** mucho en el corto plazo.
- Si se necesita el dinero en 1 año y justo ese año el mercado cae, hay que **vender en pérdida**: no hay tiempo de esperar a que se recupere.
- Si no se necesitará en 10 años, una caída temporal afecta menos: hay margen de recuperación.

Regla general: **horizonte corto → más cautela; horizonte largo → se tolera más volatilidad.**

> **Matiz:** en la academia financiera esto se discute. Samuelson (1963) argumentó que, bajo ciertos supuestos, el riesgo no disminuye con el plazo. En la práctica la regla se usa ampliamente y es una base razonable para un proyecto educativo. En el informe conviene presentarla como **criterio práctico**, no como ley.

### 2.2. El modelado: lógica difusa

Las personas no hablan en números exactos: "unos añitos", "a mediano plazo", "no por ahora". Además, los umbrales rígidos fallan:

```
Regla rígida: "menos de 3 años = corto"
  2.9 años → corto   → recomendación conservadora
  3.1 años → mediano → recomendación distinta
```

Dos personas casi iguales recibirían recomendaciones muy distintas. La lógica difusa (vista en clase) resuelve esto: un valor puede pertenecer **parcialmente** a varios conjuntos a la vez.

## 3. Conjuntos difusos del horizonte

Universo: H ∈ [0, 30] años (informe v1.1, sección 4.5.1).

| Conjunto | Función | Lectura |
|---|---|---|
| Corto | `Trap(0, 0, 1, 3)` | Totalmente corto hasta 1 año; deja de serlo a los 3 |
| Mediano | `Tri(2, 5, 8)` | Totalmente mediano a los 5 años |
| Largo | `Trap(6, 10, 30, 30)` | Totalmente largo desde los 10 años |

**Ejemplo, H = 2.5 años:**

| Conjunto | Pertenencia |
|---|---|
| Corto | (3 − 2.5) / 2 = 0.25 |
| Mediano | (2.5 − 2) / 3 ≈ 0.17 |
| Largo | 0 |

Es "un poco corto y un poco mediano", no "corto" a secas.

**Entradas cualitativas:** si el usuario solo da una etiqueta ("a largo plazo"), esa etiqueta recibe pertenencia 1 y las demás 0.

## 4. Reglas y salida

Cada conjunto activa una regla que **multiplica la aversión al riesgo (λ)**:

| Regla | Si el horizonte es… | Multiplicador `m_H` | Justificación |
|---|---|---|---|
| RH1 | Corto | 1.5 | Poco tiempo para recuperarse: más cautela |
| RH2 | Mediano | 1.0 | Sin modulación |
| RH3 | Largo | 0.7 | Más margen: se tolera más volatilidad |

La salida es un promedio ponderado por las pertenencias (inferencia Sugeno de orden cero, vista en clase):

```
m_H = Σ μₖ(H) · zₖ / Σ μₖ(H)

H = 2.5 → m_H = (0.25 · 1.5 + 0.17 · 1.0) / (0.25 + 0.17) ≈ 1.30
```

Y la aversión efectiva:

```
λ_ef = λ_base · m_H
```

Si el usuario se declaró conservador (λ_base = 2): **λ_ef = 2 × 1.30 = 2.6**. El sistema se vuelve algo más cauteloso de lo declarado, porque el dinero se necesitará relativamente pronto.

## 5. Por qué es el conjunto difuso "en el fitness"

`λ_ef` entra directamente en la función que califica cada portafolio:

```
Fitness(P) = Σ wᵢ·μ'ᵢ − λ_ef · σ'(P) − …
```

El horizonte cambia **cómo el jurado pone la nota**, no lo que cada individuo es. Por eso cumple el primer pedido del docente (ver [07-feedback-explicado.md](07-feedback-explicado.md)).

## 6. Idea para la exposición

**El concepto es financiero; la manera de manejar su imprecisión es lógica difusa.** Esa combinación de dominio y técnica es un buen mensaje para la presentación.
