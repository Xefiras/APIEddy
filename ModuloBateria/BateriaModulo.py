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
        voltage = chan.voltage

        # Calculate the battery percentage based on the voltage
        carga = max(0, min(100, int(( (voltage - self.MIN_VOLTAGE) / (self.MAX_VOLTAGE - self.MIN_VOLTAGE)) * 100 )))
        return round(carga)

    def get_cargando(self):
        pin_cargando = digitalio.DigitalInOut(board.D6)
        pin_cargando.direction = digitalio.Direction.INPUT
        return pin_cargando.value # True cargando || False no

    def get_tiempo_restante(self):
        carga = self.get_carga()
        tiempo_restante = (carga / 100) * self.tiempo_total
        return round(tiempo_restante)

    # Por favor sirve
    def get_status(self):
        return True, [self.get_carga(), self.get_cargando(), self.get_tiempo_restante()]
