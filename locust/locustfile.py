import random
from faker import Faker
from locust import HttpUser, task, tag, between

faker = Faker()
AVAILABLE_BOOKS = ["Book A", "Book B", "Book C", "Book D", "Book E"]

class User(HttpUser):
    wait_time = between(3, 5)

    def generate_valid_order(self):
        return {
            "user": {
                "name": faker.name(),
                "contact": faker.email(),
            },
            "creditCard": {
                "number": "4111111111111111", # Valid test credit card number
                "expirationDate": "12/25",
                "cvv": "123",
            },
            "userComment": "Load test order",
            "items": [],
            "billingAddress": {
                "street": faker.street_address(),
                "city": faker.city(),
                "state": faker.state_abbr(),
                "zip": faker.zipcode(),
                "country": "USA",
            },
            "shippingMethod": random.choice(["Standard", "Express", "Next-Day"]),
            "giftWrapping": random.choice([True, False]),
            "termsAccepted": True,
        }
    
    def generate_fraudulent_order(self):
        order = self.generate_valid_order()
        order["creditCard"]["number"] = "40000000000000021" # Invalid test credit card number
        return order
    
    @tag("non_fraudulent")
    @task
    def place_non_fraudulent_order(self):
        order_data = self.generate_valid_order()

        order_data["items"] = [{
            "name": random.choice(AVAILABLE_BOOKS),
            "quantity": 1
        }]

        with self.client.post("/checkout", json=order_data, catch_response=True, name="Non-Fraudulent Order") as response:
            if response.status_code != 200 or response.json()["status"] != "Order Approved":
                response.failure("Order failed")

    @tag("mixed")
    @task
    def place_mixed_order(self):
        order_data = self.generate_valid_order() if random.choice([True, False]) else self.generate_fraudulent_order()

        order_data["items"] = [{
            "name": random.choice(AVAILABLE_BOOKS) if random.random() > 0.7 else " ".join(faker.words(nb=3)),
            "quantity": 1
        } for _ in range(random.randint(1, 3))]

        with self.client.post("/checkout", json=order_data, catch_response=True, name="Mixed Order") as response:
            if response.status_code != 200 or response.json().get("status") != "Order Approved":
                response.failure("Order failed")

    @tag("conflicting")
    @task
    def place_conflicting_order(self):
        order_data = self.generate_valid_order()

        order_data["items"] = [{
            "name": book,
            "quantity": 1
        } for book in AVAILABLE_BOOKS]

        with self.client.post("/checkout", json=order_data, catch_response=True, name="Conflicting Order") as response:
            if response.status_code != 200 or response.json().get("status") != "Order Approved":
                response.failure("Order failed")
