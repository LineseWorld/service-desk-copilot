class BusinessError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class CustomerNotFound(BusinessError):
    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        super().__init__(f"Customer with id {customer_id} not found")

    def __str__(self):
        return f"CustomerNotFound(customer_id={self.customer_id})"


class CustomerAlreadyExists(BusinessError):
    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        super().__init__(f"Customer with id {customer_id} already exists")

    def __str__(self):
        return f"CustomerAlreadyExists(customer_id={self.customer_id})"


class TicketNotFound(BusinessError):
    def __init__(self, ticket_id: str):
        self.ticket_id = ticket_id
        super().__init__(f"Ticket with id {ticket_id} not found")

    def __str__(self):
        return f"TicketNotFound(ticket_id={self.ticket_id})"


class TicketAlreadyExists(BusinessError):
    def __init__(self, ticket_id: str):
        self.ticket_id = ticket_id
        super().__init__(f"Ticket with id {ticket_id} already exists")

    def __str__(self):
        return f"TicketAlreadyExists(ticket_id={self.ticket_id})"


class CustomerInactive(BusinessError):
    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        super().__init__(f"Customer with id {customer_id} inactive")

    def __str__(self):
        return f"CustomerInactive(customer_id={self.customer_id})"
