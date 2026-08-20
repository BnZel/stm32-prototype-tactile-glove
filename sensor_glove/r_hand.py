# REFERENCES:
# https://blog.embeddedexpert.io/?p=3257
# https://andykong.org/blog/velostatlinqstat/
# https://www.fsrexpert.com/force-sensor-vs-pressure-sensor-the-real-difference-guide/
# https://learn.adafruit.com/force-sensitive-resistor-fsr/using-an-fsr


R_HAND = {
    'INDEX': 
            {
                'PINS': {'DP':['A0','A1','A2','A3','A4']}, 
                'PRESSURE':{'DP':[("NONE", 2.5), ("LIGHT", 2.3), ("MEDIUM", 1.6), ("HEAVY", 1.2)],
                            'MP':[("NONE", 2.0), ("LIGHT", 2.2), ("MEDIUM", 1.7), ("HEAVY", 1.2)],
                            'PP':[("NONE", 2.8), ("LIGHT", 1.6), ("MEDIUM", 1.3), ("HEAVY", 1.2)]
                            }
            }
}



def pressure_status(vout,region):
    '''
    Using baseline data to label force\n 
    "NONE", "LIGHT", "MEDIUM", "HEAVY"
    '''
    calib = R_HAND['INDEX']['PRESSURE']

    if region in calib:
        calib = calib.get(region)

        # NONE
        if vout >= calib[0][1]:
            return calib[0][0]

        # LIGHT
        elif vout >= calib[1][1]:
            return calib[1][0]

        # MEDIUM
        elif vout >= calib[2][1]:
            return calib[2][0]

        # HEAVY
        elif vout >= calib[3][1] or vout >= 0.7:
            return calib[3][0]
    else:
        return "N/A"
  

def calculate_fsr(vout, region, vcc=3.3, resistor=3300):
    '''
    FSR = (Vin - R) / (VCC - Vin)\n
    vout -> Velostat output voltage in millivolts (default is 3300 [3.3V])\n
    region -> Name of finger region ("DP","MP","PP")\n
    vcc -> Input voltage\n
    resistor -> Resistor value (default is 3300 [3.3K])\n\n

    Returns fsr, conductance, newtons, grams
    '''

    # handle division by zero
    # due to voltage spikes and noise
    # on 1 millivolt and setting
    # to high resistance to avoid crashing
    if vout >=  (vcc - 0.001):
        fsr = 999999.0
    elif vout <= 0.001:
        fsr = 0.001
    else:
        # this formula is the FSR 
        # low side (resistor connected to VCC)
        fsr = (vout * resistor) / (vcc - vout) 

    STATUS = pressure_status(vout, region)

    # convert to micromhos
    # to measure in newtons
    conductance = 1000000 / fsr  

    newtons = conductance / 80 if conductance <= 1000 else (conductance - 100) / 30

    # newtons to grams
    grams = newtons * 101.9716

    return STATUS, round(fsr,2), int(conductance), round(newtons,2), round(grams,1)