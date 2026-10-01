# Próximos pasos

Ideas para seguir con la calculadora, de lo más útil a lo más amplio.

## Cálculo

- Paréntesis y prioridad explícita, además de la que ya tienen `*` y `/`.
- Porcentaje, potencia y raíz cuadrada.
- Memoria (`M+`, `M-`, `MR`, `MC`).
- Historial de las últimas operaciones en la propia pantalla.

## Interfaz

- Copiar el resultado al portapapeles.
- Elegir entre tema oscuro y claro.
- Mostrar el error con un texto más concreto (división por cero, expresión incompleta) sin alargar la pantalla.
- Ajustar el tamaño del resultado cuando el número es muy largo.

## Calidad

- Pruebas automáticas del evaluador: prioridad de operadores, signo unario, decimales y división por cero.
- Un flujo de GitHub Actions que ejecute esas pruebas en cada cambio.
- Límite más claro cuando el puerto 8765 ya está ocupado, con un mensaje en la terminal.

## Más adelante

- Modo científico en una segunda fila de teclas, sin mezclarlo con la vista básica.
- Guardar el historial en el navegador para que sobreviva al recargar la página.
- Empaquetar la app para abrirla sin escribir el comando de Python.
