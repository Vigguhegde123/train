from flask import Flask, request, jsonify
import heapq

app = Flask(__name__)

class Passenger:
    def __init__(self, name, pid, age, priority=0):
        self.name = name
        self.id = pid
        self.age = age
        self.priority = priority

    def __str__(self):
        return f"{self.name} (ID: {self.id}, Age: {self.age})"

    def to_dict(self):
        return {"name": self.name, "id": self.id, "age": self.age, "priority": self.priority}

class TrainReservationSystem:
    def __init__(self, max_seats=3):
        self.max_seats = max_seats
        self.confirmed = []
        self.waiting_list = []
        self.counter = 0

    def reserve(self, passenger):
        if len(self.confirmed) < self.max_seats:
            self.confirmed.append(passenger)
            return {"status": "confirmed", "passenger": passenger.to_dict()}
        else:
            heapq.heappush(self.waiting_list, (-passenger.priority, self.counter, passenger))
            self.counter += 1
            return {"status": "waiting", "passenger": passenger.to_dict()}

    def cancel(self, pid):
        for i, passenger in enumerate(self.confirmed):
            if passenger.id == pid:
                self.confirmed.pop(i)
                moved = None
                if self.waiting_list:
                    _, _, next_passenger = heapq.heappop(self.waiting_list)
                    self.confirmed.append(next_passenger)
                    moved = next_passenger.to_dict()
                return {"status": "cancelled", "moved_from_waiting": moved}
        return {"status": "not_found"}

    def status(self):
        return {
            "confirmed": [p.to_dict() for p in self.confirmed],
            "waiting_list": [p.to_dict() for _, _, p in self.waiting_list]
        }

system = TrainReservationSystem()

@app.route("/")
def home():
    return "Train Reservation System is Running"

@app.route("/reserve", methods=["POST"])
def reserve():
    data = request.get_json()
    name = data.get("name")
    pid = data.get("id")
    age = data.get("age")
    priority = data.get("priority", 0)
    passenger = Passenger(name, pid, age, priority)
    result = system.reserve(passenger)
    return jsonify(result)

@app.route("/cancel", methods=["POST"])
def cancel():
    data = request.get_json()
    pid = data.get("id")
    result = system.cancel(pid)
    return jsonify(result)

@app.route("/status", methods=["GET"])
def status():
    return jsonify(system.status())

if __name__ == "__main__":
    app.run(debug=True)
