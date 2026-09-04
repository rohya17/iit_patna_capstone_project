from pydantic import BaseModel, Field

class EmailDetails(BaseModel):

    """
    Structured output for email
    """

    subject: str = Field(
        description = "Suitable Subject for Email."
    )

    body: str = Field(
        description = "Email body containing customer complaint information"
    )