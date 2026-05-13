import sys
import os
import re

# Ensure the correct import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.inventory_mgr import InventoryManager
from services.user_mgr import UserManager
from utils.decorators import admin_required

class AppCLI:
    def __init__(self):
        self.inventory_mgr = InventoryManager("data/inventory.json")
        self.user_mgr = UserManager("data/users.json")
        self.current_user = None

    def run(self):
        print("=== Welcome to the Inventory Management System ===")
        self.login()
        if self.current_user:
            self.main_menu()

    def login(self):
        while not self.current_user:
            print("\nPlease log in to continue.")
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            
            if not re.match(r"^[a-zA-Z0-9]+$", username):
                print("Error: Username must contain only letters and numbers.")
                continue

            user = self.user_mgr.authenticate(username, password)
            if user:
                print(f"Login successful! Welcome {user.username} ({user.role}).")
                self.current_user = user
            else:
                print("Invalid username or password. Please try again.")

    def main_menu(self):
        while True:
            print("\n--- Main Menu ---")
            options = self.current_user.get_menu_options()

            
            for i, opt in enumerate(options, 1):
                print(f"{i}. {opt}")

            choice = input("\nSelect an option: ")
            
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(options):
                    selected_action = options[choice_idx]
                    self.handle_action(selected_action)
                else:
                    print("Invalid option number.")
            except ValueError:
                print("Please enter a valid number.")

    def handle_action(self, action: str):
        if action == "View all products":
            self.view_all()
        elif action == "Search/Filter products":
            self.search_filter()
        elif action == "Add a product":
            self.add_product()
        elif action == "Remove a product":
            self.remove_product()
        elif action == "Update product stock":
            self.update_stock()
        elif action == "View low stock report":
            self.view_low_stock()

        elif action == "Logout":
            self.current_user = None
            print("Logged out successfully.")
            self.login()
        elif action == "Exit":
            print("Exiting system. Goodbye!")
            sys.exit(0)

    def view_all(self):
        products = self.inventory_mgr.get_all_products()
        if not products:
            print("Inventory is empty.")
        else:
            for p in products:
                print(p)

    def search_filter(self):
        print("1. Search by name")
        print("2. Filter by price range")
        choice = input("Select an option: ")
        
        if choice == "1":
            q = input("Enter search term: ")
            results = self.inventory_mgr.search_products(q)
            if results:
                for r in results: print(r)
            else:
                print("No matches found.")
        elif choice == "2":
            try:
                min_p = float(input("Enter minimum price: "))
                max_p = float(input("Enter maximum price: "))
                results = self.inventory_mgr.filter_by_price_range(min_p, max_p)
                if results:
                    for r in results: print(r)
                else:
                    print("No products in that range.")
            except ValueError:
                print("Invalid price format.")
    def export_to_csv(self):
       
        products = self.inventory_mgr.get_all_products()
        if not products:
            print("Cannot export. Inventory is empty.")
            return

        file_path = "data/inventory_report.csv"
        headers = ["Product ID", "Name", "Price", "Quantity", "Category"]
        try:
         
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers) 

                for p in products:
                    
                    category = getattr(p, 'category', 'General')
                    writer.writerow([p.id, p.name, p.price, p.quantity, category])

            print(f"Success! Report generated dynamically and saved to '{file_path}'.")
        except IOError as e:
            print(f"File writing error: {e}")

   
    @admin_required
    def add_product(self):
        try:
            pid = int(input("Enter Product ID (integer): "))
            name = input("Enter Product Name: ")
            price = float(input("Enter Price: "))
            qty = int(input("Enter Quantity: "))
            
            if price < 0 or qty < 0:
                print("Error: Price and Quantity cannot be negative.")
                return

            if self.inventory_mgr.add_product(pid, name, price, qty):
                print("Product added successfully.")
            else:
                print("Error: Product ID already exists.")
        except ValueError:
            print("Invalid input format.")

    @admin_required
    def remove_product(self):
        try:
            pid = int(input("Enter Product ID to remove: "))
            if self.inventory_mgr.remove_product(pid):
                print("Product removed.")
            else:
                print("Product not found.")
        except ValueError:
            print("Invalid ID format.")

    @admin_required
    def update_stock(self):
        try:
            pid = int(input("Enter Product ID: "))
            amount = int(input("Enter amount to add/subtract (e.g. -5 or 10): "))
            success, msg = self.inventory_mgr.update_stock(pid, amount)
            if success:
                print(msg)
            else:
                print(f"Error: {msg}")
        except ValueError:
            print("Invalid input format.")

    @admin_required
    def view_low_stock(self):
        try:
            threshold = int(input("Enter low stock threshold: "))
            generator = self.inventory_mgr.get_low_stock_items(threshold)
            count = 0
            for item in generator:
                print(item)
                count += 1
            if count == 0:
                print("No items below that stock level.")
        except ValueError:
            print("Invalid input format.")

if __name__ == "__main__":
    app = AppCLI()
    app.run()
