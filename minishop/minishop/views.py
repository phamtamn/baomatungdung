# -*- coding: utf-8 -*-
"""Sinh HTML cho MiniShop.

Cac ham o day nhan du lieu da lay tu co so du lieu va tra ve chuoi HTML.
Ten san pham va ten nguoi dung deu duoc thoat ky tu bang html.escape,
tru mot cho co chu dinh de tao lo hong.
"""

import html


def _money(value):
    """Dinh dang so tien theo kieu Viet Nam: 120000 thanh 120.000d."""
    return "{:,}".format(value).replace(",", ".") + "d"


def layout(title, body, user):
    """Khung trang chung: dat charset UTF-8 trong the meta cho hien thi tieng Viet."""
    if user is None:
        nav = '<a href="/login">Dang nhap</a>'
    else:
        nav = (
            '<a href="/sanpham">San pham</a> '
            '<a href="/hoso">Ho so</a> '
            '<a href="/donhang">Don hang cua toi</a> '
        )
        # Lien ket quan tri chi hien khi vai tro la admin.
        if user["role"] == "admin":
            nav += '<a href="/admin">Quan tri</a> '
        nav += (
            '<span class="who">Xin chao, '
            + html.escape(user["full_name"])
            + '</span> <a href="/logout">Dang xuat</a>'
        )
    return (
        "<!DOCTYPE html>\n"
        '<html lang="vi"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>" + html.escape(title) + " - MiniShop</title>"
        "<style>body{font-family:sans-serif;max-width:760px;margin:24px auto;"
        "padding:0 16px;line-height:1.5}nav{background:#f0f0f0;padding:10px;"
        "border-radius:6px;margin-bottom:20px}nav a{margin-right:8px}"
        "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;"
        "padding:6px 10px;text-align:left}.who{color:#555}.price{color:#c0392b}"
        "form.search{margin:16px 0}input[type=text]{padding:6px;width:60%}"
        "button{padding:6px 12px}</style></head><body>"
        "<nav>" + nav + "</nav>"
        "<h1>" + html.escape(title) + "</h1>"
        + body
        + "</body></html>"
    )


def login_page(error):
    """Trang dang nhap. Hien thong bao loi neu co."""
    note = ""
    if error:
        note = '<p style="color:#c0392b">' + html.escape(error) + "</p>"
    body = (
        note
        + '<form method="post" action="/login">'
        "<p>Ten dang nhap:<br><input type=text name=username></p>"
        "<p>Mat khau:<br><input type=password name=password></p>"
        "<button type=submit>Dang nhap</button></form>"
        "<p>Tai khoan mau: lan / matkhau1</p>"
    )
    return layout("Dang nhap", body, None)


def _product_rows(products):
    rows = ""
    for p in products:
        rows += (
            "<tr><td>" + str(p["id"]) + "</td>"
            "<td>" + html.escape(p["name"]) + "</td>"
            '<td class="price">' + _money(p["price"]) + "</td>"
            "<td>" + str(p["stock"]) + "</td></tr>"
        )
    return rows


def products_page(products, user):
    """Danh sach san pham kem o tim kiem."""
    body = (
        '<form class="search" method="get" action="/tim">'
        '<input type=text name=q placeholder="Tim san pham...">'
        "<button type=submit>Tim</button></form>"
        "<table><tr><th>Ma</th><th>Ten</th><th>Gia</th><th>Ton</th></tr>"
        + _product_rows(products)
        + "</table>"
    )
    return layout("San pham", body, user)


def search_page(keyword, products, user):
    """Trang ket qua tim kiem."""
    body = "<p>Ket qua cho tu khoa: <b>" + keyword + "</b></p>"
    body += (
        '<form class="search" method="get" action="/tim">'
        '<input type=text name=q value="">'
        "<button type=submit>Tim</button></form>"
        "<table><tr><th>Ma</th><th>Ten</th><th>Gia</th><th>Ton</th></tr>"
        + _product_rows(products)
        + "</table>"
    )
    return layout("Tim kiem", body, user)


def profile_page(user):
    """Trang ho so ca nhan."""
    body = (
        "<table>"
        "<tr><th>Ho ten</th><td>" + html.escape(user["full_name"]) + "</td></tr>"
        "<tr><th>Ten dang nhap</th><td>" + html.escape(user["username"]) + "</td></tr>"
        "<tr><th>Email</th><td>" + html.escape(user["email"]) + "</td></tr>"
        "<tr><th>Vai tro</th><td>" + html.escape(user["role"]) + "</td></tr>"
        "</table>"
    )
    return layout("Ho so ca nhan", body, user)


def orders_page(orders, user):
    """Danh sach don hang cua nguoi dung."""
    rows = ""
    for o in orders:
        rows += (
            "<tr><td>" + str(o["id"]) + "</td>"
            "<td>" + html.escape(o["product_name"]) + "</td>"
            "<td>" + str(o["quantity"]) + "</td>"
            '<td class="price">' + _money(o["total"]) + "</td>"
            '<td><a href="/don/' + str(o["id"]) + '">Xem</a></td></tr>'
        )
    body = (
        "<table><tr><th>Ma don</th><th>San pham</th><th>So luong</th>"
        "<th>Thanh tien</th><th></th></tr>" + rows + "</table>"
    )
    return layout("Don hang cua toi", body, user)


def order_detail_page(order, user):
    """Trang chi tiet mot don hang."""
    body = (
        "<table>"
        "<tr><th>Ma don</th><td>" + str(order["id"]) + "</td></tr>"
        "<tr><th>Ma nguoi dat</th><td>" + str(order["user_id"]) + "</td></tr>"
        "<tr><th>San pham</th><td>" + html.escape(order["product_name"]) + "</td></tr>"
        "<tr><th>So luong</th><td>" + str(order["quantity"]) + "</td></tr>"
        '<tr><th>Thanh tien</th><td class="price">' + _money(order["total"]) + "</td></tr>"
        "<tr><th>Thoi diem</th><td>" + html.escape(str(order["created_at"])) + "</td></tr>"
        "</table>"
    )
    return layout("Chi tiet don hang", body, user)


def admin_page(users, user):
    """Trang quan tri liet ke toan bo nguoi dung."""
    rows = ""
    for u in users:
        rows += (
            "<tr><td>" + str(u["id"]) + "</td>"
            "<td>" + html.escape(u["username"]) + "</td>"
            "<td>" + html.escape(u["full_name"]) + "</td>"
            "<td>" + html.escape(u["role"]) + "</td>"
            "<td>" + html.escape(u["email"]) + "</td></tr>"
        )
    body = (
        "<table><tr><th>Ma</th><th>Ten dang nhap</th><th>Ho ten</th>"
        "<th>Vai tro</th><th>Email</th></tr>" + rows + "</table>"
    )
    return layout("Quan tri nguoi dung", body, user)


def message_page(title, message, user):
    """Trang thong bao ngan gon."""
    return layout(title, "<p>" + html.escape(message) + "</p>", user)
