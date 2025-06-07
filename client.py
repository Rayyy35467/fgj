import socket  
import threading  
import customtkinter as ctk  
import tkinter.messagebox as mbox  

HOST = '127.0.0.1'  
PORT = 5000  

ctk.set_appearance_mode('Dark')  
ctk.set_default_color_theme('blue')  

class ChatClient(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Чат Клиент")  
        self.geometry('700x500')  

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=4)  
        self.grid_columnconfigure(1, weight=1)  

        self.chat_display = ctk.CTkTextbox(self, state='disabled', wrap='word')
        self.chat_display.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=10, pady=10)

        self.user_list = ctk.CTkTextbox(self, state="disabled", width=150) 
        self.user_list.grid(row=0, column=1, sticky="nsew", padx=10, pady=10) 
        
        self.entry_message = ctk.CTkEntry(self, placeholder_text="Введите сообщение...") 
        self.entry_message.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,10)) 
        
        self.send_button = ctk.CTkButton(self, text="Отправить", command=self.send_message) 
        self.send_button.grid(row=1, column=1, sticky="ew", padx=10, pady=(0,10))

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receive_thread = None  
        self.name = None  

        self.connect_to_server()
        self.protocol('WM_DELETE_WINDOW', self.on_close)  

        self.entry_message.bind("<Return>", lambda event: self.send_message())

    def connect_to_server(self):
        try:
            self.client.connect((HOST, PORT))  
            self.receive_thread = threading.Thread(target=self.receive)  
            self.receive_thread.daemon = True  
            self.receive_thread.start()  
        except Exception as e:
            mbox.showerror('Ошибка подключения', f'Не удалось подключиться к серверу: {e}')
            self.destroy()  

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')  
                if message == 'NAME':  
                    self.name = self.ask_name()  
                    self.client.send(self.name.encode('utf-8'))  
                elif message.startswith('USERLIST:'):  
                    users = message.replace('USERLIST:', '').split(',')  
                    self.update_user_list(users)  
                else:
                    self.update_chat_display(message)  
            except Exception as e:
                mbox.showerror('Ошибка', f'Ошибка получения сообщения: {e}')
                break  

    def send_message(self):
        message = self.entry_message.get()
        if message:
            if message.strip() == "/clear":
                self.clear_chat_display()
            if message.strip() == "/whoiam":
                self.update_chat_display(f" [CLIENT]: Ви {self.name}")
            if message.strip() == "/help":
                self.update_chat_display (f" [CLIENT]: /clear очистить чат\n/whoiam показать ваше имя\n/help список команд")
            else:
                self.client.send(f"{self.name}: {message}".encode('utf-8'))
                self.entry_message.delete(0, ctk.END)
        else:
            mbox.showerror('Помилка', "Введіть повідомлення перед відправкою")

    def clear_chat_display(self):
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")


    def ask_name(self):
        return ctk.CTkInputDialog(title="Ваше им'я", text="Введите имя:").get_input()
    
    def replace_emojis(self, message):
        emoji_map = {
            ":)": "😎",
    }
        for text, emoji in emoji_map.items():
            message = message.replace(text, emoji)
        return message


    def update_chat_display(self, message):
        message = self.replace_emojis(message)
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", message + "\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def update_user_list(self, users):
        self.user_list.configure(state="normal")
        self.user_list.delete("1.0", "end")
        for user in users:
            self.user_list.insert("end", user + "\n")
        self.user_list.configure(state="disabled")
        
    def on_close(self):
        try:
            self.client.close()
        except:
            pass
        self.destroy()


app = ChatClient()
app.mainloop()
