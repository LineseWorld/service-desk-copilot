from pydantic import BaseModel, Field

from service_desk.domain.enums import CustomerPlan, CustomerStatus


class CustomerCreate(BaseModel):
    id: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    plan: CustomerPlan = Field(description="只允许FREE, STANDARD, ENTERPRISE")
    products: list[str]


class CustomerResponse(BaseModel):
    id: str
    name: str
    plan: CustomerPlan
    status: CustomerStatus
    products: list[str]
