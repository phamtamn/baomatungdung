# MiniShop: hướng dẫn chạy

MiniShop là một ứng dụng web nhỏ, viết bằng Python, dùng làm dự án chạy xuyên suốt học phần
04210 "Bảo mật phần mềm". Tài liệu này viết cho người chưa từng mở dòng lệnh, do đó chúng tôi
ghi từng bước một.

Ứng dụng này cố ý chứa lỗ hổng để phục vụ việc học. Sinh viên chỉ chạy nó trên máy cá nhân,
không đưa nó ra mạng của trường. Máy chủ được cấu hình chỉ lắng nghe trên máy của chính mình.

## 1. Ứng dụng cần gì

MiniShop chỉ cần Python phiên bản 3.9 trở lên. Ứng dụng không dùng bất kỳ gói ngoài nào, nên
sinh viên không phải chạy `pip install`, không cần quyền quản trị máy.

## 2. Kiểm tra máy đã có Python chưa

### Trên Windows

1. Bấm phím Windows, gõ chữ `cmd`, rồi mở "Command Prompt".
2. Trong cửa sổ đen vừa hiện ra, gõ dòng sau rồi bấm Enter:

   ```
   python --version
   ```

3. Nếu màn hình in ra dòng kiểu `Python 3.11.5` thì máy đã có Python. Số phiên bản cần từ
   3.9 trở lên.

### Trên macOS và Linux

1. Mở ứng dụng "Terminal".
2. Gõ dòng sau rồi bấm Enter:

   ```
   python3 --version
   ```

3. Nếu màn hình in ra dòng kiểu `Python 3.11.5` thì máy đã có Python.

## 3. Nếu máy chưa có Python

Có ba nhánh dự phòng, xếp theo thứ tự ưu tiên.

1. **Dùng phòng máy có sẵn Python.** Phòng PM401 và PM601 đã cài sẵn Python. Sinh viên chỉ
   cần đăng nhập máy phòng rồi làm theo mục 2.
2. **Dùng bản Python xách tay (portable) không cần quyền quản trị.** Trên Windows, tải bản
   "Windows embeddable package" từ trang chính thức python.org, giải nén vào một thư mục trong
   tài khoản của mình, rồi gọi Python bằng đường dẫn tới tệp `python.exe` trong thư mục đó.
   Cách này không đòi quyền quản trị máy.
3. **Dùng laptop cá nhân.** Cài Python từ python.org lên máy của mình, chọn phiên bản 3.9
   trở lên. Trên Windows, khi cài nhớ đánh dấu ô "Add Python to PATH".

Sau khi cài xong, quay lại mục 2 để kiểm tra máy đã nhận Python chưa.

## 4. Chạy MiniShop

1. Tải thư mục `minishop` về máy, ghi nhớ nó nằm ở đâu, ví dụ trong thư mục Tải xuống
   (Downloads).
2. Mở dòng lệnh như ở mục 2.
3. Chuyển vào thư mục `minishop`. Gõ chữ `cd`, một dấu cách, rồi đường dẫn tới thư mục, ví dụ:

   Trên Windows:

   ```
   cd C:\Users\ten_cua_ban\Downloads\minishop
   ```

   Trên macOS và Linux:

   ```
   cd ~/Downloads/minishop
   ```

4. Chạy ứng dụng bằng đúng một lệnh. Trên Windows:

   ```
   python app.py
   ```

   Trên macOS và Linux:

   ```
   python3 app.py
   ```

Lần chạy đầu tiên, ứng dụng tự tạo cơ sở dữ liệu và tự nạp dữ liệu mẫu, không cần bước riêng.

## 5. Cách biết đã chạy được

Nếu chạy đúng, màn hình in ra hai dòng sau:

```
MiniShop dang chay tai http://127.0.0.1:8000
CANH BAO: ung dung nay CO Y chua lo hong, chi chay cuc bo, khong dua ra mang.
```

Khi thấy hai dòng này, mở trình duyệt web rồi gõ địa chỉ sau vào thanh địa chỉ:

```
http://127.0.0.1:8000
```

Trang danh sách sản phẩm hiện ra là ứng dụng đã chạy được. Có thể đăng nhập bằng tài khoản
mẫu: tên đăng nhập `lan`, mật khẩu `matkhau1`.

## 6. Cách dừng ứng dụng

Quay lại cửa sổ dòng lệnh, bấm tổ hợp phím `Ctrl` và `C` cùng lúc. Ứng dụng in ra dòng
`Da dung may chu.` rồi thoát.

## 7. Nếu cổng 8000 đã bị chiếm

Có thể một ứng dụng khác đang dùng cổng 8000. Khi đó MiniShop không đổ ra thông báo lỗi khó
hiểu, mà in ra một dòng hướng dẫn:

```
Cong 8000 dang bi chiem. Hay dong ung dung dang giu cong do, hoac sua bien PORT
trong app.py sang mot so khac (vi du 8080) roi chay lai.
```

Sinh viên mở tệp `app.py` bằng một trình soạn thảo văn bản, tìm dòng `PORT = 8000`, đổi số
`8000` thành `8080`, lưu lại, rồi chạy lại lệnh ở mục 4. Khi đó địa chỉ mở trong trình duyệt
cũng đổi thành `http://127.0.0.1:8080`.

## 8. Chạy bộ kiểm thử khói

Bộ kiểm thử khói xác nhận máy chủ khởi động được và các trang chính trả về đúng. Trong thư
mục `minishop`, chạy lệnh sau. Trên Windows:

```
python -m unittest discover tests
```

Trên macOS và Linux:

```
python3 -m unittest discover tests
```

Nếu mọi việc bình thường, dòng cuối in ra chữ `OK`.

## 9. Cấu trúc thư mục

```
minishop/
    app.py              dinh tuyen va xu ly HTTP, diem khoi dong
    db.py               moi truy cap co so du lieu
    views.py            sinh HTML
    seed.py             tao luoc do va nap du lieu mau
    README.md           tai lieu nay
    tests/
        test_smoke.py   kiem thu khoi
```

Tệp `minishop.db` xuất hiện sau lần chạy đầu, đó là cơ sở dữ liệu do ứng dụng tự tạo. Xóa tệp
này rồi chạy lại sẽ nạp lại dữ liệu mẫu từ đầu.
