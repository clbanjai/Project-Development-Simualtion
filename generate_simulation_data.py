import pandas as pd
import math
import numpy as np
from scipy import optimize

def generate_power_curve(cut_in_ws,rated_ws,cut_out_ws,rated_power,diameter,Turbine,dt=0.5,density=1.225):
    """
    Generates a power curve for a wind turbine based on its geometric and operational properties.

    Parameters:
    - cut_in_ws (float): The wind speed at which the turbine starts generating power (m/s).
    - rated_ws (float): The wind speed at which the turbine reaches its rated power (m/s).
    - cut_out_ws (float): The wind speed at which the turbine stops generating power (m/s).
    - rated_power (float): The maximum power output of the turbine (mW).
    - diameter (float): The diameter of the turbine rotor (m).
    - Turbine (str): The name of the turbine used as the filename for saving the power curve data.
    - dt (float, optional): The step interval for wind speed (m/s). Default is 0.5 m/s.
    - density (float, optional): The air density (kg/m^3). Default is 1.225 kg/m^3 (at sea level).

    Returns:
    - power (list): The list of power outputs for each wind speed in the velocity list.
    - velocity (list): The list of wind speeds used to generate the power curve.

    Saves:
    - A CSV file named after the turbine, containing wind speed and corresponding power output.
    """
    swept_area=math.pi*(diameter/2)**2
    cp_max=2*rated_power/(density*swept_area*rated_ws**3)
    velocity=[]
    i = 0
    while i <= cut_out_ws+1:
        velocity.append(i)
        i += dt
    power=[]
    for value in velocity:
        if cut_in_ws<=value and value<rated_ws:
            power.append(1/2*density*swept_area*cp_max*value**3)
        elif value>=rated_ws and value<cut_out_ws:
            power.append(rated_power)
        else:
            power.append(0)

    return power, velocity

def generatate_power_coeffiecients(power,velocity,diameter, rho= 1.125):
    """Use power curve and """
    power_array=np.array(power)
    velocity_array=np.array(velocity)
    swept_area=math.pi*(diameter/2)**2
    Cp = power_array / (0.5 * rho * np.pi * swept_area* velocity_array**3)
    Cp = np.nan_to_num(Cp, nan=0.0)

    return Cp


def Cp_to_Ct(Cp):
    """Convert Cp to Ct in a compact function from just an array of C_P values."""

    def Cp_a(a, Cp):
        """Computes C_P(a) = 4a(1-a)^2 in residual form"""
        return 4 * a * (1 - a)**2 - Cp

    # adjust Cp to max out at Betz:
    Cp = Cp / np.max(Cp) * 16/27
    a = np.zeros_like(Cp)
    Cp_guess = 0
    for k, _Cp in enumerate(Cp[::-1]):  # iterate thru backward
        a[k] = optimize.fsolve(Cp_a, Cp_guess, _Cp)[0]
        Cp_guess = a[k]

    # we built the "a" vector backward so we need to flip it back:
    a = a[::-1]

    Ct =  4 * a * (1 - a)
    return Ct


def gen_simulation_Data(cut_in_ws,rated_ws,cut_out_ws,rated_power,diameter,Turbine,dt=0.5,density=1.225):
    power, velocity=generate_power_curve(cut_in_ws,rated_ws,cut_out_ws,rated_power,diameter,Turbine)
    Cp=generatate_power_coeffiecients(power,velocity,diameter)
    Ct=Cp_to_Ct(Cp)
    df = pd.DataFrame({
        'Wind Speed (m/s)': velocity,
        'Power Output (kW)': power,
        'Thrust Coeffient' : Ct
    })
    # df.to_csv(f'{Turbine}.csv', index=False)
    return df

if __name__ == "__main__":
    data = gen_simulation_Data(3,12,25,8,167,'SG 8.0-167 DD')
    thrust = data["Thrust Coeffient"].to_list()
    print(thrust)
