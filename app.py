import os
import json
import tkinter as tk
from tkinter import messagebox, ttk, filedialog, scrolledtext
import psycopg2
import pandas as pd
import logging

# Настройка логирования
log_folder = 'logs'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

logging.basicConfig(filename=os.path.join(log_folder, 'db_operations.log'), level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Глобальная переменная для языка
current_language = 'ru'

# Переводы
translations = {
    'ru': {
        'username': 'Имя пользователя:',
        'password': 'Пароль:',
        'email': 'Email:',
        'phone': 'Телефон:',
        'register': 'Зарегистрироваться',
        'login': 'Войти',
        'register_success': 'Регистрация прошла успешно!',
        'register_error': 'Не удалось зарегистрироваться: {}',
        'login_success': 'Добро пожаловать, {}!',
        'login_error': 'Неверное имя пользователя или пароль',
        'db_connect_error': 'Не удалось подключиться к базе данных',
        'view_data': 'Просмотреть данные',
        'add_data': 'Добавить данные',
        'update_data': 'Обновить данные',
        'delete_data': 'Удалить данные',
        'export_to_excel': 'Экспорт в WPS Office',
        'view_log': 'Просмотреть логи',
        'change_language': 'Сменить язык',
        'table': 'Выберите таблицу:',
        'search': 'Поиск:',
        'column': 'Колонка:',
        'already_have_account': 'Уже есть аккаунт?',
        'no_account': 'Нет аккаунта?'
    },
    'en': {
        'username': 'Username:',
        'password': 'Password:',
        'email': 'Email:',
        'phone': 'Phone:',
        'register': 'Register',
        'login': 'Login',
        'register_success': 'Registration successful!',
        'register_error': 'Registration failed: {}',
        'login_success': 'Welcome, {}!',
        'login_error': 'Invalid username or password',
        'db_connect_error': 'Failed to connect to the database',
        'view_data': 'View Data',
        'add_data': 'Add Data',
        'update_data': 'Update Data',
        'delete_data': 'Delete Data',
        'export_to_excel': 'Export to Excel',
        'view_log': 'View Logs',
        'change_language': 'Change Language',
        'table': 'Select Table:',
        'search': 'Search:',
        'column': 'Column:',
        'already_have_account': 'Already have an account?',
        'no_account': 'No account?'
    }
}

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
        logging.info("Подключение к базе данных установлено")
        return conn
    except Exception as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        return None

def get_translation(key):
    return translations[current_language].get(key, key)

def change_language():
    global current_language
    current_language = 'en' if current_language == 'ru' else 'ru'
    show_register_form()

def register():
    username = username_entry.get()
    password = password_entry.get()
    email = email_entry.get()
    phone = phone_entry.get()
    privilege = 0  # Можно изменить, если нужно

    conn = connect_db()
    if not conn:
        messagebox.showerror(get_translation('db_connect_error'), get_translation('db_connect_error'))
        return

    cursor = conn.cursor()

    try:
        cursor.execute(
            "CALL register_customer(%s, %s, %s, %s, %s)",
            (username, email, phone, password, privilege)
        )
        conn.commit()
        logging.info(f"Зарегистрирован новый пользователь: {username}")
        messagebox.showinfo(get_translation('register_success'), get_translation('register_success'))
    except Exception as e:
        logging.error(f"Ошибка регистрации пользователя {username}: {e}")
        messagebox.showerror(get_translation('register_error').format(e), get_translation('register_error').format(e))
    finally:
        cursor.close()
        conn.close()

def login():
    username = username_entry.get()
    password = password_entry.get()

    conn = connect_db()
    if not conn:
        messagebox.showerror(get_translation('db_connect_error'), get_translation('db_connect_error'))
        return

    cursor = conn.cursor()

    try:
        cursor.execute(
            "CALL login_customer(%s, %s, %s)",
            (username, password, None)
        )
        is_authenticated = cursor.fetchone()[0]

        if is_authenticated:
            logging.info(f"Пользователь {username} успешно вошел в систему")
            messagebox.showinfo(get_translation('login_success').format(username), get_translation('login_success').format(username))
            show_main_interface()
        else:
            logging.warning(f"Неудачная попытка входа для пользователя {username}")
            messagebox.showerror(get_translation('login_error'), get_translation('login_error'))
    except Exception as e:
        logging.error(f"Ошибка входа пользователя {username}: {e}")
        messagebox.showerror(get_translation('login_error').format(e), get_translation('login_error').format(e))
    finally:
        cursor.close()
        conn.close()

def show_register_form():
    for widget in root.winfo_children():
        widget.destroy()
    
    global username_entry, password_entry, email_entry, phone_entry

    frame = tk.Frame(root, width=frame_width, height=frame_height)
    frame.place(relx=0.5, rely=0.5, anchor='center')
    
    tk.Label(frame, text=get_translation('username')).grid(row=0, column=0, padx=10, pady=5)
    username_entry = tk.Entry(frame)
    username_entry.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(frame, text=get_translation('password')).grid(row=1, column=0, padx=10, pady=5)
    password_entry = tk.Entry(frame, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(frame, text=get_translation('email')).grid(row=2, column=0, padx=10, pady=5)
    email_entry = tk.Entry(frame)
    email_entry.grid(row=2, column=1, padx=10, pady=5)
    
    tk.Label(frame, text=get_translation('phone')).grid(row=3, column=0, padx=10, pady=5)
    phone_entry = tk.Entry(frame)
    phone_entry.grid(row=3, column=1, padx=10, pady=5)
    
    register_button = tk.Button(frame, text=get_translation('register'), command=register)
    register_button.grid(row=4, columnspan=2, pady=10)
    
    login_label = tk.Label(root, text=get_translation('already_have_account'))
    login_label.place(relx=0.5, rely=0.85, anchor='e')
    login_link = tk.Label(root, text=get_translation('login'), fg="blue", cursor="hand2")
    login_link.place(relx=0.5, rely=0.85, anchor='w')
    login_link.bind("<Button-1>", lambda e: show_login_form())

def show_login_form():
    for widget in root.winfo_children():
        widget.destroy()
    
    global username_entry, password_entry

    frame = tk.Frame(root, width=frame_width, height=frame_height)
    frame.place(relx=0.5, rely=0.5, anchor='center')
    
    tk.Label(frame, text=get_translation('username')).grid(row=0, column=0, padx=10, pady=5)
    username_entry = tk.Entry(frame)
    username_entry.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(frame, text=get_translation('password')).grid(row=1, column=0, padx=10, pady=5)
    password_entry = tk.Entry(frame, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=5)
    
    login_button = tk.Button(frame, text=get_translation('login'), command=login)
    login_button.grid(row=2, columnspan=2, pady=10)
    
    register_label = tk.Label(root, text=get_translation('no_account'))
    register_label.place(relx=0.5, rely=0.85, anchor='e')
    register_link = tk.Label(root, text=get_translation('register'), fg="blue", cursor="hand2")
    register_link.place(relx=0.5, rely=0.85, anchor='w')
    register_link.bind("<Button-1>", lambda e: show_register_form())

def show_main_interface():
    for widget in root.winfo_children():
        widget.destroy()

    frame = tk.Frame(root, width=frame_width, height=frame_height)
    frame.place(relx=0.5, rely=0.5, anchor='center')

    table_label = tk.Label(frame, text=get_translation('table'))
    table_label.grid(row=0, column=0, padx=10, pady=5)
    table_choice = ttk.Combobox(frame, values=["customers", "orders", "products", "categories", "orderdate"])
    table_choice.grid(row=0, column=1, padx=10, pady=5)
    table_choice.current(0)  # Установить значение по умолчанию

    search_label = tk.Label(frame, text=get_translation('search'))
    search_label.grid(row=1, column=0, padx=10, pady=5)
    search_entry = tk.Entry(frame)
    search_entry.grid(row=1, column=1, padx=10, pady=5)

    column_label = tk.Label(frame, text=get_translation('column'))
    column_label.grid(row=2, column=0, padx=10, pady=5)
    column_choice = ttk.Combobox(frame, values=["customer_id", "customer_name", "customer_email", "customer_phone", "customers_password", "customers_privellege"])
    column_choice.grid(row=2, column=1, padx=10, pady=5)
    column_choice.current(0)  # Установить значение по умолчанию

    def view_data():
        table = table_choice.get()
        search_query = search_entry.get()
        column = column_choice.get()
        conn = connect_db()
        if not conn:
            messagebox.showerror(get_translation('db_connect_error'), get_translation('db_connect_error'))
            return

        cursor = conn.cursor()
        try:
            tree.delete(*tree.get_children())
            if search_query:
                cursor.execute(f"SELECT * FROM {table} WHERE {column}::text ILIKE %s", (f'%{search_query}%',))
            else:
                cursor.execute(f'SELECT * FROM {table}')
            rows = cursor.fetchall()
            for row in rows:
                tree.insert("", tk.END, values=row)
            logging.info(f"Просмотр данных из таблицы: {table}")
        except Exception as e:
            logging.error(f"Ошибка просмотра данных из таблицы {table}: {e}")
            messagebox.showerror("Ошибка", f"Не удалось получить данные: {e}")
        finally:
            cursor.close()
            conn.close()

    def export_to_excel():
        table = table_choice.get()
        conn = connect_db()
        if not conn:
            messagebox.showerror(get_translation('db_connect_error'), get_translation('db_connect_error'))
            return

        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
            if file_path:
                df.to_excel(file_path, index=False)
                logging.info(f"Данные из таблицы {table} экспортированы в {file_path}")
                messagebox.showinfo("Успех", f"Данные экспортированы в {file_path}")
        except Exception as e:
            logging.error(f"Ошибка экспорта данных из таблицы {table}: {e}")
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_categories():
        conn = connect_db()
        if not conn:
            messagebox.showerror(get_translation('db_connect_error'), get_translation('db_connect_error'))
            return []
        
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT category_id, category_name FROM categories")
            categories = cursor.fetchall()
            logging.info("Получение категорий из таблицы categories")
            return categories
        except Exception as e:
            logging.error(f"Ошибка получения категорий: {e}")
            messagebox.showerror("Ошибка", f"Не удалось получить категории: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def show_add_data_form():
        table = table_choice.get()
        add_window = tk.Toplevel(root)
        add_window.title("Добавить данные")

        if table == "customers":
            tk.Label(add_window, text=get_translation('username')).grid(row=0, column=0, padx=10, pady=5)
            name_entry = tk.Entry(add_window)
            name_entry.grid(row=0, column=1, padx=10, pady=5)

            tk.Label(add_window, text=get_translation('email')).grid(row=1, column=0, padx=10, pady=5)
            email_entry = tk.Entry(add_window)
            email_entry.grid(row=1, column=1, padx=10, pady=5)

            tk.Label(add_window, text=get_translation('phone')).grid(row=2, column=0, padx=10, pady=5)
            phone_entry = tk.Entry(add_window)
            phone_entry.grid(row=2, column=1, padx=10, pady=5)

            tk.Label(add_window, text=get_translation('password')).grid(row=3, column=0, padx=10, pady=5)
            password_entry = tk.Entry(add_window, show="*")
            password_entry.grid(row=3, column=1, padx=10, pady=5)

            tk.Label(add_window, text=get_translation('privilege')).grid(row=4, column=0, padx=10, pady=5)
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
                    messagebox.showerror(get_translation('db_connect_error'), get_translation('db_connect_error'))
                    return

                cursor = conn.cursor()

                try:
                    cursor.execute(
                        "CALL add_customer(%s, %s, %s, %s, %s)",
                        (name, email, phone, password, privilege)
                    )
                    conn.commit()
                    logging.info(f"Добавлен новый пользователь: {name}")
                    messagebox.showinfo("Успех", "Данные успешно добавлены!")
                    add_window.destroy()
                except Exception as e:
                    logging.error(f"Ошибка добавления пользователя {name}: {e}")
                    messagebox.showerror("Ошибка", f"Не удалось добавить данные: {e}")
                finally:
                    cursor.close()
                    conn.close()

            add_button = tk.Button(add_window, text=get_translation('add_data'), command=add_data_to_db)
            add_button.grid(row=5, columnspan=2, pady=10)

        elif table == "categories":
            tk.Label(add_window, text=get_translation('category_name')).grid(row=0, column=0, padx=10, pady=5)
            category_name_entry = tk.Entry(add_window)
            category_name_entry.grid(row=0, column=1, padx=10, pady=5)

            def add_data_to_db():
                category_name = category_name_entry.get()

                conn = connect_db()
                if not conn:
                    messagebox.showerror(get_translation('db_connect_error'), get_translation('db_connect_error'))
                    return

                cursor = conn.cursor()

                try:
                    cursor.execute(
                        "CALL add_category(%s)",
                        (category_name,)
                    )
                    conn.commit()
                    logging.info(f"Добавлена новая категория: {category_name}")
                    messagebox.showinfo("Успех", "Категория успешно добавлена!")
                    add_window.destroy()
                except Exception as e:
                    logging.error(f"Ошибка добавления категории {category_name}: {e}")
                    messagebox.showerror("Ошибка", f"Не удалось добавить категорию: {e}")
                finally:
                    cursor.close()
                    conn.close()

            add_button = tk.Button(add_window, text=get_translation('add_data'), command=add_data_to_db)
            add_button.grid(row=1, columnspan=2, pady=10)

        elif table == "orderdate":
            tk.Label(add_window, text=get_translation('order_date')).grid(row=0, column=0, padx=10, pady=5)
            order_date_entry = tk.Entry(add_window)
            order_date_entry.grid(row=0, column=1, padx=10, pady=5)

            def add_data_to_db():
                order_date = order_date_entry.get()

                conn = connect_db()
                if not conn:
                    messagebox.showerror(get_translation('db_connect_error'), get_translation('db_connect_error'))
                    return

                cursor = conn.cursor()

                try:
                    cursor.execute(
                        "CALL add_orderdate(%s)",
                        (order_date,)
                    )
                    conn.commit()
                    logging.info(f"Добавлена новая дата заказа: {order_date}")
                    messagebox.showinfo("Успех", "Дата заказа успешно добавлена!")
                    add_window.destroy()
                except Exception as e:
                    logging.error(f"Ошибка добавления даты заказа {order_date}: {e}")
                    messagebox.showerror("Ошибка", f"Не удалось добавить дату заказа: {e}")
                finally:
                    cursor.close()
                    conn.close()

            add_button = tk.Button(add_window, text=get_translation('add_data'), command=add_data_to_db)
            add_button.grid(row=1, columnspan=2, pady=10)

        elif table == "products":
            tk.Label(add_window, text=get_translation('product_name')).grid(row=0, column=0, padx=10, pady=5)
            product_name_entry = tk.Entry(add_window)
            product_name_entry.grid(row=0, column=1, padx=10, pady=5)

            tk.Label(add_window, text=get_translation('price')).grid(row=1, column=0, padx=10, pady=5)
            price_entry = tk.Entry(add_window)
            price_entry.grid(row=1, column=1, padx=10, pady=5)

            tk.Label(add_window, text=get_translation('category')).grid(row=2, column=0, padx=10, pady=5)
            category_choice = ttk.Combobox(add_window, values=[f"{cat[0]}: {cat[1]}" for cat in get_categories()])
            category_choice.grid(row=2, column=1, padx=10, pady=5)

            def add_data_to_db():
                product_name = product_name_entry.get()
                price = price_entry.get()
                category = category_choice.get().split(": ")[1]  # Получаем название категории

                conn = connect_db()
                if not conn:
                    messagebox.showerror(get_translation('db_connect_error'), get_translation('db_connect_error'))
                    return

                cursor = conn.cursor()

                try:
                    cursor.execute(
                        "CALL add_product(%s, %s, %s)",
                        (product_name, price, category)
                    )
                    conn.commit()
                    logging.info(f"Добавлен новый продукт: {product_name}")
                    messagebox.showinfo("Успех", "Продукт успешно добавлен!")
                    add_window.destroy()
                except Exception as e:
                    logging.error(f"Ошибка добавления продукта {product_name}: {e}")
                    messagebox.showerror("Ошибка", f"Не удалось добавить продукт: {e}")
                finally:
                    cursor.close()
                    conn.close()

            add_button = tk.Button(add_window, text=get_translation('add_data'), command=add_data_to_db)
            add_button.grid(row=3, columnspan=2, pady=10)

    def show_update_data_form():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите запись для обновления")
            return

        table = table_choice.get()
        item = tree.item(selected_item)
        record = item['values']

        update_window = tk.Toplevel(root)
        update_window.title("Обновить данные")

        if table == "customers":
            tk.Label(update_window, text=get_translation('username')).grid(row=0, column=0, padx=10, pady=5)
            name_entry = tk.Entry(update_window)
            name_entry.insert(0, record[1])
            name_entry.grid(row=0, column=1, padx=10, pady=5)

            tk.Label(update_window, text=get_translation('email')).grid(row=1, column=0, padx=10, pady=5)
            email_entry = tk.Entry(update_window)
            email_entry.insert(0, record[2])
            email_entry.grid(row=1, column=1, padx=10, pady=5)

            tk.Label(update_window, text=get_translation('phone')).grid(row=2, column=0, padx=10, pady=5)
            phone_entry = tk.Entry(update_window)
            phone_entry.insert(0, record[3])
            phone_entry.grid(row=2, column=1, padx=10, pady=5)

            tk.Label(update_window, text=get_translation('password')).grid(row=3, column=0, padx=10, pady=5)
            password_entry = tk.Entry(update_window, show="*")
            password_entry.insert(0, record[4])
            password_entry.grid(row=3, column=1, padx=10, pady=5)

            tk.Label(update_window, text=get_translation('privilege')).grid(row=4, column=0, padx=10, pady=5)
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
                    messagebox.showerror(get_translation('db_connect_error'), get_translation('db_connect_error'))
                    return

                cursor = conn.cursor()

                try:
                    cursor.execute(
                        "CALL update_customer(%s, %s, %s, %s, %s, %s)",
                        (id, name, email, phone, password, privilege)
                    )
                    conn.commit()
                    logging.info(f"Обновлены данные пользователя: {name}")
                    messagebox.showinfo("Успех", "Данные успешно обновлены!")
                    update_window.destroy()
                except Exception as e:
                    logging.error(f"Ошибка обновления данных пользователя {name}: {e}")
                    messagebox.showerror("Ошибка", f"Не удалось обновить данные: {e}")
                finally:
                    cursor.close()
                    conn.close()

            update_button = tk.Button(update_window, text=get_translation('update_data'), command=update_data_to_db)
            update_button.grid(row=5, columnspan=2, pady=10)

        elif table == "categories":
            tk.Label(update_window, text=get_translation('category_name')).grid(row=0, column=0, padx=10, pady=5)
            category_name_entry = tk.Entry(update_window)
            category_name_entry.insert(0, record[1])
            category_name_entry.grid(row=0, column=1, padx=10, pady=5)

            def update_data_to_db():
                id = record[0]
                category_name = category_name_entry.get()

                conn = connect_db()
                if not conn:
                    messagebox.showerror(get_translation('db_connect_error'), get_translation('db_connect_error'))
                    return

                cursor = conn.cursor()

                try:
                    cursor.execute(
                        "CALL update_category(%s, %s)",
                        (id, category_name)
                    )
                    conn.commit()
                    logging.info(f"Обновлена категория: {category_name}")
                    messagebox.showinfo("Успех", "Категория успешно обновлена!")
                    update_window.destroy()
                except Exception as e:
                    logging.error(f"Ошибка обновления категории {category_name}: {e}")
                    messagebox.showerror("Ошибка", f"Не удалось обновить категорию: {e}")
                finally:
                    cursor.close()
                    conn.close()

            update_button = tk.Button(update_window, text=get_translation('update_data'), command=update_data_to_db)
            update_button.grid(row=1, columnspan=2, pady=10)

        elif table == "orderdate":
            tk.Label(update_window, text=get_translation('order_date')).grid(row=0, column=0, padx=10, pady=5)
            order_date_entry = tk.Entry(update_window)
            order_date_entry.insert(0, record[1])
            order_date_entry.grid(row=0, column=1, padx=10, pady=5)

            def update_data_to_db():
                id = record[0]
                order_date = order_date_entry.get()

                conn = connect_db()
                if not conn:
                    messagebox.showerror(get_translation('db_connect_error'), get_translation('db_connect_error'))
                    return

                cursor = conn.cursor()

                try:
                    cursor.execute(
                        "CALL update_orderdate(%s, %s)",
                        (id, order_date)
                    )
                    conn.commit()
                    logging.info(f"Обновлена дата заказа: {order_date}")
                    messagebox.showinfo("Успех", "Дата заказа успешно обновлена!")
                    update_window.destroy()
                except Exception as e:
                    logging.error(f"Ошибка обновления даты заказа {order_date}: {e}")
                    messagebox.showerror("Ошибка", f"Не удалось обновить дату заказа: {e}")
                finally:
                    cursor.close()
                    conn.close()

            update_button = tk.Button(update_window, text=get_translation('update_data'), command=update_data_to_db)
            update_button.grid(row=1, columnspan=2, pady=10)

        elif table == "products":
            tk.Label(update_window, text=get_translation('product_name')).grid(row=0, column=0, padx=10, pady=5)
            product_name_entry = tk.Entry(update_window)
            product_name_entry.insert(0, record[1])
            product_name_entry.grid(row=0, column=1, padx=10, pady=5)

            tk.Label(update_window, text=get_translation('price')).grid(row=1, column=0, padx=10, pady=5)
            price_entry = tk.Entry(update_window)
            price_entry.insert(0, record[2])
            price_entry.grid(row=1, column=1, padx=10, pady=5)

            tk.Label(update_window, text=get_translation('category')).grid(row=2, column=0, padx=10, pady=5)
            category_choice = ttk.Combobox(update_window, values=[f"{cat[0]}: {cat[1]}" for cat in get_categories()])
            category_choice.grid(row=2, column=1, padx=10, pady=5)
            category_choice.set(f"{record[3]}: {record[4]}")

            def update_data_to_db():
                id = record[0]
                product_name = product_name_entry.get()
                price = price_entry.get()
                category = category_choice.get().split(": ")[1]  # Получаем название категории

                conn = connect_db()
                if not conn:
                    messagebox.showerror(get_translation('db_connect_error'), get_translation('db_connect_error'))
                    return

                cursor = conn.cursor()

                try:
                    cursor.execute(
                        "CALL update_product(%s, %s, %s, %s)",
                        (id, product_name, price, category)
                    )
                    conn.commit()
                    logging.info(f"Обновлен продукт: {product_name}")
                    messagebox.showinfo("Успех", "Продукт успешно обновлен!")
                    update_window.destroy()
                except Exception as e:
                    logging.error(f"Ошибка обновления продукта {product_name}: {e}")
                    messagebox.showerror("Ошибка", f"Не удалось обновить продукт: {e}")
                finally:
                    cursor.close()
                    conn.close()

            update_button = tk.Button(update_window, text=get_translation('update_data'), command=update_data_to_db)
            update_button.grid(row=3, columnspan=2, pady=10)

    def delete_data():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите запись для удаления")
            return

        table = table_choice.get()
        item = tree.item(selected_item)
        record = item['values']
        id = record[0]

        conn = connect_db()
        if not conn:
            messagebox.showerror(get_translation('db_connect_error'), get_translation('db_connect_error'))
            return

        cursor = conn.cursor()

        try:
            if table == "customers":
                cursor.execute("CALL delete_customer(%s)", (id,))
            elif table == "categories":
                cursor.execute("CALL delete_category(%s)", (id,))
            elif table == "orderdate":
                cursor.execute("CALL delete_orderdate(%s)", (id,))
            elif table == "products":
                cursor.execute("CALL delete_product(%s)", (id,))
            conn.commit()
            logging.info(f"Удалена запись с ID {id} из таблицы {table}")
            messagebox.showinfo("Успех", "Данные успешно удалены!")
            tree.delete(selected_item)
        except Exception as e:
            logging.error(f"Ошибка удаления записи с ID {id} из таблицы {table}: {e}")
            messagebox.showerror("Ошибка", f"Не удалось удалить данные: {e}")
        finally:
            cursor.close()
            conn.close()

    def view_log():
        log_window = tk.Toplevel(root)
        log_window.title(get_translation('view_log'))

        st = scrolledtext.ScrolledText(log_window, width=80, height=20)
        st.pack(padx=10, pady=10)

        try:
            with open(os.path.join(log_folder, 'db_operations.log'), 'r') as log_file:
                st.insert(tk.END, log_file.read())
            logging.info("Просмотр истории операций")
        except Exception as e:
            logging.error(f"Ошибка при просмотре истории операций: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить историю операций: {e}")

    tree = ttk.Treeview(frame, columns=("ID", "Name", "Email", "Phone", "Password", "Privilege"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text=get_translation('username'))
    tree.heading("Email", text=get_translation('email'))
    tree.heading("Phone", text=get_translation('phone'))
    tree.heading("Password", text=get_translation('password'))
    tree.heading("Privilege", text=get_translation('privilege'))
    tree.grid(row=3, columnspan=2, pady=10)

    view_button = tk.Button(frame, text=get_translation('view_data'), command=view_data)
    view_button.grid(row=4, column=0, padx=10, pady=5)

    add_button = tk.Button(frame, text=get_translation('add_data'), command=show_add_data_form)
    add_button.grid(row=4, column=1, padx=10, pady=5)

    update_button = tk.Button(frame, text=get_translation('update_data'), command=show_update_data_form)
    update_button.grid(row=5, column=0, padx=10, pady=5)

    delete_button = tk.Button(frame, text=get_translation('delete_data'), command=delete_data)
    delete_button.grid(row=5, column=1, padx=10, pady=5)

    export_button = tk.Button(frame, text=get_translation('export_to_excel'), command=export_to_excel)
    export_button.grid(row=6, columnspan=2, pady=10)

    log_button = tk.Button(frame, text=get_translation('view_log'), command=view_log)
    log_button.grid(row=7, columnspan=2, pady=10)

    change_language_button = tk.Button(frame, text=get_translation('change_language'), command=change_language)
    change_language_button.grid(row=8, columnspan=2, pady=10)

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
