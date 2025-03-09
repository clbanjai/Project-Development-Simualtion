"""
Created on Sun Sept  29 11:38:07 2024

@author: MIT Wind

Basic Wind Farm site modules for power calculation and layout optimization. Coordinates of the turbines are from ArcGis

Assumptions:
    The site is a Uniform Weibull Site with uniform sector-dependent Weibull distributed wind speed.
    No topography or roughness considerations in defining the wind resource. This is just a general wind climate, but it is good enough for noise analysis
    The site uses a user-defined layout
    Turbines used: SG8-167
    Air density : 1.225
    Turbulence Intensity: 0.11, Roughness: 0.01
"""
from py_wake import np
from py_wake.site.xrsite import GlobalWindAtlasSite
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
from py_wake.wind_turbines import WindTurbine
from generate_simulation_data import gen_simulation_Data
from geopy.distance import geodesic
import pandas as pd
import matplotlib.pyplot as plt
import utm




# Define the wind turbine object
class V236(WindTurbine): #Siemens Gamesa 8.0 MW Turbine based on Power and CT curves
    def __init__(self,cut_in_ws,rated_ws,cut_out_ws,rated_power,diameter,Turbine, height, method='linear'):
        """
        Parameters
        ----------
        method : {'linear', 'pchip'}
            linear(fast) or pchip(smooth and gradient friendly) interpolation
        """
        frame = gen_simulation_Data(cut_in_ws,rated_ws,cut_out_ws,rated_power,diameter,Turbine)
        w_speed = np.array(frame['Wind Speed (m/s)'])
        power_curve = np.array(frame['Power Output (kW)'])
        ct_curve = np.array(frame['Thrust Coeffient'])

        power_c = np.column_stack((w_speed, power_curve))
        thrust_c = np.column_stack((w_speed, ct_curve))

        WindTurbine.__init__(self, name=Turbine, diameter=diameter, hub_height=height,
                             powerCtFunction=PowerCtTabular(power_c[:, 0], power_c[:, 1], 'mw',
                                                            thrust_c[:, 1], method=method))

# Define the site object
class Kratos(GlobalWindAtlasSite):
    # check turbulance again, value is too high NREL windtoolkit, or NOW23 (National Offshore Wind 23)
    #KIRBY says TI = 0.03-0.1 but check again
    def __init__(self, lat, lon , height, num_points, ti=0.11, roughness= 0.01, shear=None):
          self.lat, self.lon = lat, lon
        #   self.height = height
          self.num_points = num_points
          GlobalWindAtlasSite.__init__(self, lat, lon, height, roughness, ti, shear=shear)
        #   self.initial_position = np.array([coord()])

    def initial_coordinates(self):
        """
        Takes center lat long of site.
        Returns the initial positions of the 4 turbines
        in utm coordinates
        """
        lat_turbine = np.zeros(self.num_points)
        lon_turbine = np.zeros(self.num_points)
    # Generate points uniformly spaced around a circle
        angles = np.linspace(0, 2 * np.pi, self.num_points)
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
    wt3 = V236(cut_in_ws=cut_in_ws,rated_ws=rated_ws,cut_out_ws=cut_out_ws,rated_power=rated_power,diameter=diameter,Turbine=Turbine_name,height=hub_height)
    ws = np.arange(3, 33)
    plt.plot(ws, wt3.power(ws)/(1000000), '.-')
    plt.xlabel('Wind speed [m/s]')
    plt.ylabel('Power [MW]')
    plt.title("Power Curve SG167-8")
    plt.legend(['SG167-8'])
    plt.show()


if __name__ == '__main__':
    main()
