from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class ProvEntity(BaseModel):
    id: str = Field(..., description="Qualified PROV identifier e.g. entity:commit:sha123")
    prov_type: Literal["prov:Entity", "prov:Document", "prov:CodeDiff", "prov:ExtractedClaim"] = "prov:Entity"
    label: str
    value: Optional[str] = None
    created_at: str

class ProvActivity(BaseModel):
    id: str = Field(..., description="Qualified PROV activity identifier e.g. activity:llm_extraction:run_1")
    prov_type: Literal["prov:Activity"] = "prov:Activity"
    activity_type: str = Field(..., description="Type of operation e.g. Extraction, Verification, BlameScan")
    started_at: str
    ended_at: Optional[str] = None

class ProvAgent(BaseModel):
    id: str = Field(..., description="Qualified PROV agent identifier e.g. agent:dhruv_patil")
    prov_type: Literal["prov:Agent", "prov:Person", "prov:SoftwareAgent"] = "prov:Agent"
    name: str
    role: str

class ProvRelation(BaseModel):
    subject: str = Field(..., description="Source entity/activity ID")
    predicate: Literal[
        "prov:wasGeneratedBy",
        "prov:wasDerivedFrom",
        "prov:wasAttributedTo",
        "prov:used",
        "prov:wasAssociatedWith"
    ]
    object: str = Field(..., description="Target entity/activity/agent ID")
    timestamp: str

class ProvBundle(BaseModel):
    bundle_id: str
    target_project: str
    entities: List[ProvEntity] = Field(default_factory=list)
    activities: List[ProvActivity] = Field(default_factory=list)
    agents: List[ProvAgent] = Field(default_factory=list)
    relations: List[ProvRelation] = Field(default_factory=list)
