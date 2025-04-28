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

        # Variables para detectar carga
        self.voltage_history = []
        self.history_size = 10  # Número de lecturas a promediar para detectar tendencia
        self.charging_threshold = 0.4  # Umbral de aumento de voltaje para considerar carga
        self.discharging_threshold = -0.4 # Umbral de disminución de voltaje para considerar descarga
        self.is_charging = False # Estado inicial

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
        carga = chan.value * (self.VREF / self.MAX_VAL_ADC)
        print(f"Valor digital promedio: {int(median_value)} | Voltaje: {carga0:.2f} V")
        carga0 = (carga / self.VREF) * 100
        return carga0

    def get_cargando(self):
        chan = AnalogIn(self.mcp, 0) # Asume canal 0 para el voltaje de la batería
        current_avg_voltage = self.leer_promedio(chan, 10) # Obtiene voltaje promediado

        # Añade el voltaje actual al historial
        self.voltage_history.append(current_avg_voltage)

        # Mantiene el tamaño del historial
        if len(self.voltage_history) > self.history_size:
            self.voltage_history.pop(0) # Elimina la lectura más antigua

        # Necesita suficiente historial para determinar la tendencia
        if len(self.voltage_history) < self.history_size:
            # Aún no hay suficientes datos, devuelve el estado anterior
            # o False si prefieres un estado inicial definido
            return self.is_charging

        # Calcula el cambio de voltaje entre la lectura más reciente y la más antigua del historial
        voltage_change = self.voltage_history[-1] - self.voltage_history[0]

        # Determina el estado de carga basado en la tendencia del voltaje
        if voltage_change > self.charging_threshold:
            self.is_charging = True
        elif voltage_change < self.discharging_threshold:
            self.is_charging = False
        # Opcional: Si el cambio está entre los umbrales, mantiene el estado actual
        # else:
        #    pass # self.is_charging no cambia

        return self.is_charging

    def get_tiempo_restante(self):
        percentage = self.get_carga()
        # Calculo de tiempo restante
        tiempo_restante = (percentage / 100) * self.TOTAL_TIME
        return round(tiempo_restante, 2)


    # Por favor sirve
    def get_status(self):
        return True, [self.get_carga(), self.get_cargando(), self.get_tiempo_restante()]


