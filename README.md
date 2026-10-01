# Calculadora visual

Calculadora básica que se abre en el navegador y calcula en Python. No usa `eval`: un analizador propio acepta solo números, `+`, `-`, `*`, `/` y el signo unario.

## Requisitos

- Python 3.9 o superior
- Biblioteca estándar (no hace falta instalar paquetes)

## Ejecución

Desde la carpeta del proyecto:

```powershell
python server.py
```

El script abre http://127.0.0.1:8765. Si el navegador no se abre, entra a esa dirección a mano. Para detener el servidor, pulsa Ctrl+C en la terminal.

## Uso

Operaciones: suma, resta, multiplicación, división, decimales, borrar el último carácter, limpiar la pantalla y cambiar el signo.

| Tecla | Acción |
| --- | --- |
| `0`–`9` | Dígitos |
| `.` o `,` | Decimal |
| `+` `-` `*` `/` | Operadores |
| `Enter` o `=` | Calcular |
| `Backspace` | Borrar el último carácter |
| `Escape` | Limpiar |

Un segundo punto decimal en el mismo número se ignora. La división por cero y las expresiones inválidas muestran `Error` sin detener el servidor.

## Cómo está hecha

`server.py` sirve los archivos de `static/` y expone `POST /calculate`. El navegador arma la expresión con los botones o el teclado y, al pulsar igual, la envía al servidor. El resultado se calcula con `decimal.Decimal` para evitar errores típicos de los flotantes (por ejemplo, `0.1 + 0.2`).

Las expresiones se limitan a 200 caracteres. Las rutas de los archivos estáticos se comprueban para no salir de la carpeta `static/`.

## Estructura

```
server.py           Servidor y evaluador
static/index.html   Pantalla y teclas
static/style.css    Tema oscuro
static/app.js       Estado de la expresión y teclado
```
