# Sistema Integral de Gestión de Clientes, Servicios y Reservas – Software FJ

**Universidad Nacional Abierta y a Distancia (UNAD)**  
**Curso:** Programación – Código 213023  
**Actividad:** Fase 4 – Componente práctico  
**Lenguaje:** Python

## 1. Descripción del proyecto

Este proyecto consiste en el desarrollo de un sistema integral orientado a objetos para la empresa ficticia Software FJ, dedicado a la gestión de clientes, servicios y reservas.

La aplicación permite administrar usuarios, registrar diferentes tipos de servicios, crear y gestionar reservas, calcular costos y controlar errores durante la ejecución.

El sistema funciona sin utilizar bases de datos. La información se administra mediante objetos y listas en memoria, mientras que los eventos y errores se registran en un archivo de logs.

## 2. Objetivos

- Implementar los principios de programación orientada a objetos.
- Aplicar abstracción, herencia, encapsulación y polimorfismo.
- Implementar excepciones personalizadas y mecanismos avanzados de manejo de errores.
- Registrar eventos y errores mediante el módulo `logging`.
- Simular operaciones válidas e inválidas para comprobar la estabilidad del sistema.

## 3. Estructura del proyecto

```text
fase4-programacion-software-fj/
│
├── main.py
├── registro_operaciones_fj.log
└── README.md
```

El archivo `registro_operaciones_fj.log` se genera automáticamente al ejecutar el programa.

## 4. Clases principales

El sistema está organizado mediante las siguientes clases:

| Clase | Descripción |
|---|---|
| `ComponenteBaseFJ` | Clase abstracta general para los elementos del sistema. |
| `Cliente` | Gestiona los datos personales, validaciones y estado de los clientes. |
| `Servicio` | Clase abstracta que define la estructura general de los servicios. |
| `SalaReunionesFJ` | Gestiona las reservas de salas por horas. |
| `RentaEquiposFJ` | Gestiona el alquiler de equipos por días. |
| `ConsultoriaTecnicaFJ` | Gestiona los servicios de asesoría especializada. |
| `Reserva` | Gestiona las solicitudes, confirmaciones, anulaciones y liquidaciones. |
| `GestorOperacionesFJ` | Administra las listas de clientes, servicios y reservas. |

## 5. Manejo de excepciones

La aplicación implementa excepciones personalizadas para controlar los diferentes errores que pueden presentarse:

- `ExcepcionPlataformaFJ`
- `FalloRegistroUsuario`
- `FalloConfiguracionServicio`
- `FalloGestionReserva`
- `FalloLiquidacion`

También incorpora:

- Bloques `try/except`.
- Bloques `try/except/else`.
- Bloques `try/except/finally`.
- Encadenamiento de excepciones mediante `raise ... from`.
- Registro de eventos y errores utilizando el módulo `logging`.

## 6. Simulaciones del sistema

El proyecto incluye **12 simulaciones** para comprobar el funcionamiento de la aplicación.

Se contemplan operaciones como:

1. Registro válido de un cliente.
2. Rechazo de un cliente con correo electrónico inválido.
3. Registro de los tres tipos de servicios.
4. Rechazo de un servicio con tarifa inválida.
5. Creación de una reserva válida.
6. Rechazo de una reserva con duración fuera del rango permitido.
7. Rechazo de una reserva con servicio no operativo.
8. Aprobación y liquidación de una reserva con descuento e IVA.
9. Rechazo de la anulación de una reserva completada.
10. Creación y aprobación de una reserva de consultoría.
11. Liquidación con parámetros predeterminados.
12. Rechazo de una liquidación con descuento superior al permitido.

**Resultados de la ejecución de las pruebas:**

- Total de simulaciones: 12.
- Operaciones exitosas: 6.
- Errores controlados: 6.
- Fallos inesperados: 0.

## 7. Registro de eventos y errores

El sistema genera el archivo `registro_operaciones_fj.log`, donde se registran:

- Inicio y finalización de la ejecución.
- Operaciones exitosas.
- Errores controlados.
- Descripción de las excepciones.
- Causas encadenadas cuando corresponde.
- Resumen de las simulaciones realizadas.

## 8. Requisitos y ejecución

**Requisito:** Tener Python instalado.

No se requieren bases de datos ni bibliotecas externas adicionales.

Para ejecutar el programa desde una terminal, utilizar:

```bash
python main.py
```

Al iniciar la ejecución, el programa realizará automáticamente las doce simulaciones y generará el archivo de registro correspondiente.

## 9. Tecnologías utilizadas

- Python.
- Programación orientada a objetos.
- GitHub para el alojamiento del código fuente.
- Módulo `logging` para el registro de eventos y errores.

## 10. Conclusión

El desarrollo de este proyecto permite aplicar los fundamentos de la programación orientada a objetos y demostrar la importancia del manejo adecuado de excepciones en aplicaciones de software.

Mediante la implementación de clases abstractas, herencia, polimorfismo, encapsulación, validaciones y registros de eventos, se construyó un sistema funcional capaz de gestionar clientes, servicios y reservas, manteniendo su estabilidad ante diferentes situaciones de error.
