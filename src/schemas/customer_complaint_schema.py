from pydantic import BaseModel, Field

class CustomerComplaint(BaseModel):
    """
    Structured output format for customer complaint.
    """

    customer_name: str = Field(
        description="Customer's Full Name."
    )

    customer_email: str = Field(
        description="Customer's email address."
    )

    customer_phone: str = Field(
            description="Customer's contact information."
        )
    
    complaint_category: str = Field(
        description="Complaint Category."
    )

    complaint_description: str = Field(
        description="Customer's Complaint description."
    )

    resolution_provided: str = Field(
        description="Resolution provided to the customer."
    )

    escalation_information:str = Field(
        description="Esclation information if available."
    )

    supporting_information:str = Field(
        description="supporting information provided by customer on complaint."
    )

    current_status: str = Field(
        description="Current status on complaint."
    )