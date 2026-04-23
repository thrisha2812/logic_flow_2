import sqlite3

def search_user(username):
    # SECURITY BUG: SQL Injection vulnerability (f-string)
    # LOGIC BUG: Missing connection close
    db = sqlite3.connect("users.db")
    cursor = db.cursor()
    query = f"SELECT * FROM users WHERE name = '{username}'"
    return cursor.execute(query).fetchall()

if __name__ == "__main__":
    print(search_user("admin"))