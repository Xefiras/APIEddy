import busio
import digitalio
import board
from adafruit_mcp3xxx.analog_in import AnalogIn
from adafruit_mcp3xxx.mcp3008 import MCP3008

class BateriaModulo:
    VREF = 5.0 # Reference voltage
    MAX_VAL_ADC = 65535 # Maximum value of ADC
    TOTAL_TIME = 240 # Total time in minutes

    def __init__(self):
        self.spi = busio.SPI(board.SCK, board.MOSI, board.MISO) # SPI bus
        self.cs = digitalio.DigitalInOut(board.CE0) # Chip select
        self.mcp = MCP3008(self.spi, self.cs) # MCP3008 object

        self.last_voltage = None
        self.isCharging = False

    def leer_promedio(self, chan, iter=10):
        sum = 0
        for _ in range(iter):
            sum += chan.voltage
        promedio = sum / iter
        return promedio

    def get_carga(self):
        # Canal de carga
        chan = AnalogIn(self.mcp, 0)
        median_value = self.leer_promedio(chan, 10)
        # Calculo de carga
        carga0 = (median_value / self.MAX_VAL_ADC) * self.VREF
        carga = (chan.value) * (self.VREF / self.MAX_VAL_ADC)
        print(f"Valor digital promedio: {int(median_value)} | Voltaje: {carga0:.2f} V")
        # porcentaje
        carga0 = (carga / self.VREF) * 100
        return carga0

    def get_cargando(self):
        # Leer el canal analógico
        chan = AnalogIn(self.mcp, 0)
        current_voltage = self.leer_promedio(chan, 10)  # Promedio del voltaje actual

        if self.last_voltage is not None:
            # Detectar si el voltaje sube o baja bruscamente
            if current_voltage - self.last_voltage >= 0.4:
                self.is_charging = True  # Comienza a cargar
            elif self.last_voltage - current_voltage >= 0.4:
                self.is_charging = False  # Deja de cargar

        # Actualizar el último voltaje leído
        self.last_voltage = current_voltage

        return self.is_charging

    def get_tiempo_restante(self):
        percentage = self.get_carga()
        # Calculo de tiempo restante
        tiempo_restante = (percentage / 100) * self.TOTAL_TIME
        return round(tiempo_restante, 2)


    # Por favor sirve
    def get_status(self):
        return True, [self.get_carga(), self.get_cargando(), self.get_tiempo_restante()]


