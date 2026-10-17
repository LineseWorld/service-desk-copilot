from dataclasses import asdict

from pydantic import BaseModel, ConfigDict, Field

from service_desk.agent.tools.base import ToolResult
from service_desk.llm.models import ToolDefinition
from service_desk.services.customer_service import CustomerService


class GetCustomerArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(
        min_length=1,
        max_length=50,
        description="要查询的客户ID",
    )


class GetCustomerTool:
    def __init__(self, customer_service: CustomerService) -> None:
        self._customer_service = customer_service

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_customer",
            description=(
                "根据客户ID查询客户名称、套餐、产品权限和账户状态。"
                "回答具体客户信息之前必须调用此工具。"
            ),
            parameters=GetCustomerArguments.model_json_schema(),
        )

    def execute(self, arguments_json: str) -> ToolResult:
        arguments = GetCustomerArguments.model_validate_json(arguments_json)
        customer = self._customer_service.get_customer(arguments.customer_id)

        return ToolResult(
            success=True,
            data=asdict(customer),
        )
