import csv
import datetime
import sys
import os
from builtins import ValueError

from hash_table import HashTable
from package import Package
from truck import Truck

# Adding the current directory to the system path for module access
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Read distance data from CSV file
with open("csv/WGUPS_Distance_Table.csv", encoding='utf-8-sig') as distance_file:
    distances = csv.reader(distance_file)
    distances = list(distances)

# Read address data from CSV file
with open("csv/WGUPS_Address_File.csv", encoding='utf-8-sig') as address_file:
    addresses = csv.reader(address_file)
    addresses = list(addresses)

# Read package data from CSV file
with open("csv/WGUPS_Package_File.csv", encoding='utf-8-sig') as package_file:
    packages = csv.reader(package_file)
    packages = list(packages)


# Load package data into the hash table
def load_package_data(filename, package_table):
    with open(filename, encoding='utf-8-sig') as package_info:
        package_data = csv.reader(package_info)
        for package in package_data:
            if not package or not package[0].strip():  # Skip any empty lines
                continue
            try:
                # Extract package details
                package_id = int(package[0])
                address = package[1]
                city = package[2]
                state = package[3]
                zipcode = package[4]
                deadline = package[5]
                weight = package[6]
                status = "At Hub"
                notes = package[7]

                # Update status based on specific conditions
                if "Delayed on flight" in notes or "Wrong address listed" in notes:
                    status = "In Transit"

                # Create a Package object
                package_obj = Package(package_id, address, city, state, zipcode, deadline, weight, status, notes)

                # Insert the package into the hash table
                package_table.insert(package_id, package_obj)
            except ValueError:
                print(f"Skipping line due to ValueError: {package}")
                continue


# Calculate the distance between two locations based on their indices in the CSV file
def get_distance(start_index, end_index):
    distance = distances[start_index][end_index]
    if distance == '':
        distance = distances[end_index][start_index]
    return float(distance)


# Find the address index in the address list
def get_address_index(address):
    for row in addresses:
        if address in row[2]:
            return int(row[0])


# Create and configure Truck objects
truck1 = Truck(16, 18, None, [1, 13, 14, 15, 16, 19, 20, 29, 30, 31, 34, 37, 40], 0.0, "4001 South 700 East",
               datetime.timedelta(hours=8))
truck2 = Truck(16, 18, None, [3, 18, 21, 22, 23, 24, 26, 27, 35, 36, 38, 39], 0.0, "4001 South 700 East",
               datetime.timedelta(hours=8))
truck3 = Truck(16, 18, None, [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 17, 25, 28, 32, 33], 0.0, "4001 South 700 East",
               datetime.timedelta(hours=9, minutes=34, seconds=20))

# Initialize the package hash table
package_table = HashTable()

# Load packages into the hash table
load_package_data("csv/WGUPS_Package_File.csv", package_table)


# Use the nearest neighbor algorithm to sort packages for delivery and calculate total distance
def optimize_deliveries(truck):
    undelivered_packages = []
    for package_id in truck.packages:
        package = package_table.lookup(package_id)
        undelivered_packages.append(package)

    truck.packages.clear()

    while undelivered_packages:
        shortest_distance = float('inf')
        nearest_package = None
        for package in undelivered_packages:
            distance = get_distance(get_address_index(truck.address), get_address_index(package.address))
            if distance < shortest_distance:
                shortest_distance = distance
                nearest_package = package
        truck.packages.append(nearest_package.package_id)
        undelivered_packages.remove(nearest_package)
        truck.mileage += shortest_distance
        truck.address = nearest_package.address
        truck.time += datetime.timedelta(hours=shortest_distance / 18)
        nearest_package.delivery_time = truck.time
        nearest_package.departure_time = truck.depart_time
        nearest_package.status = "Delivered"


# Display delivery status for each truck
print(f"Truck 1 starts deliveries at {truck1.depart_time}")
optimize_deliveries(truck1)
print(f"Truck 1 completes deliveries at {truck1.time}")

print(f"Truck 2 starts deliveries at {truck2.depart_time}")
optimize_deliveries(truck2)
print(f"Truck 2 completes deliveries at {truck2.time}")

# Truck 3 starts after 09:32 and after truck 1 and 2 complete their routes
truck3_start_time = min(truck1.time, truck2.time)
truck3.depart_time = truck3_start_time
print(f"Truck 3 starts deliveries at {truck3.depart_time}")
optimize_deliveries(truck3)
print(f"Truck 3 completes deliveries at {truck3.time}")


