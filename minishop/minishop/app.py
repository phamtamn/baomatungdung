# -*- coding: utf-8 -*-
"""MiniShop: ung dung web day hoc cho hoc phan 04210 Bao mat phan mem.

Diem khoi dong. Module nay lo dinh tuyen va xu ly HTTP, con truy cap
co so du lieu nam trong db.py va sinh HTML nam trong views.py.

Ung dung nay CO Y chua lo hong de sinh vien tim va va. No chi duoc chay
cuc bo tren may ca nhan, khong bao gio dua ra mang cua truong.
"""

import hashlib
import http.cookies
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import db
import seed
import views

# May chu chi lang nghe tren dia chi noi bo. Ly do: ung dung nay co y chua
# lo hong, no khong duoc phep lo ra mang LAN cua phong may hay cua truong.
# Dat 0.0.0.0 se mo cong ra moi may trong mang, tuyet doi khong lam vay.
HOST = "127.0.0.1"
PORT = 8000

SESSION_KEY = "minishop-secret-key-2026"

# Kho phien luu trong bo nho tien trinh: ma phien tro toi ma nguoi dung.
SESSIONS = {}
_next_sid = 0


def _new_session_id():
    """Sinh mot ma phien moi."""
    global _next_sid
    _next_sid += 1
    return str(_next_sid)


def _sign(sid):
    """Ky ma phien de gan vao cookie."""
    return hashlib.md5((SESSION_KEY + sid).encode("utf-8")).hexdigest()


class Handler(BaseHTTPRequestHandler):
    """Bo xu ly moi yeu cau HTTP: doc duong dan roi goi trang tuong ung."""

    server_version = "MiniShop/1.0"

    def log_message(self, fmt, *args):
        """Ghi log gon mot dong, khong in ra chi tiet thua."""
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    # --- Tien ich phan hoi ---

    def _send(self, status, html_text):
        """Gui phan hoi HTML voi charset UTF-8 trong tieu de HTTP."""
        body = html_text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location):
        """Chuyen huong trinh duyet sang duong dan khac."""
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def _set_session_cookie(self, sid):
        """Dat cookie phien co chu ky."""
        cookie = http.cookies.SimpleCookie()
        cookie["session"] = sid + "." + _sign(sid)
        cookie["session"]["path"] = "/"
        self.send_header("Set-Cookie", cookie["session"].OutputString())

    def _current_user(self):
        """Lay nguoi dung dang dang nhap tu cookie, hoac None."""
        raw = self.headers.get("Cookie")
        if not raw:
            return None
        cookie = http.cookies.SimpleCookie(raw)
        if "session" not in cookie:
            return None
        value = cookie["session"].value
        if "." not in value:
            return None
        sid, sig = value.rsplit(".", 1)
        if _sign(sid) != sig:
            return None
        user_id = SESSIONS.get(sid)
        if user_id is None:
            return None
        return db.get_user(user_id)

    def _read_form(self):
        """Doc du lieu bieu mau tu than yeu cau POST."""
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8")
        return parse_qs(raw, keep_blank_values=True)

    # --- Dinh tuyen ---

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query, keep_blank_values=True)
        try:
            self._route_get(path, query)
        except Exception as exc:
            self._send(500, views.message_page("Loi", "Loi he thong: " + str(exc), None))

    def _route_get(self, path, query):
        user = self._current_user()
        if path == "/" or path == "/sanpham":
            self._send(200, views.products_page(db.list_products(), user))
        elif path == "/login":
            self._send(200, views.login_page(""))
        elif path == "/logout":
            self._do_logout()
        elif path == "/tim":
            keyword = query.get("q", [""])[0]
            self._send(200, views.search_page(keyword, db.search_products(keyword), user))
        elif path == "/hoso":
            if user is None:
                self._redirect("/login")
            else:
                self._send(200, views.profile_page(user))
        elif path == "/donhang":
            if user is None:
                self._redirect("/login")
            else:
                self._send(200, views.orders_page(db.list_orders_for_user(user["id"]), user))
        elif path.startswith("/don/"):
            self._show_order(path, user)
        elif path == "/admin":
            self._show_admin(user)
        else:
            self._send(404, views.message_page("Khong tim thay", "Trang khong ton tai.", user))

    def _show_order(self, path, user):
        """Chi tiet mot don hang."""
        if user is None:
            self._redirect("/login")
            return
        order_id = int(path[len("/don/"):])
        order = db.get_order(order_id)
        if order is None:
            self._send(404, views.message_page("Khong tim thay", "Don hang khong ton tai.", user))
        else:
            self._send(200, views.order_detail_page(order, user))

    def _show_admin(self, user):
        """Trang quan tri liet ke toan bo nguoi dung."""
        if user is None:
            self._redirect("/login")
            return
        self._send(200, views.admin_page(db.list_users(), user))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path == "/login":
                self._do_login()
            elif path == "/mua":
                self._do_buy()
            else:
                self._send(404, views.message_page("Khong tim thay", "Trang khong ton tai.", None))
        except Exception as exc:
            self._send(500, views.message_page("Loi", "Loi he thong: " + str(exc), None))

    def _do_login(self):
        """Xu ly dang nhap: xac thuc roi mo phien."""
        form = self._read_form()
        username = form.get("username", [""])[0]
        password = form.get("password", [""])[0]
        row = db.find_login(username, password)
        if row is None:
            self._send(200, views.login_page("Sai ten dang nhap hoac mat khau."))
            return
        sid = _new_session_id()
        SESSIONS[sid] = row["id"]
        self.send_response(302)
        self.send_header("Location", "/sanpham")
        self._set_session_cookie(sid)
        self.end_headers()

    def _do_logout(self):
        """Xu ly dang xuat: xoa phien."""
        raw = self.headers.get("Cookie")
        if raw:
            cookie = http.cookies.SimpleCookie(raw)
            if "session" in cookie and "." in cookie["session"].value:
                sid = cookie["session"].value.rsplit(".", 1)[0]
                SESSIONS.pop(sid, None)
        self._redirect("/login")

    def _do_buy(self):
        """Xu ly mua hang: tru ton kho."""
        user = self._current_user()
        if user is None:
            self._redirect("/login")
            return
        form = self._read_form()
        product_id = int(form.get("product_id", ["0"])[0])
        quantity = int(form.get("quantity", ["1"])[0])
        ok = db.buy_product(user["id"], product_id, quantity)
        if ok:
            self._send(200, views.message_page("Mua hang", "Dat hang thanh cong.", user))
        else:
            self._send(200, views.message_page("Mua hang", "Khong du hang trong kho.", user))


def _init_database():
    """Tao co so du lieu va nap du lieu mau trong lan chay dau."""
    conn = db.connect()
    try:
        seed.ensure_db(conn)
    finally:
        conn.close()


def main():
    """Diem khoi dong: nap co so du lieu roi chay may chu."""
    _init_database()
    try:
        httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError:
        # Cong da bi chiem: in huong dan doi cong thay vi do ra vet ngan xep.
        sys.stderr.write(
            "Cong " + str(PORT) + " dang bi chiem. Hay dong ung dung dang giu cong do, "
            "hoac sua bien PORT trong app.py sang mot so khac (vi du 8080) roi chay lai.\n"
        )
        sys.exit(1)
    # In dong xac nhan de sinh vien doi chieu, gom dia chi va cong.
    print("MiniShop dang chay tai http://" + HOST + ":" + str(PORT))
    print("CANH BAO: ung dung nay CO Y chua lo hong, chi chay cuc bo, khong dua ra mang.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDa dung may chu.")
        httpd.server_close()


if __name__ == "__main__":
    main()
