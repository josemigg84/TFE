import time
import datetime as dt
import os
import contextlib
import settings
from snap7.util import get_bool, get_word, get_dword, set_bool, get_byte
import snap7

class PLCClient:
    def __init__(self, logger):
        self._ip = settings.PLC_IP
        self._rack = settings.PLC_RACK
        self._slot = settings.PLC_SLOT
        self._logger = logger
        self._client = snap7.client.Client()
        self._connected = False

    def _reset_client(self):
        try: self._client.disconnect()
        except Exception: pass
        try: self._client.destroy()
        except Exception: pass
        self._client = snap7.client.Client()
        self._connected = False

    def connect(self, retry: bool = True, delay_s: float = 2.0) -> None:
        if self._connected and self._client.get_connected():
            return
        while True:
            self._reset_client()
            try:
                with open(os.devnull, "w") as devnull, contextlib.redirect_stderr(devnull):
                    self._client.connect(self._ip, self._rack, self._slot)
                if self._client.get_connected():
                    self._connected = True
                    self._logger.log(f"PLC conectado: ip={self._ip}, rack={self._rack}, slot={self._slot}")
                    return
                raise RuntimeError("Conexión no establecida")
            except (RuntimeError, OSError) as e:
                self._connected = False
                self._logger.log(f"No se ha podido conectar con el PLC: {e}")
                if not retry:
                    raise
                time.sleep(delay_s)

    def reconnect(self, delay_s: float = 2.0) -> None:
        self._reset_client()
        self.connect(retry=True, delay_s=delay_s)

    def disconnect(self):
        try:
            if self._connected:
                self._client.disconnect()
                self._logger.log("PLC desconectado.")
        finally:
            self._connected = False

    # Metodo:  Lee 10 bytes del DB y devuelve trigger, pin, skid, modelo.
    def leer(self):
        try:
            with open(os.devnull, 'w') as devnull, contextlib.redirect_stderr(devnull):
                data = self._client.db_read(settings.DB_NUM, start=settings.INICIO_BYTES, size=settings.TOTAL_BYTES)
        except (RuntimeError, OSError) as e:
            self._connected = False  # Reconectar en el siguiente bucle
            raise ValueError("Fallo al leer datos del PLC")

        trigger = get_bool(data, settings.TRIGGER_BYTE, settings.TRIGGER_BIT)
        pin = get_dword(data, settings.PIN_OFFSET)
        skid = get_word(data, settings.SKID_OFFSET)
        modelo = get_word(data, settings.MODELO_OFFSET)

        dd = get_byte(data, settings.APP_DATETIME_OFFSET+0)
        mm = get_byte(data, settings.APP_DATETIME_OFFSET+1)
        yy = get_byte(data, settings.APP_DATETIME_OFFSET+2)
        hh = get_byte(data, settings.APP_DATETIME_OFFSET+3)
        mi = get_byte(data, settings.APP_DATETIME_OFFSET+4)
        ss = get_byte(data, settings.APP_DATETIME_OFFSET+5)
        fecha_app = dt.datetime(int(yy)+2000, int(mm), int(dd), int(hh), int(mi), int(ss))


        return {"trigger": trigger, "pin": pin, "skid": skid, "modelo": modelo, "fecha_app": fecha_app}

    def escribir(self):

        try:
            data = self._client.db_read(settings.DB_NUM, start=settings.INICIO_BYTES, size=settings.TOTAL_BYTES)
            trigger = get_bool(data, settings.TRIGGER_BYTE, settings.TRIGGER_BIT)
            ack = get_bool(data, settings.ACK_BYTE, settings.ACK_BIT)
            if trigger and not ack:
                buf = bytearray(self._client.db_read(settings.DB_NUM, settings.ACK_BYTE, 1))  # lee 1 byte
                set_bool(buf, 0, settings.ACK_BIT, True)  # cambia el bit dentro del buffer
                self._client.db_write(settings.DB_NUM, settings.ACK_BYTE, bytes(buf))  # escribe el byte al PLC
                self._logger.log("Enviado ack a PLC")
            else:
                self._logger.log("No se envía ack a PLC, no hay condiciones")
        except (RuntimeError, OSError) as e:
            raise ValueError("Fallo al escibir ack en el PLC")





