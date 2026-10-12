"""
CHAT CLIENT GUI (TCP, Tkinter) - dùng chung với server.py
Chạy: python client_gui.py
"""
import queue
import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog

SERVER_PORT = 5555
BUFFER_SIZE = 1024
SERVER_PROMPT = "Nhập tên của bạn: "  # Câu server gửi khi mới kết nối (ẩn đi khi hiển thị)


class ChatApp:
    def __init__(self, root, sock, name):
        self.root = root
        self.sock = sock
        self.name = name
        self.incoming = queue.Queue()  # Hàng đợi tin nhắn từ luồng nhận -> giao diện
        self.running = True

        root.title(f"Chat TCP - {name}")
        root.geometry("480x520")

        # Khung hiển thị tin nhắn (chỉ đọc)
        self.chat_box = scrolledtext.ScrolledText(root, state="disabled", wrap=tk.WORD,
                                                  font=("Arial", 11))
        self.chat_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 4))
        self.chat_box.tag_config("me", foreground="#0b6bcb", justify="right")
        self.chat_box.tag_config("system", foreground="#888888", font=("Arial", 10, "italic"))

        # Khung nhập + nút gửi
        bottom = tk.Frame(root)
        bottom.pack(fill=tk.X, padx=8, pady=(0, 8))
        self.entry = tk.Entry(bottom, font=("Arial", 11))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self.entry.bind("<Return>", self.send_message)
        self.entry.focus()
        tk.Button(bottom, text="Gửi", width=8, command=self.send_message).pack(side=tk.LEFT, padx=(6, 0))

        root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Gửi tên cho server rồi bật luồng nhận tin
        self.sock.sendall(name.encode("utf-8"))
        threading.Thread(target=self.receive_loop, daemon=True).start()
        self.root.after(100, self.process_queue)

    def receive_loop(self):
        """Luồng nền: nhận dữ liệu từ server và đẩy vào hàng đợi."""
        while self.running:
            try:
                data = self.sock.recv(BUFFER_SIZE)
                if not data:
                    self.incoming.put("*** Server đã đóng kết nối ***\n")
                    break
                self.incoming.put(data.decode("utf-8"))
            except OSError:
                break

    def process_queue(self):
        """Chạy trên luồng giao diện: lấy tin từ hàng đợi và hiển thị."""
        while not self.incoming.empty():
            text = self.incoming.get().replace(SERVER_PROMPT, "")
            if text.strip():
                tag = "system" if text.startswith("***") or text.startswith("Chào") \
                    or text.startswith("Đang online") else None
                self.show(text, tag)
        if self.running:
            self.root.after(100, self.process_queue)

    def show(self, text, tag=None):
        self.chat_box.config(state="normal")
        self.chat_box.insert(tk.END, text if text.endswith("\n") else text + "\n", tag)
        self.chat_box.config(state="disabled")
        self.chat_box.see(tk.END)

    def send_message(self, event=None):
        msg = self.entry.get().strip()
        if not msg:
            return
        try:
            self.sock.sendall(msg.encode("utf-8"))
        except OSError:
            messagebox.showerror("Lỗi", "Mất kết nối tới server.")
            return
        self.entry.delete(0, tk.END)
        if msg == "/quit":
            self.on_close()
        elif msg != "/list":
            self.show(f"Bạn: {msg}", "me")  # Server không gửi lại tin cho người gửi nên tự hiển thị

    def on_close(self):
        self.running = False
        try:
            self.sock.sendall(b"/quit")
        except OSError:
            pass
        self.sock.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    root.withdraw()  # Ẩn cửa sổ chính trong lúc hỏi thông tin
    host = simpledialog.askstring("Kết nối", "Địa chỉ server:", initialvalue="127.0.0.1", parent=root)
    if not host:
        return
    name = simpledialog.askstring("Tên người dùng", "Nhập tên của bạn:", parent=root)
    if not name:
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host.strip(), SERVER_PORT))
    except OSError:
        messagebox.showerror("Lỗi", "Không kết nối được tới server.\nHãy kiểm tra server đã chạy chưa.")
        return

    root.deiconify()
    ChatApp(root, sock, name.strip())
    root.mainloop()


if __name__ == "__main__":
    main()
