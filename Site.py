"""
Created on Sun Sept  29 11:38:07 2024

@author: MIT Wind

Basic Wind Farm site modules for power calculation and layout optimization. Coordinates of the turbines are from ArcGis

Assumptions:
    The site is a Uniform Weibull Site with uniform sector-dependent Weibull distributed wind speed.
    No topography or roughness considerations in defining the wind resource. This is just a general wind climate, but it is good enough for noise analysis
    The site uses a user-defined layout
    Turbines used: V236 - 15 MW Turbine
    Hub Height: 150 m
    Air density : 1.225
    Turbulence Intensity: 0.11, Roughness: 0.01
"""
import numpy as np
from py_wake.site.xrsite import GlobalWindAtlasSite
from py_wake.wind_turbines.power_ct_functions import PowerCtTabular
from py_wake.wind_turbines import WindTurbine
from generate_simulation_data import gen_simulation_Data
from geopy.distance import geodesic
import pandas as pd
import matplotlib.pyplot as plt
import utm
from scipy.spatial import ConvexHull




# Define the wind turbine object
class V236(WindTurbine): #V236   15.0 MW Turbine based on Power and CT curves, changed from siemens gamesa 8MW
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
# class Kratos(GlobalWindAtlasSite):
#     # check turbulance again, value is too high NREL windtoolkit, or NOW23 (National Offshore Wind 23)
#     #KIRBY says TI = 0.03-0.1 but check again
#     def __init__(self, lat, lon , height, num_points, ti=0.11, roughness= 0.01, shear=None):
#           self.lat, self.lon = lat, lon
#         #   self.height = height
#           self.num_points = num_points
#           GlobalWindAtlasSite.__init__(self, lat, lon, height, roughness, ti, shear=shear)
#         #   self.initial_position = np.array([coord()])

#     def initial_coordinates(self):
#         """
#         Takes center lat long of site.
#         Returns the initial positions of the 4 turbines
#         in utm coordinates
#         """
#         lat_turbine = np.zeros(self.num_points)
#         lon_turbine = np.zeros(self.num_points)
#         # Generate points uniformly spaced around a circle
#         angles = np.linspace(0, 2 * np.pi, self.num_points)
#         for i, angle in enumerate(angles):
#             # Calculate the latitude and longitude at the specified distance and angle
#             point = geodesic(meters=200).destination((self.lat, self.lon), angle)
#             lat_turbine[i] = point.latitude
#             lon_turbine[i] = point.longitude
#         # lat_turbine = np.array([self.lat-0.004, self.lat-0.003, self.lat -0.002, self.lat - 0.001]) # Initial latitudes for turbines
#         # lon_turbine = np.array([self.lon-0.001, self.lon-0.002, self.lon -0.003, self.lon - 0.004]) # Initial latitudes for turbines
#         wt_x, wt_y, zone_number, zone_letter = utm.from_latlon(lat_turbine, lon_turbine)
#         return wt_x, wt_y,zone_number, zone_letter
from geopy.distance import geodesic
import numpy as np
import utm

from py_wake.site.xrsite import GlobalWindAtlasSite

class Kratos(GlobalWindAtlasSite):
    def __init__(self, lat, long, height, num_points, ti=0.11, roughness=0.01, shear=None):
        self.lat, self.long = lat, long
        self.num_points = num_points
        GlobalWindAtlasSite.__init__(self, lat = lat, long = long, height=height, roughness=roughness, ti = ti, shear=shear)
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
            point = geodesic(meters=200).destination((self.lat, self.long), angle)
            lat_turbine[i] = point.latitude
            lon_turbine[i] = point.longitude
        # lat_turbine = np.array([self.lat-0.004, self.lat-0.003, self.lat -0.002, self.lat - 0.001]) # Initial latitudes for turbines
        # lon_turbine = np.array([self.lon-0.001, self.lon-0.002, self.lon -0.003, self.lon - 0.004]) # Initial latitudes for turbines
        wt_x, wt_y, zone_number, zone_letter = utm.from_latlon(lat_turbine, lon_turbine)
        return wt_x, wt_y,zone_number, zone_letter
    # def initial_coordinates(self,num_rows,num_cols, corner_lats, corner_lons, margin_ratio=0.2):
    #     """
    #     Generate turbine positions in a 6x4 grid fully contained within the
    #     area defined by corner coordinates, with reduced spacing between turbines.

    #     margin_ratio: float between 0 and 1. Higher value -> tighter grid.
    #     """
    #     # num_cols = 12
    #     # num_rows = 2

    #     if self.num_points != num_cols * num_rows:
    #         raise ValueError(f"Expected num_points to be {num_cols * num_rows} for a {num_cols}x{num_rows} grid.")

    #     # Convert corner lat/lons to UTM
    #     utm_x, utm_y, zone_number, zone_letter = utm.from_latlon(np.array(corner_lats), np.array(corner_lons))

    #     # Define full bounding box
    #     min_x, max_x = min(utm_x), max(utm_x)
    #     min_y, max_y = min(utm_y), max(utm_y)

    #     # Apply margins
    #     width = max_x - min_x
    #     height = max_y - min_y
    #     margin_x = margin_ratio * width
    #     margin_y = margin_ratio * height

    #     usable_min_x = min_x + margin_x
    #     usable_max_x = max_x - margin_x
    #     usable_min_y = min_y + margin_y
    #     usable_max_y = max_y - margin_y

    #     # Compute tighter grid spacing
    #     dx = (usable_max_x - usable_min_x) / (num_cols - 1)
    #     dy = (usable_max_y - usable_min_y) / (num_rows - 1)

    #     lat_turbine = []
    #     lon_turbine = []

    #     for i in range(num_rows):
    #         for j in range(num_cols):
    #             x = usable_min_x + j * dx
    #             y = usable_max_y - i * dy
    #             lat, lon = utm.to_latlon(x, y, zone_number, zone_letter)
    #             lat_turbine.append(lat)
    #             lon_turbine.append(lon)

    #     lat_turbine = np.array(lat_turbine)
    #     lon_turbine = np.array(lon_turbine)
    #     wt_x, wt_y, _, _ = utm.from_latlon(lat_turbine, lon_turbine)
    #     return wt_x, wt_y, zone_number, zone_letter


