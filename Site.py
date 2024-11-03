# -*- coding: utf-8 -*-
"""
Created on Sun Sept  29 11:38:07 2024

@author: MIT Wind

Basic Wind Farm site modules for power calculation and layout optimization. Coordinates of the turbines are from ArcGis

Assumptions:
    The site is a Uniform Weibull Site with uniform sector-dependent Weibull distributed wind speed.
    No topography or roughness considerations in defining the wind resource. This is just a general wind climate, but it is good enough for noise analysis
    The site uses a user-defined layout
    Turbines used: V163-4.5
    Air density : 1.225
    Turbulence Intensity: 0.11, Roughness: 0.01
"""
#%%
from py_wake import np
from geopy.distance import geodesic
from py_wake.site._site import UniformWeibullSite
from py_wake.site.xrsite import GlobalWindAtlasSite
from py_wake.wind_turbines import OneTypeWindTurbines
from py_wake.wind_turbines.power_ct_functions import PowerCtFunctionList
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
from py_wake.wind_turbines.generic_wind_turbines import GenericWindTurbine
from py_wake.wind_turbines import WindTurbine, WindTurbines
from power_curve import generate_power_curve
import pandas as pd
import matplotlib.pyplot as plt
import utm
#%%
# std_df = pd.read_csv('CSV with turbine layout') # Dataframe with standard wind layout
def gen_initial_cood(centroid_lat, centroid_lon, radius_m=600, num_points=45):
    """
    Generates an array of initial coordinates within a given radius from a centroid.
    """    
    latitudes = np.zeros(num_points)
    longitudes = np.zeros(num_points)
    # Generate points uniformly spaced around a circle
    angles = np.linspace(0, 2 * np.pi, num_points)
    for i, angle in enumerate(angles):
        # Calculate the latitude and longitude at the specified distance and angle
        point = geodesic(meters=radius_m).destination((centroid_lat, centroid_lon), angle)
        latitudes[i] = point.latitude
        longitudes[i] = point.longitude
    return latitudes, longitudes

lat_wt, lon_wt  = gen_initial_cood(124.7488486, 42.20889)
wt_x, wt_y, zone_number, zone_letter= utm.from_latlon(lat_wt,lon_wt) # Turbine locations for Standard Wind

#%%
# Generated Power Curves without smoothing
power_c, speed = generate_power_curve(3,12,25,8,167,0.2)
v163_wsp = np.array(speed) # Wind speeds for power curves
std_power = np.array(power_c) # Standard wind power values
std_ct = 1 # Add ct curves

V163_power_curve = np.column_stack((v163_wsp, std_power)) # Stack to create power and ct curves
V163_ct_curve = np.column_stack((v163_wsp, std_ct))

#%%
class VWT45(WindTurbine): #Vestas 4.5 MW Turbine based on Power and CT curves
    def __init__(self, method='linear'):
        """
        Parameters
        ----------
        method : {'linear', 'pchip'}
            linear(fast) or pchip(smooth and gradient friendly) interpolation
        """
        WindTurbine.__init__(self, name='VWT45', diameter=163, hub_height=119,
                             powerCtFunction=PowerCtTabular(V163_power_curve[:, 0], V163_power_curve[:, 1], 'kw',
                                                            V163_ct_curve[:, 1], method=method))

WindeckerVWT = VWT45

class Kratos(GlobalWindAtlasSite):
    """
    Note that this is not a real representation of the wind resource at the site. It is just for comparison purposes
    Here are getting the general wind climate at two different hub height based on which turbine we are using.
    It will be overriden by the 8760 values during the simulation.
    """
    def __init__(self, ti=0.11, roughness= 0.01, shear=None):
          latm, longm = 1, 1  # Define the center point coordinates of the farm 
          height = 1 # Hub height
          GlobalWindAtlasSite.__init__(self, latm, longm, height, roughness, ti, shear=shear)
          self.initial_position = np.array([wt_x, wt_y]).T
          
def main():
    # For sanity, lets plot the power curve for both turbines  
    wt45 = VWT45()
    ws = np.arange(3, 25)
    plt.plot(ws, wt45.power(ws), '.-')
    plt.xlabel('Wind speed [m/s]')
    plt.ylabel('Power [W]')
    plt.title("Power Curves V163-4.5")
    plt.legend(['V163-4.5'])
    plt.show()


if __name__ == '__main__':
    main()
