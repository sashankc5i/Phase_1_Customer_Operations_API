from .models import Customer


class CustomerRepository:

    def __init__(self, size: int = 1_000_000):
        self.customers: dict[int, Customer] = {}

        for customer_id in range(1, size + 1):
            self.customers[customer_id] = Customer(
                id=customer_id,
                name=f"Customer {customer_id}",
                email=f"customer{customer_id}@example.com"
            )

        self.next_id = size + 1

    def get_by_id(self, customer_id: int) -> Customer | None:
        return self.customers.get(customer_id)

    def get_page(
        self,
        offset: int,
        limit: int
    ) -> list[Customer]:

        start_id = offset + 1
        end_id = min(
            start_id + limit,
            self.next_id
        )

        return [
            self.customers[customer_id]
            for customer_id in range(start_id, end_id)
            if customer_id in self.customers
        ]

    def count(self) -> int:
        return len(self.customers)

    def create(
        self,
        name: str,
        email: str
    ) -> Customer:

        customer = Customer(
            id=self.next_id,
            name=name,
            email=email
        )

        self.customers[self.next_id] = customer
        self.next_id += 1

        return customer

    def update(
        self,
        customer_id: int,
        name: str | None,
        email: str | None
    ) -> Customer | None:

        existing = self.customers.get(customer_id)

        if existing is None:
            return None

        updated = Customer(
            id=customer_id,
            name=name if name is not None else existing.name,
            email=email if email is not None else existing.email
        )

        self.customers[customer_id] = updated

        return updated

    def delete(self, customer_id: int) -> bool:

        if customer_id not in self.customers:
            return False

        del self.customers[customer_id]

        return True