def get_users():
    # Logic to get users from database or service
    return {"users": ["John", "Jane", "Doe"]}

def get_user(user_id):
    # Logic to get a single user by id
    return {"user": {"id": user_id, "name": "John"}}