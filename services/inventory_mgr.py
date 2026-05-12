from models.product import Product
from utils.file_handler import load_json, save_json

class InventoryManager:
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.inventory = {}
        self.load_data()

    def load_data(self):
        # load data from the json file
        data = load_json(self.data_file)
        self.inventory = {}
        for item in data:
            product = Product(item["id"], item["name"], item["price"], item["quantity"])
            self.inventory[product.id] = product

    def save_data(self):
        # save back to json
        data_to_save = [product.to_dict() for product in self.inventory.values()]
        save_json(self.data_file, data_to_save)

    def get_all_products(self) -> list:
        return list(self.inventory.values())

    def add_product(self, product_id: int, name: str, price: float, quantity: int) -> bool:
        if product_id in self.inventory:
            return False  # Product ID already exists
        new_product = Product(product_id, name, price, quantity)
        self.inventory[product_id] = new_product
        self.save_data()
        return True

    def remove_product(self, product_id: int) -> bool:
        if product_id in self.inventory:
            del self.inventory[product_id]
            self.save_data()
            return True
        return False

    def update_stock(self, product_id: int, amount: int) -> tuple[bool, str]:
        if product_id not in self.inventory:
            return False, "Product not found."
        try:
            self.inventory[product_id].update_quantity(amount)
            self.save_data()
            return True, "Stock updated successfully."
        except ValueError as e:
            return False, str(e)

    def search_products(self, query: str) -> list:
        # search by name
        query = query.lower()
        return list(filter(lambda p: query in p.name.lower(), self.inventory.values()))

    def filter_by_price_range(self, min_price: float, max_price: float) -> list:
        # filter price
        return list(filter(lambda p: min_price <= p.price <= max_price, self.inventory.values()))

    def get_low_stock_items(self, threshold: int = 10):
        # get items that have low stock
        for product in self.inventory.values():
            if product.quantity < threshold:
                yield product
