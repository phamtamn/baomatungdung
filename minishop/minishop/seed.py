# -*- coding: utf-8 -*-
"""Tao luoc do co so du lieu va nap du lieu mau cho MiniShop.

Module nay chi lam mot viec: bao dam co so du lieu ton tai va co du lieu.
Ham ensure_db co tinh chat idempotent, goi bao nhieu lan cung an toan.
"""

from db import hash_password

# Luoc do gom ba bang: nguoi dung, san pham, don hang.
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_md5 TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL,
    email TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    stock INTEGER NOT NULL,
    description TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
"""

# Ba nguoi dung: mot quan tri vien va hai nguoi dung thuong.
# Cot thu hai la mat khau goc, chi dung khi nap du lieu mau.
USERS = [
    ("quantri", "admin123", "Trần Quản Trị", "admin", "quantri@minishop.vn"),
    ("lan", "matkhau1", "Nguyễn Thị Lan", "user", "lan@minishop.vn"),
    ("hung", "matkhau2", "Lê Văn Hùng", "user", "hung@minishop.vn"),
]

# Muoi hai san pham, ten tieng Viet co dau de kiem tra ma hoa ky tu.
PRODUCTS = [
    ("Áo thun cổ tròn", 120000, 25, "Áo thun cotton cổ tròn màu trắng"),
    ("Quần jean xanh", 320000, 15, "Quần jean nam ống đứng màu xanh"),
    ("Nón lá Huế", 85000, 40, "Nón lá truyền thống làm tại Huế"),
    ("Giày da nâu", 650000, 8, "Giày da thật màu nâu đi làm"),
    ("Túi xách vải", 190000, 12, "Túi xách vải canvas bền chắc"),
    ("Khăn lụa Hà Đông", 250000, 10, "Khăn lụa dệt tại làng Hà Đông"),
    ("Bình giữ nhiệt", 210000, 30, "Bình giữ nhiệt inox 500ml"),
    ("Sổ tay bìa da", 95000, 50, "Sổ tay bìa da 200 trang"),
    ("Bút máy Hồng Hà", 45000, 60, "Bút máy học sinh Hồng Hà"),
    ("Cà phê Buôn Ma Thuột", 160000, 20, "Cà phê rang xay nguyên chất"),
    ("Trà sen Tây Hồ", 180000, 18, "Trà sen ướp hương tự nhiên"),
    ("Bánh đậu xanh Hải Dương", 55000, 35, "Bánh đậu xanh đặc sản Hải Dương"),
]

# Sau don hang lien ket nguoi dung voi san pham: (user_id, product_id, quantity).
ORDERS = [
    (2, 1, 2),
    (2, 8, 1),
    (2, 11, 3),
    (3, 4, 1),
    (3, 7, 2),
    (3, 12, 5),
]


def ensure_db(conn):
    """Tao bang neu chua co va nap du lieu mau khi bang nguoi dung con rong."""
    conn.executescript(SCHEMA)
    row = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()
    if row["n"] > 0:
        return
    _seed(conn)
    conn.commit()


def _seed(conn):
    """Nap ba nguoi dung, muoi hai san pham va sau don hang mau."""
    for username, password, full_name, role, email in USERS:
        conn.execute(
            "INSERT INTO users (username, password_md5, full_name, role, email) "
            "VALUES (?, ?, ?, ?, ?)",
            (username, hash_password(password), full_name, role, email),
        )
    for name, price, stock, desc in PRODUCTS:
        conn.execute(
            "INSERT INTO products (name, price, stock, description) VALUES (?, ?, ?, ?)",
            (name, price, stock, desc),
        )
    for user_id, product_id, qty in ORDERS:
        price = conn.execute(
            "SELECT price FROM products WHERE id = ?", (product_id,)
        ).fetchone()["price"]
        conn.execute(
            "INSERT INTO orders (user_id, product_id, quantity, total, created_at) "
            "VALUES (?, ?, ?, ?, datetime('now'))",
            (user_id, product_id, qty, price * qty),
        )


# Cho phep chay truc tiep: python seed.py
# Tao lai co so du lieu tu dau, dung khi du lieu mau bi xoa hoac bi sua hong.
if __name__ == "__main__":
    import os
    import sqlite3
    import db as _db

    if os.path.exists(_db.DB_PATH):
        os.remove(_db.DB_PATH)
        print("Da xoa co so du lieu cu.")
    conn = sqlite3.connect(_db.DB_PATH)
    conn.row_factory = sqlite3.Row
    ensure_db(conn)
    conn.commit()
    conn.close()
    print("Da nap lai du lieu mau: 3 nguoi dung, 12 san pham, 6 don hang.")
    print("Chay lai 'python app.py' de mo ung dung.")
