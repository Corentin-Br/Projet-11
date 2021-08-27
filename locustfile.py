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
    def book_place(self):
        self.client.post("/purchasePlaces", data={"competition": "Spring Festival",
                                                  "club": "Simply Lift",
                                                  "places": 1
                                                  })

    @task
    def logout(self):
        self.client.get("/logout")