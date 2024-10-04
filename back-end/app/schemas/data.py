from pydantic import BaseModel

class SwimmingCategory(BaseModel):
    is_relay: bool
    total_distance: int
    stroke: str
