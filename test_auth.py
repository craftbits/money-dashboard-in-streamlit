import hashlib
import json

def test_password():
    # Test the password hash
    password = "test1pw"
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    print(f"Password: {password}")
    print(f"Generated Hash: {password_hash}")
    
    # Load the users file
    with open("data/users.json", "r") as f:
        users = json.load(f)
    
    stored_hash = users["user1"]["password_hash"]
    print(f"Stored Hash: {stored_hash}")
    
    # Check if they match
    if password_hash == stored_hash:
        print("✅ Password hash matches! Authentication should work.")
    else:
        print("❌ Password hash mismatch! This is why login isn't working.")
        print(f"Difference: {password_hash != stored_hash}")

if __name__ == "__main__":
    test_password()
