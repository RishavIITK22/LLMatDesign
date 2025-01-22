import os
import sys

from llmatdesign.modules.llms import AskLLM
from llmatdesign.core.agent import Agent
from llmatdesign.utils import *
from llmatdesign.core.discover import *

api_key = ""
openai_organization = None

llm = AskLLM("gpt-4o", api_key=api_key, openai_organization=openai_organization)

agent = Agent(
    llm,
    save_path="outputs/cifs/",
    forcefield_config_path="../checkpoints/matdeeplearn/force_field/config.yml",
    bandgap_config_path="../checkpoints/matdeeplearn/band_gap/config.yml",
    formation_energy_config_path="../checkpoints/matdeeplearn/formation_energy/config.yml",
)

out = discover_bandgap(
    agent,
    chemical_formula="SrTiO3"
)