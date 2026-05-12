from models.user import User, Admin, Customer
from utils.file_handler import load_json

class UserManager:
    def __init__(self, users_file: str):
        self.users_file = users_file
        self.users = {}
        self.load_users()

    def load_users(self):
        data = load_json(self.users_file)
        for item in data:
            username = item["username"]
            role = item["role"]
            password = item.get("password", "") # Optional basic auth simulation
            
            if role == "admin":
                user_obj = Admin(username)
            else:
                user_obj = Customer(username)
            
            # Store tuple of user object and their password
            self.users[username] = {"user": user_obj, "password": password}

    def authenticate(self, username: str, password: str) -> User | None:
        if username in self.users:
            if self.users[username]["password"] == password:
                return self.users[username]["user"]
        return None
