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


class RouteQuery(BaseModel):
    """Route a user query to the most relevant prompt based on their intent."""
    
    target: Literal["academic_search", "general_research"] = Field(
        ...,
        description="""Choose the destination based on the user's intent:
        - 'academic_search': Select this if the query relates to Northwestern University (NU) specifically. 
          This includes searching for specific professors, identifying research labs, inquiring about 
          departmental faculty, or finding which groups at NU work on a particular technology.
        - 'general_research': Select this if the query is a general scientific or technical question 
          that does NOT require Northwestern-specific data. This includes explaining terminologies 
          (e.g., 'What is Cross-Entropy?'), helping with general research methodology, or 
          conceptual explanations that apply universally regardless of the institution.
        """
    )