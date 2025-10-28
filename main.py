import threading
from socket import socket, AF_INET, SOCK_STREAM
from  customtkinter import *
from PIL import Image
import base64
import io
from tkinter import filedialog #add

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('400x300')
        self.title("Chat Client")
        self.username = "Yarik"
        self.label = None
        self.menu_frame = CTkFrame(self, width=30, height=300)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)
        self.is_show_menu = False
        self.speed_animate_menu = -20
        self.btn = CTkButton(self, text='▶️', command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)
        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x=0, y=0)
        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення:',  height=40)
        self.message_entry.place(x=0, y=0)
        self.send_button = CTkButton(self, text='>', width=50, height=40, command=self.send_message)
        self.send_button.place(x=0, y=0)
        self.open_img_button = CTkButton(self, text='📂', width=50, height=40, command=self.open_image)
        self.open_img_button.place(x=0, y=0)
        self.adaptive_ui()
        self.add_message("Демонстрація відображення зображення:", CTkImage(Image.open('setting.png'), size=(300, 300)))
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('7.tcp.eu.ngrok.io', 18668))
            hello = f"TEXT@{self.username}@[SYSTEM] {self.username} приєднався(лась) до чату!\n"
            self.sock.send(hello.encode('utf-8'))
            threading.Thread(target=self.recv_message, daemon=True).start()
        except Exception as e:
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀️')
            self.show_menu()
            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=30)
            self.entry = CTkEntry(self.menu_frame, placeholder_text="Ваш нік...")
            self.entry.pack()
            self.save_button = CTkButton(self.menu_frame, text="Зберегти", command=self.save_name)
            self.save_button.pack()

    def show_menu(self):
        self.menu_frame.configure(width=self.menu_frame.winfo_width() + self.speed_animate_menu)
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)
        elif self.menu_frame.winfo_width() >= 60 and not self.is_show_menu:
            self.after(10, self.show_menu)
            if self.label:
                self.label.destroy()
            if getattr(self, "entry", None):
                self.entry.destroy()
            if getattr(self, "save_button", None):
                self.save_button.destroy()

    def save_name(self):
        new_name = self.entry.get().strip()
        if new_name:
            self.username = new_name
            self.add_message(f"Ваш новий нік: {self.username}")

    def adaptive_ui(self):
        self.menu_frame.configure(height=self.winfo_height())
        self.chat_field.place(x=self.menu_frame.winfo_width())
        self.chat_field.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 20, height=self.winfo_height() - 40)
        self.send_button.place(x=self.winfo_width() - 50, y=self.winfo_height() - 40)
        self.message_entry.place(x=self.menu_frame.winfo_width(), y=self.send_button.winfo_y())
        self.message_entry.configure(width=self.winfo_width() - self.menu_frame.winfo_width() - 110)
        self.open_img_button.place(x=self.winfo_width() - 105, y=self.send_button.winfo_y())
        self.after(50, self.adaptive_ui)



    def add_message(self, message, img=None):
        message_frame = CTkFrame(self.chat_field, fg_color='grey')
        message_frame.pack(pady=5, anchor='w')
        wrapleng_size = self.winfo_width() - self.menu_frame.winfo_width() - 40
        if not img:
            CTkLabel(message_frame, text=message, wraplength=wrapleng_size, text_color='white', justify='left').pack(padx=10, pady=5)
        else:
            CTkLabel(message_frame, text=message, wraplength=wrapleng_size, text_color='white', image=img, compound='top', justify='left').pack(padx=10, pady=5)
#add
    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.add_message(
                f"{self.username}: {message}")
            data = f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_entry.delete(0, END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode('utf-8', errors='ignore')
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())
            except:
                break
        self.sock.close()

    def handle_line(self, line):  # Обробляє один повний рядок, отриманий від сервера
        if not line:  # Якщо рядок порожній
            return  # Нічого не робити
        parts = line.split("@", 3)  # Розділяє повідомлення максимум на 4 частини за символом "@"
        msg_type = parts[0]  # Перший елемент — тип повідомлення
        if msg_type == "TEXT":  # Якщо це текстове повідомлення
            if len(parts) >= 3:  # Перевірка наявності автора та тексту
                author = parts[1]  # Автор повідомлення
                message = parts[2]  # Сам текст
                self.add_message(f"{author}: {message}")  # Додає текст до чату
        elif msg_type == "IMAGE":  # Якщо це повідомлення із зображенням
            if len(parts) >= 4:  # Перевірка наявності всіх частин
                author = parts[1]  # Автор
                filename = parts[2]  # Ім’я файлу
                b64_img = parts[3]  # Зображення у форматі base64
                try:  # Спроба декодувати та відобразити
                    img_data = base64.b64decode(b64_img)  # Декодування base64 у байти
                    pil_img = Image.open(io.BytesIO(img_data))  # Створення об’єкта PIL.Image з потоку байтів
                    ctk_img = CTkImage(pil_img, size=(300, 300))  # Створення зображення для CustomTkinter
                    self.add_message(f"{author} надіслав(ла) зображення: {filename}",
                                     img=ctk_img)  # Додає до чату зображення
                except Exception as e:  # Якщо сталася помилка під час обробки
                    self.add_message(f"Помилка відображення зображення: {e}")  # Повідомляє про помилку
        else:  # Якщо тип повідомлення невідомий
            self.add_message(line)  # Просто показує рядок у чаті

    def open_image(self):  # Метод для вибору та надсилання зображення на сервер
        file_name = filedialog.askopenfilename()  # Відкриває діалогове вікно вибору файлу
        if not file_name:  # Якщо користувач нічого не вибрав
            return
        try:
            with open(file_name, "rb") as f:
                raw = f.read()
            b64_data = base64.b64encode(raw).decode()
            short_name = os.path.basename(file_name)
            data = f"IMAGE@{self.username}@{short_name}@{b64_data}\n"
            self.sock.sendall(data.encode())
            self.add_message('', CTkImage(light_image=Image.open(file_name),
                                          size=(300, 300)))
        except Exception as e:
            self.add_message(f"Не вдалося надіслати зображення: {e}")
#add

if __name__ == "__main__":
   win = MainWindow()
   win.mainloop()
