"""
Test Locust simple pour mesurer le temps de réponse des endpoints principaux
"""
from locust import HttpUser, task, between
import time

class SimpleTestUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def test_homepage(self):
        start = time.time()
        with self.client.get("/", catch_response=True) as response:
            elapsed = time.time() - start
            print(f"🏠 / : {elapsed:.3f}s")
            if elapsed > 2.0:
                response.failure(f"Trop lent: {elapsed:.3f}s > 2s")
            else:
                response.success()

    @task
    def test_public_points(self):
        start = time.time()
        with self.client.get("/public/points", catch_response=True) as response:
            elapsed = time.time() - start
            print(f"🏆 /public/points : {elapsed:.3f}s")
            if elapsed > 2.0:
                response.failure(f"Trop lent: {elapsed:.3f}s > 2s")
            else:
                response.success()

    @task
    def test_update_booking(self):
        """Test POST /purchasePlaces (mise à jour)"""
        payload = {
            "competition": "Spring Festival",  
            "club": "Simply Lift",            
            "places": 1
        }
        start = time.time()
        with self.client.post("/purchasePlaces", data=payload, catch_response=True) as response:
            elapsed = time.time() - start
            print(f"📝 /purchasePlaces : {elapsed:.3f}s")
            if elapsed > 2.0:
                response.failure(f"Mise à jour trop lente: {elapsed:.3f}s > 2s")
            else:
                response.success()

if __name__ == "__main__":
    import os
    os.system("locust -f simple_test.py --host http://127.0.0.1:5000 --users 6 --spawn-rate 1 --run-time 30s --headless")
