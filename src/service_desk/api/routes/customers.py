from fastapi import APIRouter, status

from service_desk.api.dependencies import CustomerServiceDep
from service_desk.schemas.customer import CustomerCreate, CustomerResponse

router = APIRouter(prefix="/api/v1/customers")


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: str,
    svc: CustomerServiceDep,
) -> CustomerResponse:
    customer = svc.get_customer(customer_id)

    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        plan=customer.plan,
        status=customer.status,
        products=customer.products,
    )


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    param: CustomerCreate,
    svc: CustomerServiceDep,
) -> CustomerResponse:
    customer = svc.create_customer(
        customer_id=param.id,
        name=param.name,
        plan=param.plan,
        products=param.products,
    )

    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        plan=customer.plan,
        status=customer.status,
        products=customer.products,
    )
