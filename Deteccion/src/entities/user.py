class User:
    def __init__(self, username: str, email: str, password: str, created_at: str, updated_at: str):
        self.username = username
        self.email = email
        self.password = password
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(data: dict):
        return User(
            username=data.get("username", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )
