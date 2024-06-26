class Package:
    def __init__(self, package_id, address, city, state, zip_code, deadline, weight, status, notes=""):
        self.package_id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.status = status
        self.notes = notes
        self.delivery_time = None
        self.departure_time = None
        self.truck = None

    def update_status(self, status, delivery_time=None):
        self.status = status
        self.delivery_time = delivery_time

    def __str__(self):
        return (f"Package {self.package_id} to {self.address}, {self.city}, {self.state}, {self.zip_code}, "
                f"deadline: {self.deadline}, weight: {self.weight}kg, status: {self.status}, "
                f"notes: {self.notes}, delivery time: {self.delivery_time}, truck: {self.truck}")
