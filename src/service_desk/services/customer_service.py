from service_desk.domain.enums import CustomerPlan, CustomerStatus
from service_desk.domain.exceptions import CustomerAlreadyExists, CustomerNotFound
from service_desk.domain.models import Customer
from service_desk.repositories.interfaces import CustomerRepository


class CustomerService:
    def __init__(self, repository: CustomerRepository):
        self._repository = repository

    def create_customer(
        self, *, customer_id: str, name: str, plan: CustomerPlan, products: list[str]
    ) -> Customer:

        if self._repository.get_by_id(customer_id) is not None:
            raise CustomerAlreadyExists(customer_id)

        customer = Customer(
            id=customer_id,
            name=name,
            plan=plan,
            products=list(products),
            status=CustomerStatus.ACTIVE,
        )

        self._repository.add(customer=customer)

        return customer

    def get_customer(self, customer_id: str) -> Customer:
        customer = self._repository.get_by_id(customer_id=customer_id)
        if customer is None:
            raise CustomerNotFound(customer_id=customer_id)

        return customer
