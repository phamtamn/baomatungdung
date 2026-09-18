# -*- coding: utf-8 -*-
"""Kiem thu khoi cho MiniShop.

Xac nhan may chu khoi dong duoc, sau trang chinh deu tra ma 200, va
du lieu mau da duoc nap. Chay bang: python -m unittest discover tests
"""

import os
import sys
import tempfile
import threading
import time
import unittest
from http.server import ThreadingHTTPServer
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# Cho phep import cac module cua ung dung tu thu muc cha.
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

# Dung mot tep co so du lieu tam rieng cho kiem thu.
_TMP_DB = os.path.join(tempfile.gettempdir(), "minishop_test.db")
if os.path.exists(_TMP_DB):
    os.remove(_TMP_DB)
os.environ["MINISHOP_DB"] = _TMP_DB

import app  # noqa: E402
import db  # noqa: E402
import seed  # noqa: E402


def _get(path, cookie=None, data=None):
    """Goi mot duong dan, tra ve (ma trang thai, than phan hoi, cookie)."""
    url = "http://127.0.0.1:8000" + path
    headers = {}
    if cookie:
        headers["Cookie"] = cookie
    body = None
    if data is not None:
        body = urlencode(data).encode("utf-8")
    req = Request(url, data=body, headers=headers)
    try:
        resp = urlopen(req)
        return resp.status, resp.read().decode("utf-8"), resp.headers.get("Set-Cookie")
    except HTTPError as exc:
        return exc.code, exc.read().decode("utf-8"), None


class SmokeTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.DB_PATH = _TMP_DB
        conn = db.connect()
        seed.ensure_db(conn)
        conn.close()
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 8000), app.Handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever)
        cls.thread.daemon = True
        cls.thread.start()
        time.sleep(0.3)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def _login(self):
        """Dang nhap tai khoan mau, tra ve chuoi cookie."""
        url = "http://127.0.0.1:8000/login"
        body = urlencode({"username": "lan", "password": "matkhau1"}).encode("utf-8")
        req = Request(url, data=body)
        # Khong theo chuyen huong de doc cookie tu phan hoi 302.
        opener = _NoRedirect()
        resp = opener.open(req)
        set_cookie = resp.headers.get("Set-Cookie")
        return set_cookie.split(";")[0]

    def test_login_page(self):
        status, body, _ = _get("/login")
        self.assertEqual(status, 200)
        self.assertIn("Dang nhap", body)

    def test_products_page(self):
        status, body, _ = _get("/sanpham")
        self.assertEqual(status, 200)
        # Du lieu mau da nap: mot san pham tieng Viet co dau xuat hien.
        self.assertIn("Áo thun cổ tròn", body)

    def test_search_page(self):
        status, body, _ = _get("/tim?q=" + "Non")
        self.assertEqual(status, 200)
        self.assertIn("Ket qua cho tu khoa", body)

    def test_profile_page(self):
        cookie = self._login()
        status, body, _ = _get("/hoso", cookie=cookie)
        self.assertEqual(status, 200)
        self.assertIn("Nguyễn Thị Lan", body)

    def test_orders_page(self):
        cookie = self._login()
        status, body, _ = _get("/donhang", cookie=cookie)
        self.assertEqual(status, 200)
        self.assertIn("Don hang cua toi", body)

    def test_admin_page(self):
        cookie = self._login()
        status, body, _ = _get("/admin", cookie=cookie)
        self.assertEqual(status, 200)
        self.assertIn("Quan tri nguoi dung", body)

    def test_seed_counts(self):
        conn = db.connect()
        users = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
        products = conn.execute("SELECT COUNT(*) AS n FROM products").fetchone()["n"]
        orders = conn.execute("SELECT COUNT(*) AS n FROM orders").fetchone()["n"]
        conn.close()
        self.assertEqual(users, 3)
        self.assertEqual(products, 12)
        self.assertEqual(orders, 6)


class _NoRedirect:
    """Mo URL nhung khong tu dong theo chuyen huong, de doc phan hoi 302."""

    def open(self, req):
        import urllib.request

        class _H(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args):
                return None

        opener = urllib.request.build_opener(_H)
        try:
            return opener.open(req)
        except HTTPError as exc:
            return exc


if __name__ == "__main__":
    unittest.main()
