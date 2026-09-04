from pydantic import BaseModel, Field

class CaseSummary(BaseModel):

    case_overview: str = Field(
        description="customer complaint case overview."
    )
    key_issue: str = Field(
        description="customer complaint key issue in one line."
    )
    action_taken: str = Field(
        description="action taken for customer complaint."
    )
    current_status: str = Field(
        description="current status of a complaint(resolved/under progess)."
    )
    recommended_next_action: str = Field(
        description="recommend suitable next action for case."
    )
