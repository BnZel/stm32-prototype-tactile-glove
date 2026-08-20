from machine import Pin, ADC
from time import sleep
from r_hand import *

# PRESSURE SENSORS
idx_dp_ps = ADC(R_HAND['INDEX']['PINS']['DP'][0])
idx_mp_ps = ADC(R_HAND['INDEX']['PINS']['DP'][1])
idx_pp_ps = ADC(R_HAND['INDEX']['PINS']['DP'][2])

# POTENTIOMETERS
idx_dp_pot1 = ADC(R_HAND['INDEX']['PINS']['DP'][3])
idx_mp_pot2 = ADC(R_HAND['INDEX']['PINS']['DP'][4])

def to_voltage(raw_adc,vcc=3.3,max_val=4095):
    adc = raw_adc.read_u16() >> 4
    return adc * (vcc / max_val)

def to_angle(raw_adc, max_adc=4095, max_angle=330):
    adc = raw_adc.read_u16() >> 4
    return int((adc / max_adc) * max_angle)

while True:
    voltage_dp = to_voltage(idx_dp_ps)
    voltage_mp = to_voltage(idx_mp_ps)
    voltage_pp = to_voltage(idx_pp_ps)

    pot1_angle = to_angle(idx_dp_pot1)
    pot2_angle = to_angle(idx_mp_pot2)

    status_dp, fsr_dp, conductance_dp, newtons_dp, grams_dp = calculate_fsr(voltage_dp, "DP")
    status_mp, fsr_mp, conductance_mp, newtons_mp, grams_mp = calculate_fsr(voltage_mp, "MP")
    status_pp, fsr_pp, conductance_pp, newtons_pp, grams_pp = calculate_fsr(voltage_pp, "PP")

    # print(f"ANGLE => POT1: {pot1_angle}° | POT2: {pot2_angle}° || GRAMS => DP: {grams_dp} {status_dp} | MP: {grams_mp} {status_mp} | PP: {grams_pp} {status_pp}")
    print(f"{pot1_angle},{pot2_angle},{grams_dp},{status_dp},{grams_mp},{status_mp},{grams_pp},{status_pp}")

    sleep(0.05) 