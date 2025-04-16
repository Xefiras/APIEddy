import busio
import digitalio
import board
from adafruit_mcp3xxx.analog_in import AnalogIn
import adafruit_mcp3xxx.mcp3008 as MCP


class BateriaModulo:
    MIN_VOLTAGE = 11.0
    MAX_VOLTAGE = 16.8
    tiempo_total = 60 * 3 # 3 horas en minutos

    def __init__(self):
        self.spi = busio.SPI(board.SCK, board.MOSI, board.MISO) # SPI bus
        self.cs = digitalio.DigitalInOut(board.D5) # Chip select
        self.mcp = MCP.MCP3008(self.spi, self.cs) # MCP3008 object

    def get_carga(self):
        chan = AnalogIn(self.mcp, MCP.P0, MCP.P1)
        print("chan:", chan)
        voltage = chan.voltage
        print("voltage:", voltage)

        # Calculate the battery percentage based on the voltage
        carga = max(0, min(100, int(( (voltage - self.MIN_VOLTAGE) / (self.MAX_VOLTAGE - self.MIN_VOLTAGE)) * 100 )))
        print("carga:", carga)
        return round(carga)

    def get_cargando(self):
        pin_cargando = digitalio.DigitalInOut(board.D6)
        print("pin_cargando:", pin_cargando)
        pin_cargando.direction = digitalio.Direction.INPUT
        print("pin_cargando direction:", pin_cargando.direction)

        print("pin cargando value:", pin_cargando.value)




        return pin_cargando.value # True cargando || False no

    def get_tiempo_restante(self):
        carga = self.get_carga()
        print("carga:", carga)
        tiempo_restante = (carga / 100) * self.tiempo_total
        print("tiempo restante:", tiempo_restante)
        return round(tiempo_restante)

    def leer_todos_los_canales(self):
        print("Leyendo todos los canales del MCP3008:")
        for i in range(8):
            canal = AnalogIn(self.mcp, getattr(MCP, f'P{i}'))
            print(f"Canal P{i} -> Voltaje: {canal.voltage:.2f} V | Valor crudo: {canal.value}")

    def inspeccionar_pin_carga(self):
        pin_cargando = digitalio.DigitalInOut(board.D6)
        pin_cargando.direction = digitalio.Direction.INPUT
        print("Inspección del pin de carga (D6):")
        print(f" - Dirección: {pin_cargando.direction}")
        print(f" - Valor: {pin_cargando.value}")
        print(f" - Pull: {pin_cargando.pull}")

    def debug(self):
        print("\n--- DEBUG ---")
        self.leer_todos_los_canales()
        self.inspeccionar_pin_carga()
        print("Carga estimada:", self.get_carga())
        print("Cargando:", self.get_cargando())
        print("Tiempo restante:", self.get_tiempo_restante())

    # Por favor sirve
    def get_status(self):
        print("Configurando SPI:")
        print(f"SCK: {board.SCK}, MOSI: {board.MOSI}, MISO: {board.MISO}")

        print(f"SPI is locked? {self.spi.try_lock()}")
        self.spi.unlock()

        return True, [self.get_carga(), self.get_cargando(), self.get_tiempo_restante()]