# Update package status based on the current time
# Update package status based on the current time
def update_package_status(package, current_time):
    if package.package_id == 9 and current_time >= datetime.timedelta(hours=10, minutes=20):
        package.address = "410 S State St"
        package.city = "Salt Lake City"
        package.zip_code = "84111"
        package.notes = package.notes.replace("Wrong address listed", "Address corrected at 10:20 AM")
    elif package.package_id == 9 and current_time <= datetime.timedelta(hours=10, minutes=20):
        package.address = "300 State St"
        package.city = "Salt Lake City"
        package.zip_code = "84103"
        package.notes = package.notes.replace("Address corrected at 10:20 AM", "Wrong address listed")

    if "Delayed on flight" in package.notes:
        arrival_time = datetime.timedelta(hours=9, minutes=5)
        if current_time < arrival_time:
            package.status = "In Transit"
        elif current_time < truck3.depart_time:
            package.status = "At Hub"
        elif current_time < package.delivery_time:
            package.status = "En Route"
        else:
            package.status = "Delivered"
    elif "Wrong address listed" in package.notes:
        arrival_time = datetime.timedelta(hours=10, minutes=20)  # For package 9
        if current_time < arrival_time and current_time < truck3.depart_time:
            package.status = "At Hub"
        elif current_time < truck3.depart_time:
            package.status = "At Hub"
        elif current_time < package.delivery_time:
            package.status = "En Route"
        else:
            package.status = "Delivered"
    else:
        if package.package_id in truck1.packages:
            truck_depart_time = truck1.depart_time
        elif package.package_id in truck2.packages:
            truck_depart_time = truck2.depart_time
        elif package.package_id in truck3.packages:
            truck_depart_time = truck3.depart_time
        else:
            truck_depart_time = None

        if current_time < truck_depart_time:
            package.status = "At Hub"
        elif current_time < package.delivery_time:
            package.status = "En Route"
        else:
            package.status = "Delivered"


# Main class to handle user interaction
class Main:
    @staticmethod
    def run():

        # Display total mileage information
        print("Parcel Service")
        print("Total mileage for each truck:")
        print(f"Truck 1 mileage: {truck1.mileage:.2f} miles")
        print(f"Truck 2 mileage: {truck2.mileage:.2f} miles")
        print(f"Truck 3 mileage: {truck3.mileage:.2f} miles")
        print(f"Overall total mileage: {truck1.mileage + truck2.mileage + truck3.mileage:.2f} miles")
        print(r"""

  _     _             _ _                _                       _ _                           _                __  __                                                               _         
 | |__ (_)_ __  _ __ (_) |_ _   _       | |__   ___  _ __  _ __ (_) |_ _   _         __ _  ___| |_        ___  / _|/ _|       _ __ ___  _   _        _ __  _ __ ___  _ __   ___ _ __| |_ _   _ 
 | '_ \| | '_ \| '_ \| | __| | | |      | '_ \ / _ \| '_ \| '_ \| | __| | | |       / _` |/ _ \ __|      / _ \| |_| |_       | '_ ` _ \| | | |      | '_ \| '__/ _ \| '_ \ / _ \ '__| __| | | |
 | | | | | |_) | |_) | | |_| |_| |      | | | | (_) | |_) | |_) | | |_| |_| |      | (_| |  __/ |_      | (_) |  _|  _|      | | | | | | |_| |      | |_) | | | (_) | |_) |  __/ |  | |_| |_| |
 |_| |_|_| .__/| .__/|_|\__|\__, |      |_| |_|\___/| .__/| .__/|_|\__|\__, |       \__, |\___|\__|      \___/|_| |_|        |_| |_| |_|\__, |      | .__/|_|  \___/| .__/ \___|_|   \__|\__, |
         |_|   |_|          |___/                   |_|   |_|          |___/        |___/                                               |___/       |_|             |_|                  |___/ 

        """)

        while True:
            # Prompt user to start the process
            user_input = input("Enter 'time' to proceed, or any other key to exit: ").strip().lower()
            if user_input != "time":
                print("Invalid input. Exiting the program.")
                break

            try:
                # Prompt user to enter a specific time
                user_time = input("Enter a time (HH:MM:SS) to check the status of the packages: ")
                hours, minutes, seconds = map(int, user_time.split(":"))
                current_time = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

                # Ensure the entered time is valid
                if current_time < datetime.timedelta(hours=8):
                    print("Invalid time. Please enter a time after 08:00:00.")
                    continue

                # Prompt user to choose between viewing a single package or all packages
                view_option = input(
                    "Type 'solo' to view an individual package or 'all' to view all packages: ").strip().lower()
                if view_option == "solo":
                    try:
                        # Prompt user to enter a package ID
                        package_id = int(input("Enter the package ID: "))
                        package = package_table.lookup(package_id)
                        update_package_status(package, current_time)
                        if package_id in truck1.packages and package_table.lookup(package_id).status == "En Route":
                            package_table.lookup(package_id).truck = "Truck 1"
                        elif package_id in truck2.packages and package_table.lookup(package_id).status == "En Route":
                            package_table.lookup(package_id).truck = "Truck 2"
                        elif package_id in truck3.packages and package_table.lookup(package_id).status == "En Route":
                            package_table.lookup(package_id).truck = "Truck 3"
                        else:
                            package_table.lookup(package_id).truck = "None"
                        print(package)
                    except ValueError:
                        print("Invalid entry.")
                elif view_option == "all":
                    try:
                        # Update and display the status of all packages
                        for package_id in range(1, 41):
                            package = package_table.lookup(package_id)
                            update_package_status(package, current_time)
                            if package_id in truck1.packages and package_table.lookup(package_id).status == "En Route":
                                package_table.lookup(package_id).truck = "Truck 1"
                            elif package_id in truck2.packages and package_table.lookup(package_id).status == "En Route":
                                package_table.lookup(package_id).truck = "Truck 2"
                            elif package_id in truck3.packages and package_table.lookup(package_id).status == "En Route":
                                package_table.lookup(package_id).truck = "Truck 3"
                            else:
                                package_table.lookup(package_id).truck = "None"
                            print(package)
                    except ValueError:
                        print("Invalid entry.")
                else:
                    break
            except ValueError:
                print("Invalid entry.")
                break


if __name__ == "__main__":
    Main.run()
