import tkinter as tk
from tkinter import messagebox, ttk
import psycopg2

# Подключение к базе данных PostgreSQL
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="auto_parts_store",
            user="postgres",
            password="Tusson112",
            host="127.0.0.1",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return None

def register():
    username = username_entry.get()
    password = password_entry.get()
    email = email_entry.get()
    phone = phone_entry.get()
    privilege = 0  # Можно изменить, если нужно

    conn = connect_db()
    if not conn:
        messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
        return

    cursor = conn.cursor()

    try:
        cursor.execute(
            "CALL register_customer(%s, %s, %s, %s, %s)",
            (username, email, phone, password, privilege)
        )
        conn.commit()
        messagebox.showinfo("Успех", "Регистрация прошла успешно!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось зарегистрироваться: {e}")
    finally:
        cursor.close()
        conn.close()

def login():
    username = username_entry.get()
    password = password_entry.get()

    conn = connect_db()
    if not conn:
        messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
        return

    cursor = conn.cursor()

    try:
        cursor.execute(
            "CALL login_customer(%s, %s, %s)",
            (username, password, None)
        )
        is_authenticated = cursor.fetchone()[0]

        if is_authenticated:
            messagebox.showinfo("Успех", f"Добро пожаловать, {username}!")
            show_main_interface()
        else:
            messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось выполнить вход: {e}")
    finally:
        cursor.close()
        conn.close()

