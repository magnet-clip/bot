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

def parse_op(name: str):
    name = name.lower()
    if name == 'less' or name == 'lower' or name == 'smaller' or name == '<' or name == '<=':
        return '<'
    if name == 'bigger' or name == 'greater' or name == 'larger' or name == '>' or name == '>=':
        return '>'
    if name == 'equal' or name == 'equals' or name == '=' or name == '==':
        return '='
    return False


def find_var_by_name(name: str):
    return SYNONIMS.get(name.lower(), False)


def list_synonims(name: str):
    if not find_var_by_name(name.lower()):
        return []

    res = {}
    for key in SYNONIMS.keys():
        real_key = SYNONIMS[key]
        real_value = key

        if res.get(real_key) is None:
            res[real_key] = [real_value]
        else:
            res[real_key].push(real_value)

    return res