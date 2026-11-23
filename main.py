"""Plataforma de Gestion de Usuarios, Servicios y Reservas - Software FJ.

Implementacion en un unico archivo ejecutable sin base de datos.
Registra eventos, errores y causas encadenadas en registro_operaciones_fj.log.
Ejecucion: python main.py
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
import logging
from pathlib import Path
import re


# ---------------------------------------------------------------------------
# 1. EXCEPCIONES PERSONALIZADAS Y SISTEMA DE LOGS
# ---------------------------------------------------------------------------

class ExcepcionPlataformaFJ(Exception):
    """Excepcion raiz para errores controlados del dominio de Software FJ."""


class FalloRegistroUsuario(ExcepcionPlataformaFJ):
    """Error al validar o registrar un usuario."""


class FalloConfiguracionServicio(ExcepcionPlataformaFJ):
    """Error al crear o validar un servicio."""


class FalloGestionReserva(ExcepcionPlataformaFJ):
    """Error en creacion, aprobacion, anulacion o cobro de reservas."""


class FalloLiquidacion(ExcepcionPlataformaFJ):
    """Error en el calculo de montos, descuentos o impuestos."""


def iniciar_bitacora():
    """Configura el logger para escribir en registro_operaciones_fj.log."""
    bitacora = logging.getLogger("BitacoraSoftwareFJ")
    bitacora.setLevel(logging.INFO)
    bitacora.propagate = False

    # Limpia manejadores previos para evitar duplicados o archivos bloqueados al reejecutar.
    for manejador in list(bitacora.handlers):
        bitacora.removeHandler(manejador)
        manejador.close()

    try:
        base_dir = Path(__file__).resolve().parent
    except NameError:
        base_dir = Path.cwd()

    archivo_log = base_dir / "registro_operaciones_fj.log"
    # Modo 'w' para dejar un log limpio de la ejecucion actual.
    manejador_archivo = logging.FileHandler(archivo_log, mode="w", encoding="utf-8")
    formato = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    manejador_archivo.setFormatter(formato)
    bitacora.addHandler(manejador_archivo)

    return bitacora, archivo_log


def formatear_excepcion_con_causa(err: Exception) -> str:
    """Devuelve el mensaje de error incluyendo la excepcion encadenada (__cause__) si existe."""
    partes = [f"{type(err).__name__}: {err}"]
    if err.__cause__ is not None:
        partes.append(f"Causa encadenada -> {type(err.__cause__).__name__}: {err.__cause__}")
    return " | ".join(partes)


# ---------------------------------------------------------------------------
# 2. JERARQUIA ABSTRACTA Y ENTIDAD CLIENTE (Cliente)
# ---------------------------------------------------------------------------

class ComponenteBaseFJ(ABC):
    """Clase abstracta general para elementos gestionados en el sistema."""

    def __init__(self, codigo: str):
        # Valida que el codigo sea texto no vacio con longitud minima.
        if not isinstance(codigo, str) or len(codigo.strip()) < 3:
            raise FalloConfiguracionServicio("El codigo debe ser texto de al menos 3 caracteres.")
        # Atributo protegido encapsulado para identificar la entidad.
        self._codigo = codigo.strip().upper()

    @property
    def codigo(self) -> str:
        return self._codigo

    @abstractmethod
    def ficha_resumen(self) -> str:
        """Retorna una representacion resumida del componente."""


class Cliente(ComponenteBaseFJ):
    """Representa a un cliente/usuario con datos encapsulados y validados."""

    def __init__(self, codigo: str, nombre_completo: str, email: str, habilitado: bool = True):
        super().__init__(codigo)
        self._nombre_completo = ""
        self._email = ""
        self._habilitado = True

        # Usa los setters para aplicar validaciones desde la construccion.
        self.nombre_completo = nombre_completo
        self.email = email
        self.habilitado = habilitado

    @property
    def nombre_completo(self) -> str:
        return self._nombre_completo

    @nombre_completo.setter
    def nombre_completo(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise FalloRegistroUsuario("Nombre invalido: se requieren al menos 3 caracteres.")
        self._nombre_completo = valor.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        if not isinstance(valor, str) or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", valor.strip()):
            raise FalloRegistroUsuario(f"Correo electronico invalido: '{valor}'.")
        self._email = valor.strip().lower()

    @property
    def habilitado(self) -> bool:
        return self._habilitado

    @habilitado.setter
    def habilitado(self, estado: bool) -> None:
        if not isinstance(estado, bool):
            raise FalloRegistroUsuario("El estado 'habilitado' debe ser booleano (True/False).")
        self._habilitado = estado

    def suspender(self) -> None:
        self._habilitado = False

    def ficha_resumen(self) -> str:
        estado_txt = "Habilitado" if self._habilitado else "Suspendido"
        return f"Usuario({self._codigo}) -> {self._nombre_completo} <{self._email}> [{estado_txt}]"


# ---------------------------------------------------------------------------
# 3. SERVICIOS ABSTRACTOS Y TRES TIPOS ESPECIALIZADOS
# ---------------------------------------------------------------------------

class Servicio(ComponenteBaseFJ, ABC):
    """Clase abstracta para los servicios de Software FJ."""

    def __init__(self, codigo: str, titulo: str, precio_unitario: float, operativo: bool = True):
        super().__init__(codigo)
        if not isinstance(titulo, str) or len(titulo.strip()) < 3:
            raise FalloConfiguracionServicio("El titulo del servicio debe tener al menos 3 caracteres.")
        if isinstance(precio_unitario, bool) or not isinstance(precio_unitario, (int, float)) or precio_unitario <= 0:
            raise FalloConfiguracionServicio("El precio unitario debe ser un numero mayor que cero.")
        if not isinstance(operativo, bool):
            raise FalloConfiguracionServicio("La disponibilidad operativa debe ser booleana.")

        self._titulo = titulo.strip()
        self._precio_unitario = float(precio_unitario)
        self._operativo = operativo

    @property
    def titulo(self) -> str:
        return self._titulo

    @property
    def precio_unitario(self) -> float:
        return self._precio_unitario

    @property
    def operativo(self) -> bool:
        return self._operativo

    def marcar_operativo(self, estado: bool) -> None:
        if not isinstance(estado, bool):
            raise FalloConfiguracionServicio("El estado operativo debe ser booleano.")
        self._operativo = estado

    @abstractmethod
    def validar_cantidad(self, cantidad: int) -> None:
        """Valida si la cantidad solicitada es correcta para el tipo de servicio."""

    @abstractmethod
    def detalle_servicio(self) -> str:
        """Describe las caracteristicas especificas del servicio."""

    def liquidar_costo(
        self,
        cantidad: int,
        descuento_porc: float = 0.0,
        iva_porc: float = 19.0,
    ) -> dict:
        """Calcula subtotal, descuento, IVA y total con parametros opcionales."""
        try:
            # Polimorfismo: cada servicio valida su propia regla de cantidad.
            self.validar_cantidad(cantidad)

            if isinstance(descuento_porc, bool) or not isinstance(descuento_porc, (int, float)):
                raise FalloLiquidacion("El descuento debe ser numerico.")
            if isinstance(iva_porc, bool) or not isinstance(iva_porc, (int, float)):
                raise FalloLiquidacion("El IVA debe ser numerico.")
            if not (0.0 <= float(descuento_porc) < 100.0):
                raise FalloLiquidacion("El descuento debe estar entre 0 y menor a 100.")
            if float(iva_porc) < 0.0 or float(iva_porc) > 50.0:
                raise FalloLiquidacion("El IVA debe estar entre 0 y 50.")

            tarifa_efectiva = self._precio_base_ajustado()
            subtotal = round(tarifa_efectiva * cantidad, 2)
            ahorro = round(subtotal * (float(descuento_porc) / 100.0), 2)
            base_gravable = round(subtotal - ahorro, 2)
            impuesto = round(base_gravable * (float(iva_porc) / 100.0), 2)
            total = round(base_gravable + impuesto, 2)

            if total < 0:
                raise FalloLiquidacion("Liquidacion inconsistente: valor total negativo.")

            return {
                "subtotal": subtotal,
                "descuento": ahorro,
                "iva": impuesto,
                "total": total,
            }
        except ExcepcionPlataformaFJ:
            # Propaga excepciones propias ya tipificadas sin perder su contexto.
            raise
        except Exception as exc:
            # Encadena cualquier error inesperado dentro de FalloLiquidacion.
            raise FalloLiquidacion("Fallo al liquidar el costo del servicio.") from exc

    def _precio_base_ajustado(self) -> float:
        """Permite a subclases ajustar la tarifa base por condiciones propias."""
        return self._precio_unitario

    def ficha_resumen(self) -> str:
        return self.detalle_servicio()


class SalaReunionesFJ(Servicio):
    """Servicio 1: Reserva de salas por bloques de horas."""

    def __init__(self, codigo: str, titulo: str, tarifa_hora: float, cupo_maximo: int, operativo: bool = True):
        super().__init__(codigo, titulo, tarifa_hora, operativo)
        if isinstance(cupo_maximo, bool) or not isinstance(cupo_maximo, int) or cupo_maximo < 2:
            raise FalloConfiguracionServicio("El cupo de la sala debe ser entero de minimo 2 personas.")
        self._cupo_maximo = cupo_maximo

    def validar_cantidad(self, cantidad: int) -> None:
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or not (1 <= cantidad <= 10):
            raise FalloConfiguracionServicio("Las horas de reserva de sala deben estar entre 1 y 10.")

    def detalle_servicio(self) -> str:
        estado = "Operativa" if self._operativo else "Fuera de servicio"
        return (
            f"Sala [{self._codigo}] '{self._titulo}' | Cupo: {self._cupo_maximo} | "
            f"${self._precio_unitario:,.2f}/h ({estado})"
        )


class RentaEquiposFJ(Servicio):
    """Servicio 2: Alquiler de equipos por dias."""

    def __init__(self, codigo: str, titulo: str, tarifa_dia: float, serial_equipo: str, operativo: bool = True):
        super().__init__(codigo, titulo, tarifa_dia, operativo)
        if not isinstance(serial_equipo, str) or len(serial_equipo.strip()) < 4:
            raise FalloConfiguracionServicio("El serial del equipo debe tener al menos 4 caracteres.")
        self._serial_equipo = serial_equipo.strip().upper()

    def validar_cantidad(self, cantidad: int) -> None:
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or not (1 <= cantidad <= 15):
            raise FalloConfiguracionServicio("Los dias de alquiler de equipo deben estar entre 1 y 15.")

    def detalle_servicio(self) -> str:
        estado = "Operativo" if self._operativo else "Fuera de servicio"
        return (
            f"Equipo [{self._codigo}] '{self._titulo}' (SN:{self._serial_equipo}) | "
            f"${self._precio_unitario:,.2f}/dia ({estado})"
        )


class ConsultoriaTecnicaFJ(Servicio):
    """Servicio 3: Asesoria especializada por sesiones (con recargo en modalidad presencial)."""

    def __init__(self, codigo: str, titulo: str, tarifa_sesion: float, area_tecnica: str, presencial: bool = False, operativo: bool = True):
        super().__init__(codigo, titulo, tarifa_sesion, operativo)
        if not isinstance(area_tecnica, str) or len(area_tecnica.strip()) < 3:
            raise FalloConfiguracionServicio("El area tecnica es obligatoria.")
        if not isinstance(presencial, bool):
            raise FalloConfiguracionServicio("El indicador presencial debe ser booleano.")
        self._area_tecnica = area_tecnica.strip()
        self._presencial = presencial

    def _precio_base_ajustado(self) -> float:
        # Recargo del 15% si la consultoria es presencial.
        return self._precio_unitario * (1.15 if self._presencial else 1.0)

    def validar_cantidad(self, cantidad: int) -> None:
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or not (1 <= cantidad <= 12):
            raise FalloConfiguracionServicio("Las sesiones de consultoria deben estar entre 1 y 12.")

    def detalle_servicio(self) -> str:
        modalidad = "Presencial (+15%)" if self._presencial else "Remota"
        estado = "Operativa" if self._operativo else "Fuera de servicio"
        return (
            f"Consultoria [{self._codigo}] '{self._titulo}' ({self._area_tecnica} - {modalidad}) | "
            f"${self._precio_unitario:,.2f}/sesion ({estado})"
        )


# ---------------------------------------------------------------------------
# 4. RESERVA Y GESTOR EN MEMORIA (LISTAS, SIN BASE DE DATOS)
# ---------------------------------------------------------------------------

class EstadoSolicitud(Enum):
    REGISTRADA = "REGISTRADA"
    APROBADA = "APROBADA"
    ANULADA = "ANULADA"
    COMPLETADA = "COMPLETADA"


class Reserva:
    """Vincula un usuario, un servicio, duracion/unidades, fecha y estado."""

    def __init__(self, folio: str, usuario: Cliente, servicio: Servicio, unidades: int, inicio: datetime):
        if not isinstance(folio, str) or not folio.strip():
            raise FalloGestionReserva("El folio de la reserva es obligatorio.")
        if not isinstance(usuario, Cliente):
            raise FalloGestionReserva("Se requiere una instancia valida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise FalloGestionReserva("Se requiere una instancia valida de Servicio.")
        if not usuario.habilitado:
            raise FalloGestionReserva("El usuario esta suspendido y no puede reservar.")
        if not servicio.operativo:
            raise FalloGestionReserva("El servicio no se encuentra operativo.")
        if not isinstance(inicio, datetime) or inicio <= datetime.now():
            raise FalloGestionReserva("La fecha de inicio debe ser una fecha futura valida.")

        try:
            servicio.validar_cantidad(unidades)
        except ExcepcionPlataformaFJ as exc:
            # Encadenamiento explicito: conserva la excepcion original en __cause__.
            raise FalloGestionReserva("Cantidad invalida al crear la reserva.") from exc

        self.folio = folio.strip().upper()
        self.usuario = usuario
        self.servicio = servicio
        self.unidades = unidades
        self.inicio = inicio
        self.estado = EstadoSolicitud.REGISTRADA
        self.liquidacion = None

    def aprobar(self) -> str:
        if self.estado != EstadoSolicitud.REGISTRADA:
            raise FalloGestionReserva(f"No se puede aprobar una reserva en estado {self.estado.value}.")
        if not self.usuario.habilitado or not self.servicio.operativo:
            raise FalloGestionReserva("Usuario o servicio no disponible para aprobar la reserva.")
        self.estado = EstadoSolicitud.APROBADA
        return f"Reserva {self.folio} aprobada."

    def anular(self) -> str:
        if self.estado == EstadoSolicitud.COMPLETADA:
            raise FalloGestionReserva("No se puede anular una reserva ya completada.")
        if self.estado == EstadoSolicitud.ANULADA:
            raise FalloGestionReserva("La reserva ya se encuentra anulada.")
        self.estado = EstadoSolicitud.ANULADA
        return f"Reserva {self.folio} anulada."

    def completar_y_cobrar(self, descuento_porc: float = 0.0, iva_porc: float = 19.0) -> dict:
        if self.estado != EstadoSolicitud.APROBADA:
            raise FalloGestionReserva("Solo reservas APROBADAS pueden completarse y liquidarse.")
        try:
            self.liquidacion = self.servicio.liquidar_costo(
                self.unidades, descuento_porc=descuento_porc, iva_porc=iva_porc
            )
        except ExcepcionPlataformaFJ as exc:
            # Encadenamiento explicito del error de liquidacion dentro de la gestion de reserva.
            raise FalloGestionReserva("Error al procesar el cobro de la reserva.") from exc

        self.estado = EstadoSolicitud.COMPLETADA
        return self.liquidacion

    def __str__(self) -> str:
        return (
            f"Folio {self.folio} | {self.usuario.nombre_completo} | "
            f"{self.servicio.titulo} x{self.unidades} | Estado: {self.estado.value}"
        )


class GestorOperacionesFJ:
    """Administra colecciones en memoria (listas) sin usar bases de datos."""

    def __init__(self, bitacora: logging.Logger):
        # Estructuras en memoria (sin base de datos).
        self.usuarios: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []
        self.bitacora = bitacora

    def agregar_usuario(self, usuario: Cliente) -> str:
        if any(u.codigo == usuario.codigo for u in self.usuarios):
            raise FalloRegistroUsuario(f"Ya existe un usuario con codigo {usuario.codigo}.")
        if any(u.email == usuario.email for u in self.usuarios):
            raise FalloRegistroUsuario(f"Ya existe un usuario con correo {usuario.email}.")
        self.usuarios.append(usuario)
        self.bitacora.info("Usuario agregado: %s", usuario.ficha_resumen())
        return usuario.ficha_resumen()

    def agregar_servicio(self, servicio: Servicio) -> str:
        if any(s.codigo == servicio.codigo for s in self.servicios):
            raise FalloConfiguracionServicio(f"Ya existe un servicio con codigo {servicio.codigo}.")
        self.servicios.append(servicio)
        self.bitacora.info("Servicio agregado: %s", servicio.detalle_servicio())
        return servicio.detalle_servicio()

    def buscar_usuario(self, codigo: str) -> Cliente:
        cod = str(codigo).strip().upper()
        for u in self.usuarios:
            if u.codigo == cod:
                return u
        raise FalloRegistroUsuario(f"Usuario con codigo '{cod}' no encontrado.")

    def buscar_servicio(self, codigo: str) -> Servicio:
        cod = str(codigo).strip().upper()
        for s in self.servicios:
            if s.codigo == cod:
                return s
        raise FalloConfiguracionServicio(f"Servicio con codigo '{cod}' no encontrado.")

    def registrar_reserva(self, folio: str, cod_usuario: str, cod_servicio: str, unidades: int, inicio: datetime) -> Reserva:
        usuario = self.buscar_usuario(cod_usuario)
        servicio = self.buscar_servicio(cod_servicio)
        if any(r.folio == folio.strip().upper() for r in self.reservas):
            raise FalloGestionReserva(f"El folio '{folio}' ya esta registrado.")

        reserva = Reserva(folio, usuario, servicio, unidades, inicio)
        self.reservas.append(reserva)
        self.bitacora.info("Reserva registrada: %s", reserva)
        return reserva


# ---------------------------------------------------------------------------
# 5. EJECUCION DE 12 SIMULACIONES (VALIDAS E INVALIDAS)
# ---------------------------------------------------------------------------

def correr_simulacion(nro: int, descripcion: str, fn, bitacora: logging.Logger, metricas: dict) -> None:
    """Ejecuta una simulacion usando try/except/else/finally sin detener el programa."""
    print(f"\n[Simulacion {nro:02d}] {descripcion}")
    try:
        salida = fn()
    except ExcepcionPlataformaFJ as err:
        metricas["errores_controlados"] += 1
        detalle = formatear_excepcion_con_causa(err)
        bitacora.warning("Simulacion %02d error controlado: %s", nro, detalle)
        print(f"  -> Error controlado: {detalle}")
    except Exception as err:
        metricas["fallos_inesperados"] += 1
        detalle = formatear_excepcion_con_causa(err)
        bitacora.error("Simulacion %02d fallo inesperado: %s", nro, detalle, exc_info=True)
        print(f"  -> Fallo inesperado: {detalle}")
    else:
        metricas["exitos"] += 1
        bitacora.info("Simulacion %02d exitosa: %s", nro, salida)
        print(f"  -> Exito: {salida}")
    finally:
        metricas["total"] += 1


def ejecutar_12_simulaciones(bitacora: logging.Logger, archivo_log: Path) -> None:
    gestor = GestorOperacionesFJ(bitacora)
    metricas = {"total": 0, "exitos": 0, "errores_controlados": 0, "fallos_inesperados": 0}

    fecha_futura_1 = datetime.now() + timedelta(days=2)
    fecha_futura_2 = datetime.now() + timedelta(days=3)

    bitacora.info("Inicio de ejecucion de simulaciones para Software FJ.")
    print("=== INICIO DE SIMULACIONES - SOFTWARE FJ (SIN BASE DE DATOS) ===")

    # 1. Registro valido de usuario
    correr_simulacion(
        1, "Registrar usuario valido",
        lambda: gestor.agregar_usuario(Cliente("USR01", "Laura Gomez", "laura.gomez@correo.com", True)),
        bitacora, metricas
    )

    # 2. Registro invalido de usuario (correo sin formato valido)
    correr_simulacion(
        2, "Rechazar usuario con correo invalido",
        lambda: gestor.agregar_usuario(Cliente("USR02", "Pedro Ruiz", "pedro_sin_arroba", True)),
        bitacora, metricas
    )

    # 3. Registro de los 3 tipos de servicios (polimorfismo y herencia)
    correr_simulacion(
        3, "Registrar sala de reuniones, renta de equipos y consultoria",
        lambda: (
            gestor.agregar_servicio(SalaReunionesFJ("SRV-S1", "Sala Norte", 65000, 12, True)),
            gestor.agregar_servicio(RentaEquiposFJ("SRV-E1", "Laptop Dell", 45000, "SN998877", True)),
            gestor.agregar_servicio(ConsultoriaTecnicaFJ("SRV-C1", "Arquitectura Cloud", 120000, "DevOps", True, True)),
        ),
        bitacora, metricas
    )

    # 4. Creacion invalida de servicio (tarifa cero/negativa)
    correr_simulacion(
        4, "Rechazar servicio con tarifa invalida",
        lambda: gestor.agregar_servicio(SalaReunionesFJ("SRV-BAD", "Sala Invalida", 0, 6, True)),
        bitacora, metricas
    )

    # 5. Reserva valida de sala
    correr_simulacion(
        5, "Crear reserva valida de sala (3 horas)",
        lambda: gestor.registrar_reserva("RES-101", "USR01", "SRV-S1", 3, fecha_futura_1),
        bitacora, metricas
    )

    # 6. Reserva invalida por cantidad fuera de rango (encadenamiento de excepcion)
    correr_simulacion(
        6, "Rechazar reserva de sala con 25 horas (fuera de rango)",
        lambda: gestor.registrar_reserva("RES-102", "USR01", "SRV-S1", 25, fecha_futura_1),
        bitacora, metricas
    )

    # 7. Reserva invalida con servicio fuera de operacion
    correr_simulacion(
        7, "Rechazar reserva cuando el servicio no esta operativo",
        lambda: (
            gestor.buscar_servicio("SRV-E1").marcar_operativo(False),
            gestor.registrar_reserva("RES-103", "USR01", "SRV-E1", 2, fecha_futura_2),
        ),
        bitacora, metricas
    )

    # 8. Confirmar y liquidar reserva valida con descuento e IVA
    correr_simulacion(
        8, "Aprobar y liquidar reserva RES-101 con 10% descuento e IVA 19%",
        lambda: (
            next(r for r in gestor.reservas if r.folio == "RES-101").aprobar(),
            next(r for r in gestor.reservas if r.folio == "RES-101").completar_y_cobrar(descuento_porc=10.0, iva_porc=19.0),
        ),
        bitacora, metricas
    )

    # 9. Intentar anular una reserva ya completada (error de estado)
    correr_simulacion(
        9, "Rechazar anulacion de reserva ya completada",
        lambda: next(r for r in gestor.reservas if r.folio == "RES-101").anular(),
        bitacora, metricas
    )

    # 10. Crear y aprobar reserva de consultoria presencial
    def _crear_y_aprobar_consultoria():
        res = gestor.registrar_reserva("RES-104", "USR01", "SRV-C1", 2, fecha_futura_2)
        estado_msg = res.aprobar()
        return f"{res} -> {estado_msg}"

    correr_simulacion(
        10, "Crear y aprobar reserva de consultoria presencial (2 sesiones)",
        _crear_y_aprobar_consultoria,
        bitacora, metricas
    )

    # 11. Liquidar consultoria con parametros por defecto (sin descuento, IVA 19%)
    correr_simulacion(
        11, "Liquidar consultoria RES-104 con parametros opcionales por defecto",
        lambda: next(r for r in gestor.reservas if r.folio == "RES-104").completar_y_cobrar(),
        bitacora, metricas
    )

    # 12. Liquidacion invalida con descuento mayor al 100%
    correr_simulacion(
        12, "Rechazar liquidacion con descuento del 150%",
        lambda: gestor.buscar_servicio("SRV-S1").liquidar_costo(2, descuento_porc=150.0),
        bitacora, metricas
    )

    print("\n=== RESUMEN FINAL ===")
    print(f"Total simulaciones:  {metricas['total']}")
    print(f"Exitosas:            {metricas['exitos']}")
    print(f"Errores controlados: {metricas['errores_controlados']}")
    print(f"Fallos inesperados:  {metricas['fallos_inesperados']}")
    print(f"Log generado en:     {archivo_log.name}")

    bitacora.info(
        "Resumen final -> Total: %d | Exitosas: %d | Errores controlados: %d | Fallos inesperados: %d",
        metricas["total"], metricas["exitos"], metricas["errores_controlados"], metricas["fallos_inesperados"]
    )


if __name__ == "__main__":
    bitacora_fj, ruta_log = iniciar_bitacora()
    try:
        ejecutar_12_simulaciones(bitacora_fj, ruta_log)
    finally:
        # Cierra y libera los manejadores del log de forma ordenada al finalizar.
        bitacora_fj.info("Cierre de bitacora de ejecucion.")
        for handler in list(bitacora_fj.handlers):
            handler.flush()
            handler.close()
            bitacora_fj.removeHandler(handler)