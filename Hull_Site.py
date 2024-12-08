"""
Created on Tue April  9 11:38:07 2024

@author: WilhemHector

Hull initial wind turbine site for optimization purposes.
Coordinates of turbines are obained by doing a simple layout optimization

Assumptions:
    The site is a Uniform Weibull Site with uniform sector-dependent Weibull distributed wind speed.

    The wind resource comes from the Global Wind Climate (GWC) from Global Wind Atlas based on
    latitude and longitude which is interpolated at specific roughness and height.
    This approach is only valid for offshore farms with homogeous roughness at the site and around.

    Turbines used: V163-4.5
    Air density : 1.225
    Turbulence Intensity: 0.11, Roughness: 0.01

"""
from py_wake import np
from py_wake.site.xrsite import GlobalWindAtlasSite
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
from py_wake.wind_turbines import WindTurbine
from geopy.distance import geodesic
import pandas as pd
import matplotlib.pyplot as plt
import utm

# Power  and CT Curves for V63
frame = pd.read_csv('SG 8.0-167 DD.csv')
w_speed = np.array(frame['speed'])
power_curve = np.array(frame['power'])
ct_curve = np.array(frame['ct'])

# Wind Farm Layout

# wt_x, wt_y = initial_coordinates(42.30,-70.84) # Initial coordinates for the farm

V90_power_curve = np.column_stack((w_speed, power_curve))
V90_ct_curve = np.column_stack((w_speed, ct_curve))

# Define the wind turbine object
class VWT3(WindTurbine): #Vestas 3.0 MW Turbine based on Power and CT curves
    def __init__(self, method='linear'):
        """
        Parameters
        ----------
        method : {'linear', 'pchip'}
            linear(fast) or pchip(smooth and gradient friendly) interpolation
        """
        WindTurbine.__init__(self, name='SG167', diameter=167, hub_height=100,
                             powerCtFunction=PowerCtTabular(V90_power_curve[:, 0], V90_power_curve[:, 1], 'kw',
                                                            V90_ct_curve[:, 1], method=method))
HullVWT = VWT3

# Define the site object
class HullSite45(GlobalWindAtlasSite):

    def __init__(self, lat, lon , ti=0.11, roughness= 0.01, shear=None):
          self.lat, self.lon = lat, lon
        #   latm, longm = 42.30, -70.84
          height = 100
          GlobalWindAtlasSite.__init__(self, self.lat, self.lon, height, roughness, ti, shear=shear)
        #   self.initial_position = np.array([coord()])

    def initial_coordinates(self, num_points=45):
        """
        Takes center lat long of site.
        Returns the initial positions of the 4 turbines
        in utm coordinates
        """
        lat_turbine = np.zeros(num_points)
        lon_turbine = np.zeros(num_points)
    # Generate points uniformly spaced around a circle
        angles = np.linspace(0, 2 * np.pi, num_points)
        for i, angle in enumerate(angles):
            # Calculate the latitude and longitude at the specified distance and angle
            point = geodesic(meters=200).destination((self.lat, self.lon), angle)
            lat_turbine[i] = point.latitude
            lon_turbine[i] = point.longitude
        # lat_turbine = np.array([self.lat-0.004, self.lat-0.003, self.lat -0.002, self.lat - 0.001]) # Initial latitudes for turbines
        # lon_turbine = np.array([self.lon-0.001, self.lon-0.002, self.lon -0.003, self.lon - 0.004]) # Initial latitudes for turbines
        wt_x, wt_y, zone_number, zone_letter = utm.from_latlon(lat_turbine, lon_turbine)
        return wt_x, wt_y,zone_number, zone_letter

def main():
    # For sanity, lets plot the power curve of the turbine
    wt3 = VWT3()
    ws = np.arange(3, 25)
    plt.plot(ws, wt3.power(ws), '.-')
    plt.xlabel('Wind speed [m/s]')
    plt.ylabel('Power [W]')
    plt.title("Power Curves V90-3")
    plt.legend(['V90-3'])
    plt.show()


if __name__ == '__main__':
    main()
