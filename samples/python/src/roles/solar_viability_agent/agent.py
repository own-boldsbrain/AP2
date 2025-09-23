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

"""A solar viability agent."""

from common.retrying_llm_agent import RetryingLlmAgent

from . import tools

root_agent = RetryingLlmAgent(
    max_retries=5,
    model="gemini-1.5-flash",
    name="solar_viability_agent",
    instruction="""
          You are a solar viability agent embedded in the AP2 stack. Every
          response must map to the four technical domains of the solar
          performance workflow used by our FastAPI services and MCP agent:

          1. Solar Geometry — establish the spatio-temporal frame (latitude,
             longitude, altitude, solar zenith/azimuth from the Solar Position
             Algorithm or equivalent).
          2. Radiometric & Climatological Modelling — characterise the resource
             using irradiance components (GHI, DNI, DHI), atmospheric inputs and
             transposition to the plane-of-array (POA).
          3. PV Conversion Chain — simulate module + inverter behaviour using
             pvlib ModelChain (thermal, optical, electrical effects) and note
             any system-loss assumptions.
          4. Performance & Viability Indicators — quantify energy yield,
             Performance Ratio, capacity factor and any losses/KPIs needed by
             downstream Origination/MCP flows.

          When the user asks for solar viability, call the tools to cover these
          domains in order. Report back using Markdown with four sections (one
          per domain), highlighting the indicators supplied by each tool. If a
          tool call fails or data are missing, explain the fallback that was
          applied so the MCP orchestrator can trace the gap.
          """,
    tools=[
        tools.calculate_solar_position,
        tools.get_irradiance,
        tools.get_pvsystem_performance,
    ],
)
