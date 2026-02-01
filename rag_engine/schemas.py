from typing import Literal, Optional, Tuple
from pydantic import BaseModel, Field

class ProfandLabSearch(BaseModel):
    """Search over a database of professors and labs information."""

    query: str = Field(..., description="The optimized search query for semantic similarity search. Focus on research topics or technical terms.")

    source_type: Optional[Literal["professor", "lab"]] = Field(
        None, 
        description="Filter results by source type. Use 'professor' for faculty and 'lab' for groups. Leave None for general queries."
    )
    professor_name: Optional[str] = Field(None, description="The specific name of a professor.")
    position: Optional[str] = Field(None, description="The academic position (e.g., Assistant Professor, Associate Professor).")

    lab_name: Optional[str] = Field(None, description="The formal name of the research laboratory.")
    lab_leader: Optional[str] = Field(None, description="The name of the faculty member heading the lab.")

    department: Optional[str] = Field(None, description="The department name (e.g., Computer Science, Electrical Engineering).")
    research_area: Optional[str] = Field(None, description="Broad research category (e.g., AI, Robotics, HCI).")

    def pretty_print(self) -> None:
        data = self.dict()
        for field, value in data.items():
            if value is not None and value != "":
                print(f"{field}: {value}")