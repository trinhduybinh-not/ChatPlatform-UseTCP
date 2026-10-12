Cách chạy demo

Cần mở nhiều cửa sổ terminal:
Có 2 phiên bản client
Bản console (client.py) và bản GUI dùng thư viện Tkinter (client_gui.py)
Terminal 1 (server): python server.py

Terminal 2 (client 1): python client.py, rồi nhập tên, ví dụ “An”

Terminal 3 (client 2): python client.py, rồi nhập tên, ví dụ “Binh”

Sau đó gõ tin nhắn ở một client thì client còn lại sẽ nhận được. Chụp màn hình cả 3 cửa sổ để đưa vào báo cáo.

Nếu chạy trên nhiều máy cùng mạng LAN (demo sẽ ấn tượng hơn), chạy client bằng python client.py <IP máy server>, ví dụ python client.py 192.168.1.10.

Chức năng
Nhiều client chat cùng lúc (mỗi client một luồng threading riêng trên server)
Đặt tên người dùng khi vào phòng
Thông báo khi có người vào hoặc rời phòng
Lệnh /list xem ai đang online, /quit để thoát
Ý chính để giải thích trong báo cáo
Server: socket (TCP) → bind → listen → accept trong vòng lặp. Mỗi client mới được giao cho một luồng chạy handle_client. Hàm broadcast gửi tin cho tất cả client khác. Biến clients_lock dùng để tránh xung đột khi nhiều luồng cùng sửa danh sách client.
Client: connect tới server, dùng 2 luồng: luồng phụ liên tục nhận tin từ server, luồng chính chờ người dùng gõ và gửi đi. Cần 2 luồng vì input() và recv() đều chặn (blocking).
Vì sao chọn TCP: đảm bảo tin nhắn đến đủ và đúng thứ tự.