def show_register_form():
    for widget in root.winfo_children():
        widget.destroy()
    
    global username_entry, password_entry, email_entry, phone_entry

    frame = tk.Frame(root, width=frame_width, height=frame_height)
    frame.place(relx=0.5, rely=0.5, anchor='center')
    
    tk.Label(frame, text="Имя пользователя:").grid(row=0, column=0, padx=10, pady=5)
    username_entry = tk.Entry(frame)
    username_entry.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(frame, text="Пароль:").grid(row=1, column=0, padx=10, pady=5)
    password_entry = tk.Entry(frame, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(frame, text="Email:").grid(row=2, column=0, padx=10, pady=5)
    email_entry = tk.Entry(frame)
    email_entry.grid(row=2, column=1, padx=10, pady=5)
    
    tk.Label(frame, text="Телефон:").grid(row=3, column=0, padx=10, pady=5)
    phone_entry = tk.Entry(frame)
    phone_entry.grid(row=3, column=1, padx=10, pady=5)
    
    register_button = tk.Button(frame, text="Зарегистрироваться", command=register)
    register_button.grid(row=4, columnspan=2, pady=10)
    
    login_label = tk.Label(root, text="Уже есть аккаунт? ")
    login_label.place(relx=0.5, rely=0.85, anchor='e')
    login_link = tk.Label(root, text="Войти", fg="blue", cursor="hand2")
    login_link.place(relx=0.5, rely=0.85, anchor='w')
    login_link.bind("<Button-1>", lambda e: show_login_form())

def show_login_form():
    for widget in root.winfo_children():
        widget.destroy()
    
    global username_entry, password_entry

    frame = tk.Frame(root, width=frame_width, height=frame_height)
    frame.place(relx=0.5, rely=0.5, anchor='center')
    
    tk.Label(frame, text="Имя пользователя:").grid(row=0, column=0, padx=10, pady=5)
    username_entry = tk.Entry(frame)
    username_entry.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(frame, text="Пароль:").grid(row=1, column=0, padx=10, pady=5)
    password_entry = tk.Entry(frame, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=5)
    
    login_button = tk.Button(frame, text="Войти", command=login)
    login_button.grid(row=2, columnspan=2, pady=10)
    
    register_label = tk.Label(root, text="Нет аккаунта? ")
    register_label.place(relx=0.5, rely=0.85, anchor='e')
    register_link = tk.Label(root, text="Зарегистрироваться", fg="blue", cursor="hand2")
    register_link.place(relx=0.5, rely=0.85, anchor='w')
    register_link.bind("<Button-1>", lambda e: show_register_form())

def show_main_interface():
    for widget in root.winfo_children():
        widget.destroy()

    frame = tk.Frame(root, width=frame_width, height=frame_height)
    frame.place(relx=0.5, rely=0.5, anchor='center')

    table_label = tk.Label(frame, text="Выберите таблицу:")
    table_label.grid(row=0, column=0, padx=10, pady=5)
    table_choice = ttk.Combobox(frame, values=["customers", "orders", "products"])
    table_choice.grid(row=0, column=1, padx=10, pady=5)
    table_choice.current(0)  # Установить значение по умолчанию

    def view_data():
        table = table_choice.get()
        conn = connect_db()
        if not conn:
            messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
            return

        cursor = conn.cursor()
        try:
            cursor.execute(f'SELECT * FROM {table}')
            rows = cursor.fetchall()
            for row in rows:
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить данные: {e}")
        finally:
            cursor.close()
            conn.close()

    def show_add_data_form():
        table = table_choice.get()
        add_window = tk.Toplevel(root)
        add_window.title("Добавить данные")

        if table == "customers":
            tk.Label(add_window, text="Имя:").grid(row=0, column=0, padx=10, pady=5)
            name_entry = tk.Entry(add_window)
            name_entry.grid(row=0, column=1, padx=10, pady=5)

            tk.Label(add_window, text="Email:").grid(row=1, column=0, padx=10, pady=5)
            email_entry = tk.Entry(add_window)
            email_entry.grid(row=1, column=1, padx=10, pady=5)

            tk.Label(add_window, text="Телефон:").grid(row=2, column=0, padx=10, pady=5)
            phone_entry = tk.Entry(add_window)
            phone_entry.grid(row=2, column=1, padx=10, pady=5)

            tk.Label(add_window, text="Пароль:").grid(row=3, column=0, padx=10, pady=5)
            password_entry = tk.Entry(add_window, show="*")
            password_entry.grid(row=3, column=1, padx=10, pady=5)

            tk.Label(add_window, text="Привилегия:").grid(row=4, column=0, padx=10, pady=5)
            privilege_entry = tk.Entry(add_window)
            privilege_entry.grid(row=4, column=1, padx=10, pady=5)

            def add_data_to_db():
                name = name_entry.get()
                email = email_entry.get()
                phone = phone_entry.get()
                password = password_entry.get()
                privilege = privilege_entry.get()

                conn = connect_db()
                if not conn:
                    messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
                    return

                cursor = conn.cursor()

                try:
                    cursor.execute(
                        "CALL add_customer(%s, %s, %s, %s, %s)",
                        (name, email, phone, password, privilege)
                    )
                    conn.commit()
                    messagebox.showinfo("Успех", "Данные успешно добавлены!")
                    add_window.destroy()
                    # Перезагрузите данные в основном интерфейсе, если необходимо
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось добавить данные: {e}")
                finally:
                    cursor.close()
                    conn.close()

            add_button = tk.Button(add_window, text="Добавить", command=add_data_to_db)
            add_button.grid(row=5, columnspan=2, pady=10)

        # Добавьте формы для других таблиц аналогично

    def show_update_data_form():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите запись для обновления")
            return

        item = tree.item(selected_item)
        record = item['values']

        update_window = tk.Toplevel(root)
        update_window.title("Обновить данные")

        tk.Label(update_window, text="Имя:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(update_window)
        name_entry.insert(0, record[1])
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(update_window, text="Email:").grid(row=1, column=0, padx=10, pady=5)
        email_entry = tk.Entry(update_window)
        email_entry.insert(0, record[2])
        email_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(update_window, text="Телефон:").grid(row=2, column=0, padx=10, pady=5)
        phone_entry = tk.Entry(update_window)
        phone_entry.insert(0, record[3])
        phone_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(update_window, text="Пароль:").grid(row=3, column=0, padx=10, pady=5)
        password_entry = tk.Entry(update_window, show="*")
        password_entry.insert(0, record[4])
        password_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(update_window, text="Привилегия:").grid(row=4, column=0, padx=10, pady=5)
        privilege_entry = tk.Entry(update_window)
        privilege_entry.insert(0, record[5])
        privilege_entry.grid(row=4, column=1, padx=10, pady=5)

        def update_data_to_db():
            id = record[0]
            name = name_entry.get()
            email = email_entry.get()
            phone = phone_entry.get()
            password = password_entry.get()
            privilege = privilege_entry.get()

            conn = connect_db()
            if not conn:
                messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
                return

            cursor = conn.cursor()

            try:
                cursor.execute(
                    "CALL update_customer(%s, %s, %s, %s, %s, %s)",
                    (id, name, email, phone, password, privilege)
                )
                conn.commit()
                messagebox.showinfo("Успех", "Данные успешно обновлены!")
                update_window.destroy()
                # Перезагрузите данные в основном интерфейсе, если необходимо
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить данные: {e}")
            finally:
                cursor.close()
                conn.close()

        update_button = tk.Button(update_window, text="Обновить", command=update_data_to_db)
        update_button.grid(row=5, columnspan=2, pady=10)

    def delete_data():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите запись для удаления")
            return

        item = tree.item(selected_item)
        record = item['values']
        id = record[0]

        conn = connect_db()
        if not conn:
            messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
            return

        cursor = conn.cursor()

        try:
            cursor.execute(
                "CALL delete_customer(%s)",
                (id,)
            )
            conn.commit()
            messagebox.showinfo("Успех", "Данные успешно удалены!")
            tree.delete(selected_item)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить данные: {e}")
        finally:
            cursor.close()
            conn.close()

    tree = ttk.Treeview(frame, columns=("ID", "Name", "Email", "Phone", "Password", "Privilege"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Email", text="Email")
    tree.heading("Phone", text="Phone")
    tree.heading("Password", text="Password")
    tree.heading("Privilege", text="Privilege")
    tree.grid(row=1, columnspan=2, pady=10)

    view_button = tk.Button(frame, text="Просмотреть данные", command=view_data)
    view_button.grid(row=2, column=0, padx=10, pady=5)

    add_button = tk.Button(frame, text="Добавить данные", command=show_add_data_form)
    add_button.grid(row=2, column=1, padx=10, pady=5)

    update_button = tk.Button(frame, text="Обновить данные", command=show_update_data_form)
    update_button.grid(row=3, column=0, padx=10, pady=5)

    delete_button = tk.Button(frame, text="Удалить данные", command=delete_data)
    delete_button.grid(row=3, column=1, padx=10, pady=5)

# Создаем главное окно
root = tk.Tk()
root.title("Регистрация и Вход")

# Размеры окна
window_width = 350
window_height = 300

# Получаем размеры экрана пользователя
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Рассчитываем позицию окна по центру экрана
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2

# Устанавливаем позицию окна
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Размеры рамки
frame_width = 300
frame_height = 150

# Показать форму регистрации при запуске
show_register_form()

# Запускаем главный цикл обработки событий
root.mainloop()
