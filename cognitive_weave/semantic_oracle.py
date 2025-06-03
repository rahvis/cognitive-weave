# cognitive_weave_poc/cognitive_weave/semantic_oracle.py

import json
from typing import List, Dict, Optional

from openai import AzureOpenAI

from .utils import get_azure_openai_client, AZURE_OAI_DEPLOYMENT_GPT4, log_info, log_error
from .data_structures import InsightParticle, InsightAggregateAttributes

class SemanticOracleInterface:
    """
    The Semantic Oracle Interface (SOI) uses an LLM (Azure OpenAI GPT-4)
    for deep semantic understanding, enrichment of information (IPs),
    and synthesis of higher-level insights (IAs).
    """
    def __init__(self):
        self.client: AzureOpenAI = get_azure_openai_client()
        self.model_deployment: str = AZURE_OAI_DEPLOYMENT_GPT4 # Using GPT-4 as requested

    def enrich_text_to_ip_attributes(self, raw_text: str) -> Optional[Dict]:
        """
        Processes raw text to generate structured attributes for an Insight Particle (IP).
        These attributes include resonance keys, signifiers, and a situational imprint.

        Args:
            raw_text: The raw text input to be processed.

        Returns:
            A dictionary containing the structured attributes for the IP,
            or None if an error occurs.
        """
        log_info(f"SOI: Enriching text to IP attributes. Input text length: {len(raw_text)} chars.")
        
        prompt = f"""
You are an advanced text analysis agent. Your task is to analyze the provided text and generate a structured JSON object.
This JSON object will form the core semantic attributes of an Insight Particle (IP).

The JSON object MUST contain the following keys:
- "resonance_keys": A list of 5-7 specific, core terms or short phrases that are crucial for identifying and searching this information. These should capture key entities, actions, concepts, and outcomes. Order them by perceived importance.
- "signifiers": A list of 3-5 broader categorical or thematic labels for classification (e.g., "project management", "technical issue", "user feedback", "strategic decision").
- "situational_imprint": A concise, single-sentence summary that captures the core context (what the text is about) and the most critical essence, key takeaway, or outcome from the text.
- "extracted_entities": An optional list of key named entities (people, organizations, locations, products, projects) mentioned in the text. If none are prominent, provide an empty list.

Text for Analysis:
---
{raw_text}
---

Strictly output ONLY the JSON object. Do not include any explanatory text before or after the JSON.
Ensure the JSON is well-formed.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_deployment,
                response_format={"type": "json_object"}, # Request JSON output
                messages=[
                    {"role": "system", "content": "You are an AI assistant specialized in extracting structured information from text and outputting it in valid JSON format, adhering strictly to the specified schema."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Lower temperature for more deterministic and factual output
                max_tokens=1000     # Adjust as needed based on expected output size
            )
            
            enriched_attributes_json_str = response.choices[0].message.content
            log_info("SOI: Successfully received IP attributes from LLM.")
            
            # Validate and parse the JSON
            try:
                enriched_attributes = json.loads(enriched_attributes_json_str)
                # Basic validation of expected keys
                expected_keys = {"resonance_keys", "signifiers", "situational_imprint", "extracted_entities"}
                if not expected_keys.issubset(enriched_attributes.keys()):
                    log_error(f"SOI: LLM output missing some expected keys. Got: {enriched_attributes.keys()}")
                    return None
                return enriched_attributes
            except json.JSONDecodeError as e:
                log_error(f"SOI: Error parsing JSON response from LLM for IP enrichment: {e}")
                log_error(f"Raw LLM response: {enriched_attributes_json_str}")
                return None

        except Exception as e:
            log_error(f"SOI: An error occurred during API call for IP enrichment: {e}")
            return None

    def synthesize_ia_from_imprints(self, ip_imprints: List[str]) -> Optional[InsightAggregateAttributes]:
        """
        Synthesizes a new Insight Aggregate (IA) from a list of situational imprints
        of related Insight Particles.

        Args:
            ip_imprints: A list of strings, where each string is the situational_imprint
                         of a related IP.

        Returns:
            An InsightAggregateAttributes object containing the synthesized IA's core data
            and its own attributes, or None if an error occurs.
        """
        if not ip_imprints:
            log_error("SOI: No IP imprints provided for IA synthesis.")
            return None

        log_info(f"SOI: Synthesizing IA from {len(ip_imprints)} IP imprints.")
        
        formatted_imprints = "\n".join([f"- Imprint {idx+1}: \"{imprint}\"" for idx, imprint in enumerate(ip_imprints)])

        prompt = f"""
You are an advanced AI knowledge synthesizer. You are tasked with creating a new, higher-level Insight Aggregate (IA) 
from a collection of related situational imprints, each derived from a distinct Insight Particle (IP).

Your goal is to:
1. Identify the core, overarching theme, pattern, problem, or emergent conclusion that connects these imprints.
2. Synthesize a new "ia_core_data" statement. This statement should be a concise, abstracted insight that is not explicitly stated in any single input but becomes evident from their combination. It should represent new, synthesized knowledge.
3. Generate attributes specifically for this new IA.

Input Information (Related IP Imprints):
---
{formatted_imprints}
---

Based on the collective information from these imprints, generate a single, valid JSON object with the following keys:
- "ia_core_data": (String) The synthesized higher-level conclusion, summary, or identified pattern. This is the core knowledge of the new IA.
- "ia_resonance_keys": (List of strings) 3-5 core terms or short phrases that are crucial for identifying this specific synthesized IA.
- "ia_signifiers": (List of strings) 2-3 broad categorical labels for this IA (e.g., "strategic insight", "emergent trend", "risk assessment", "solution proposal").
- "ia_situational_imprint": (String) A concise, single-sentence summary describing what this new Insight Aggregate itself represents or signifies.

Strictly output ONLY the JSON object. Do not include any explanatory text before or after the JSON.
Ensure the JSON is well-formed.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_deployment,
                response_format={"type": "json_object"}, # Request JSON output
                messages=[
                    {"role": "system", "content": "You are an AI assistant specialized in synthesizing higher-level insights from related information snippets and outputting the result as a valid JSON object, adhering strictly to the specified schema."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,  # Slightly higher temperature for more abstractive/creative synthesis
                max_tokens=1500     # Adjust as needed
            )
            
            synthesized_ia_json_str = response.choices[0].message.content
            log_info("SOI: Successfully received IA attributes from LLM.")
            
            try:
                ia_data_dict = json.loads(synthesized_ia_json_str)
                # Validate using Pydantic model
                ia_attributes = InsightAggregateAttributes(**ia_data_dict)
                return ia_attributes
            except json.JSONDecodeError as e:
                log_error(f"SOI: Error parsing JSON response from LLM for IA synthesis: {e}")
                log_error(f"Raw LLM response: {synthesized_ia_json_str}")
                return None
            except Exception as pydantic_error: # Catch Pydantic validation errors
                log_error(f"SOI: Error validating IA attributes against Pydantic model: {pydantic_error}")
                log_error(f"Raw LLM response: {synthesized_ia_json_str}")
                return None

        except Exception as e:
            log_error(f"SOI: An error occurred during API call for IA synthesis: {e}")
            return None

