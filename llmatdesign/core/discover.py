import os
import ase
import ast
import math
from llmatdesign.prompts.gpt import *
from llmatdesign.prompts.utils import *

def discover_bandgap(
    agent,
    chemical_formula: str,
    structure: ase.Atoms = None,
    band_gap: float = None,
    target_value: float = None,
    max_iterations: int = 55
):
    # query materials project
    if structure is None:
        _, structure = agent.query_materials_project(chemical_formula, 'structure')
    if band_gap is None:
        _, band_gap = agent.query_materials_project(chemical_formula, 'band_gap')
    
    # ask the expert for suggestions
    suggestions_list = [None]
    structures_list = [structure]
    band_gaps_list = [band_gap]
    band_gap_uncertainty_list = [0.0]
    reflections_list = [None]

    for i in range(max_iterations):
        # get prompt
        prompt = format_prompt(
            base_template_bandgap,
            suggestions_list, 
            structures_list, 
            band_gaps_list,
            reflections_list,
            property_type='band_gap', 
            target_property=target_value
        )

        print(prompt)

        # get modification
        modification_str = get_action(agent.llm, prompt)
        modification = ast.literal_eval(modification_str)

        new_structure, new_band_gap, band_gap_uncertainty, real_structure = agent.perform_modification(
            structures_list[-1], 
            modification["Modification"], 
            calculation_type='band_gap'
        )
        print(new_band_gap)
        print(band_gap_uncertainty)

        threshold=0.1*new_band_gap
        reflection=None
        reflection_prompt_template=None
        if real_structure is not None:
        
    
        # get post action reflection
            reflection_prompt_template = get_reflection_prompt_A(
                structures_list[-1].get_chemical_formula('metal'),
                new_structure.get_chemical_formula('metal'),
                modification_str,
                target_value,
                band_gaps_list[-1],
                new_band_gap
            )
        #     reflection_prompt = format_prompt(
        #     base_template_bandgap,
        #     suggestions_list, 
        #     structures_list, 
        #     band_gaps_list,
        #     reflections_list,
        #     property_type='band_gap', 
        #     target_property=target_value
        # )
        #     print(reflection_prompt)
            reflection = get_reflection(agent.llm, reflection_prompt_template)
        else:
            if not math.isnan(band_gap_uncertainty):
                if band_gap_uncertainty > threshold:
                    # get post action reflection
                    print("------------------------------------------ALERT-----------------------------------------")
                    print("THE PREDICTED BAND GAP OF THE MODIFIED STRUCTURE IS HIGHLY UNCERTAIN. NEED TO RECOMPUTE THE BAND GAP THROUGH DFT")
                    print("------------------------------------------------------------------------------------------")
                    reflection_prompt_template = get_reflection_prompt_B(
                    structures_list[-1].get_chemical_formula('metal'),
                    new_structure.get_chemical_formula('metal'),
                    modification_str,
                    target_value,
                    band_gaps_list[-1],
                    new_band_gap
                )
                    #reflection_prompt = format_prompt(
                    # base_template_bandgap,
                    # suggestions_list, 
                    # structures_list, 
                    # band_gaps_list,
                    # reflections_list,
                    # property_type='band_gap', 
                    # target_property=target_value
        # )
                    #print(reflection_prompt)
                    reflection = get_reflection(agent.llm, reflection_prompt_template)
                else:
                    reflection_prompt_template = get_reflection_prompt_B(
                    structures_list[-1].get_chemical_formula('metal'),
                    new_structure.get_chemical_formula('metal'),
                    modification_str,
                    target_value,
                    band_gaps_list[-1],
                    new_band_gap
                )
            #         reflection_prompt = format_prompt(
            #         base_template_bandgap,
            #         suggestions_list, 
            #         structures_list, 
            #         band_gaps_list,
            #         reflections_list,
            #         property_type='band_gap', 
            #         target_property=target_value
            # )
            #         print(reflection_prompt)
                    reflection = get_reflection(agent.llm, reflection_prompt_template)
            else:
                raise ValueError("Band gap uncertainty is not available for the modified structure.") 
            # self-reflection
            #reflection = get_reflection(agent.llm, reflection_prompt)
        

        suggestions_list.append(modification_str)
        structures_list.append(new_structure)
        band_gaps_list.append(new_band_gap)
        reflections_list.append(reflection)
        band_gap_uncertainty_list.append(band_gap_uncertainty)

        if agent.is_within_threshold(new_band_gap, target_value):
            return True, suggestions_list, structures_list, band_gaps_list, reflections_list
    
    return False, suggestions_list, structures_list, band_gaps_list, reflections_list
