# cognitive_weave_poc/cognitive_weave/data_structures.py

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class InsightParticle(BaseModel):
    """
    Represents the fundamental unit of knowledge in Cognitive Weave.
    """
    particle_id: str = Field(default_factory=lambda: f"IP_{uuid.uuid4()}")
    core_data: Any  # The original raw information content
    resonance_keys: List[str] = Field(default_factory=list)
    signifiers: List[str] = Field(default_factory=list)
    situational_imprint: Optional[str] = None
    extracted_entities: Optional[List[str]] = Field(default_factory=list) # Added from example
    
    # Timestamps
    creation_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    modification_timestamp: Optional[str] = None
    last_access_timestamp: Optional[str] = None
    
    # Relational Strands (simplified for PoC)
    # In a full system, these would be more complex objects or references
    relational_strands: List[Dict[str, str]] = Field(default_factory=list) 
                                                # e.g., [{"type": "supports", "target_id": "IP_xyz"}]

    # Dynamic metrics (simplified for PoC)
    access_frequency: int = 0
    importance_score: float = 0.0
    
    # For Insight Aggregates
    is_aggregate: bool = False
    derived_from_ids: List[str] = Field(default_factory=list) # IDs of IPs used to form this IA

    class Config:
        # Title for the schema in OpenAPI/JSON Schema
        title = "InsightParticle"


class InsightAggregateAttributes(BaseModel):
    """
    Specific attributes generated during the synthesis of an Insight Aggregate.
    """
    ia_core_data: str = Field(description="The synthesized higher-level conclusion or pattern.")
    ia_resonance_keys: List[str] = Field(description="Core terms for the synthesized IA.")
    ia_signifiers: List[str] = Field(description="Broad categories for the synthesized IA.")
    ia_situational_imprint: str = Field(description="Concise summary of what the new IA represents.")

    class Config:
        title = "InsightAggregateAttributes"

# Note: An Insight Aggregate (IA) is essentially an InsightParticle 
# where `is_aggregate` is True, and its `core_data` would be the `ia_core_data`,
# and its `resonance_keys`, `signifiers`, `situational_imprint` would be
# the `ia_resonance_keys`, `ia_signifiers`, `ia_situational_imprint` respectively.
# The `derived_from_ids` field would link it back to source IPs.
