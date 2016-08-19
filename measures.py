class Measures:
    TEMPERATURE = 'temperature'
    HUMIDITY = 'humidity'
    CO2 = 'co2'
    LIGHT = 'light'
    GAS = 'gas'
    MOTION = 'motion'
    CANCAM = 'cameraAllowed'
    TIME = 'time'

    BOOL_VARS = [MOTION, CANCAM]
    NUM_VARS = [TEMPERATURE, HUMIDITY, CO2, GAS, LIGHT]
    ALL_VARS = [TEMPERATURE, HUMIDITY, CO2, LIGHT, GAS, MOTION, CANCAM]

    SYNONIMS = {
        TEMPERATURE: TEMPERATURE,
        'temp': TEMPERATURE,
        't': TEMPERATURE,
        HUMIDITY: HUMIDITY,
        'hum': HUMIDITY,
        'h': HUMIDITY,
        CO2: CO2,
        'co': CO2,
        LIGHT: LIGHT,
        'l': LIGHT,
        GAS: GAS,
        'g': GAS,
        MOTION: MOTION,
        'mot': MOTION,
        'm': MOTION,
        CANCAM: CANCAM,
        'camalowed': CANCAM,
        'cancam': CANCAM
    }

    OP_SYNS = {
        '<': '<', '<=': '<', 'less' : '<', 'smaller': '<',
        'bigger': '>', 'greater' : '>', 'larger': '>', '>' : '>', '>=' : '>=',
        'equal': '=',  'equals': '=',  '=' : '=', '==': '='
    }

    def parse_op(self, name: str):
        return self.OP_SYNS.get(name.strip().lower(), False)

    def find_var_by_name(self, name: str):
        return self.SYNONIMS.get(name.strip().lower(), False)


    def list_synonims(self, name: str):
        if not self.find_var_by_name(name.strip().lower()):
            return []

        res = {}
        for key in self.SYNONIMS.keys():
            real_key = self.SYNONIMS[key]
            real_value = key

            if not real_key in res.keys():
                res[real_key] = [real_value]
            else:
                res[real_key].push(real_value)

        return res
