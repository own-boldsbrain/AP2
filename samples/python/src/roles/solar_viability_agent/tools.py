# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tools for the Solar Viability Agent."""

import pandas as pd
import pvlib
from google.adk.tools.tool_context import ToolContext


async def calculate_solar_position(
    latitude: float, longitude: float, date: str, tool_context: ToolContext
) -> str:
    """Calculates the solar position for a given location and date.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
        date: Date in ISO format (e.g., '2023-01-01T12:00:00').
        tool_context: The ADK supplied tool context.

    Returns:
        A string with the solar zenith and azimuth angles.
    """
    dt = pd.to_datetime(date)
    solpos = pvlib.solarposition.get_solarposition(dt, latitude, longitude)
    zenith = solpos['zenith'].iloc[0]
    azimuth = solpos['azimuth'].iloc[0]
    return f'Solar zenith: {zenith:.2f} degrees, Azimuth: {azimuth:.2f} degrees'


async def get_irradiance(
    latitude: float,
    longitude: float,
    date: str,
    tilt: float,
    azimuth: float,
    tool_context: ToolContext,
) -> str:
    """Calculates the irradiance on a tilted surface.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
        date: Date in ISO format (e.g., '2023-01-01T12:00:00').
        tilt: The tilt of the surface in degrees.
        azimuth: The azimuth of the surface in degrees.
        tool_context: The ADK supplied tool context.

    Returns:
        A string with the calculated irradiance components.
    """
    dt = pd.to_datetime(date)
    solpos = pvlib.solarposition.get_solarposition(dt, latitude, longitude)
    dni_extra = pvlib.irradiance.get_extra_radiation(dt)
    airmass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])
    linke_turbidity = pvlib.clearsky.lookup_linke_turbidity(
        dt, latitude, longitude
    )
    clearsky = pvlib.clearsky.ineichen(
        solpos['apparent_zenith'], airmass, linke_turbidity, altitude=0
    )
    total_irrad = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        solar_zenith=solpos['apparent_zenith'],
        solar_azimuth=solpos['azimuth'],
        dni=clearsky['dni'],
        ghi=clearsky['ghi'],
        dhi=clearsky['dhi'],
        dni_extra=dni_extra,
        model='haydavies',
    )
    return f'Irradiance (W/m^2): GHI={clearsky["ghi"].iloc[0]:.2f}, DNI={clearsky["dni"].iloc[0]:.2f}, DHI={clearsky["dhi"].iloc[0]:.2f}, POA Global={total_irrad["poa_global"].iloc[0]:.2f}'


async def get_pvsystem_performance(
    latitude: float,
    longitude: float,
    date: str,
    tilt: float,
    azimuth: float,
    module_pdc0: float,
    tool_context: ToolContext,
) -> str:
    """Calculates the performance of a simple PV system.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
        date: Date in ISO format (e.g., '2023-01-01T12:00:00').
        tilt: The tilt of the surface in degrees.
        azimuth: The azimuth of the surface in degrees.
        module_pdc0: The DC power of the module at standard test conditions.
        tool_context: The ADK supplied tool context.

    Returns:
        A string with the calculated PV system power output.
    """
    dt = pd.to_datetime(date)
    solpos = pvlib.solarposition.get_solarposition(dt, latitude, longitude)
    clearsky = pvlib.clearsky.ineichen(
        solpos['apparent_zenith'],
        pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith']),
    )

    # Simplified model, assuming a generic module and inverter
    temperature_model_parameters = (
        pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm'][
            'open_rack_glass_glass'
        ]
    )

    # Create a location object
    location = pvlib.location.Location(latitude, longitude)

    # Create a simple PVSystem
    system = pvlib.pvsystem.PVSystem(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        module_parameters={'pdc0': module_pdc0, 'gamma_pdc': -0.003},
        inverter_parameters={'pdc0': module_pdc0},
        temperature_model_parameters=temperature_model_parameters,
    )

    # Use ModelChain to get the performance
    mc = pvlib.modelchain.ModelChain(system, location)
    mc.run_model(clearsky)

    return f'PV System AC Power Output: {mc.results.ac.iloc[0]:.2f} W'
