from locust import HttpUser, task, constant


class User(HttpUser):
    wait_time = constant(0.5)

    @task
    def check_index(self):
        self.client.get("/")

    @task
    def see_their_account(self):
        self.client.post("/showSummary", data={"email": "john@simplylift.co"})

    @task
    def see_all_points(self):
        self.client.get("/showpoints")

    @task
    def book(self):
        self.client.get("/book/Spring Festival/Simply Lift")

    @task
    def book_place(self):
        with self.client.post("/purchasePlaces", data={"competition": "Spring Festival",
                                                         "club": "Simply Lift",
                                                         "places": 1
                                                         }, catch_response=True) as response:
            if response.status_code == 500:
                # The purchasePlaces will send errors with the code 500 if the purchase doesn't take place. It is
                # however a sign that the route works.
                response.success()

    @task
    def logout(self):
        self.client.get("/logout")