# #only make changes here

# from py_wake.wind_farm_models import PropagateDownwind
# from py_wake.deficit_models.gaussian import BastankhahGaussianDeficit
# from py_wake.superposition_models import SquaredSum
# from py_wake.flow_map import HorizontalGrid



# n_wts = 24 # Number of turbines in the farm

# #turbine specifications

Turbine_name = "V236"
hub_height = 150
diameter = 236
rated_ws = 11.1
cut_out_ws = 33
rated_power = 15
cut_in_ws = 3

# #coordinates of the center point
# center_latitude = 42.21031
# center_longitude = -124.7488486

# #coordinates of the coorner points
# import numpy as np

# # Original coordinates
# latitudes = np.array([42.241220, 42.235171, 42.193742, 42.199795])
# longitudes = np.array([-124.696095, -124.754752, -124.746961, -124.688304])

# # Vertical shrink factor (e.g., 0.9 = shrink by 10%)
# shrink_factor = 0.8

# # Find center latitude
# lat_center = np.mean(latitudes)

# # Apply vertical scaling
# latitudes_scaled = lat_center + shrink_factor * (latitudes - lat_center)

# # Result: longitudes stay the same, latitudes get compressed
# print("New latitudes:", latitudes_scaled)
# print("Longitudes (unchanged):", longitudes)


# site = Kratos(lat=center_latitude, lon=center_longitude, height=hub_height,num_points=n_wts)

# wt_x,wt_y , zone_number, zone_letter= site.initial_coordinates(latitudes,longitudes)


# # print(wt_x)
# corner_x, corner_y, _, _= utm.from_latlon(latitudes,longitudes,zone_number, zone_letter)

# points = np.column_stack((corner_x, corner_y))
# hull = ConvexHull(points)

# # Plot the convex hull by connecting the vertices in order
# turbine = V236(cut_in_ws ,rated_ws ,cut_out_ws ,rated_power ,diameter,Turbine_name, hub_height)

# # Close the loop by adding the first point to the end of the hull vertices
# wfm = PropagateDownwind(site, turbine, wake_deficitModel=BastankhahGaussianDeficit(use_effective_ws=False),
#                                         superpositionModel=SquaredSum(), deflectionModel=None) # Wind farm model
# sim_res_op = wfm(wt_x, wt_y) # Simulate result for optimize turbine placement

# wdir = 0 # Wind direction to plot flow map
# wsp = 11 # Wind speed to plot flow map

# xmin = min(wt_x)-1000
# xmax = max(wt_x)+1000
# ymin = min(wt_y)-1000
# ymax = max(wt_y)+1000
# plt.figure(figsize=(8,6))

# flow_map = sim_res_op.flow_map(HorizontalGrid(x = np.arange(xmin,xmax,100),),
#                             wd=wdir,
#                             ws = wsp).plot_wake_map()
# # Combine x and y into an array of (x, y) points
# points = np.column_stack((corner_x, corner_y))
# hull = ConvexHull(points)

# # Plot the convex hull by connecting the vertices in order
# for simplex in hull.simplices:
#     plt.plot(points[simplex, 0], points[simplex, 1], 'r-', linewidth=1)

# # Close the loop by adding the first point to the end of the hull vertices
# plt.plot(points[hull.vertices, 0], points[hull.vertices, 1], 'r-', linewidth=1, label='Site Boundary')

# plt.xlabel('x [m]')
# plt.ylabel('y [m]')
# plt.title('Wind Farm Layout'+ f' {wdir} deg and {wsp} m/s')
# plt.xlim(xmin,xmax)
# plt.legend()
# plt.show()
def main():
    # Create the wind turbine object
    wt3 = V236(
        cut_in_ws=cut_in_ws,
        rated_ws=rated_ws,
        cut_out_ws=cut_out_ws,
        rated_power=rated_power,
        diameter=diameter,
        Turbine=Turbine_name,
        height=hub_height
    )

    # Wind speed range
    ws = np.arange(0, 35)
    ct_values = wt3.ct(ws)
    # Plot setup
    plt.figure(figsize=(10, 6))

    # Power curve
    plt.plot(ws, ct_values, '.-', label='V236-15MW')

    # Fill area under the curve
    plt.fill_between(ws, ct_values, alpha=0.3, color='skyblue')

    # Vertical lines for key wind speeds
    # plt.axvline(x=cut_in_ws, color='green', linestyle='--', label='Cut-in wind speed')
    # plt.axvline(x=rated_ws, color='orange', linestyle='--', label='Rated wind speed')
    # plt.axvline(x=cut_out_ws, color='red', linestyle='--', label='Cut-out wind speed')

    # Horizontal line for rated power
    # plt.axhline(y=rated_power, color='blue', linestyle=':', label='Rated power')

    # Labels, grid, legend
    plt.xlabel('Wind speed [m/s]')
    plt.ylabel('Thrust Coefficient')
    plt.title(r'Ct curve – V236-15MW')
    plt.grid(True)
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
