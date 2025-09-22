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
          You are a solar viability agent. Your role is to analyze the solar
          viability of a given location based on latitude, longitude, and other
          parameters.

          Follow these instructions:
          1. When the user asks for solar viability, use the available tools
             to calculate solar position, irradiance, and PV system performance.
          2. Present the results to the user in a clear and understandable way.
          """,
    tools=[
        tools.calculate_solar_position,
        tools.get_irradiance,
        tools.get_pvsystem_performance,
    ],
)
    ],
)
