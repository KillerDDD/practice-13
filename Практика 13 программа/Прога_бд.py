# app_obyv.py - Адаптированная версия для новой структуры БД
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import os
import datetime
from pathlib import Path

# Попытка подключить Pillow для .jpg/.jpeg
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# ---------------- DB CONFIG ----------------
DB_PATH = "product.db"  # изменен путь к новой базе данных

# ---------------- UI STYLE ----------------
BG_MAIN = "#FFFFFF"
BG_SECOND = "#7FFF00"
BTN_ACCENT = "#00FA9A"
DISCOUNT_BG = "#2E8B57"
APP_FONT = ("Times New Roman", 11)

# Путь к логотипу/иконке
LOGO_PATH = "C:\\Users\\ZOM\\Desktop\\Практика11\\БУ\\Модуль 1\\import\\icon.png"
ICON_PATH = None

# ---------------- Helpers ----------------
def get_db_connection():
    """Получение соединения с SQLite базой данных"""
    return sqlite3.connect(DB_PATH)

def safe_columns(table):
    """Получение списка колонок таблицы"""
    try:
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(f"PRAGMA table_info({table});")
        cols = [r[1] for r in cur.fetchall()]
        cur.close()
        con.close()
        return cols
    except Exception as e:
        print("safe_columns error:", e)
        return []

def normalize_role(raw):
    """Нормализация роли пользователя"""
    if not raw:
        return "guest"
    r = str(raw).strip().lower()
    if "администратор" in r:
        return "admin"
    if "менедж" in r:
        return "manager"
    if "клиент" in r or "авториз" in r:
        return "client"
    return "guest"

# ---------------- Login Window ----------------
class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.win = tk.Toplevel(root)
        self.win.title("Вход — Продукты")
        self.win.geometry("420x300")
        self.win.config(bg=BG_MAIN)
        self.win.grab_set()

        # Иконка
        if os.path.exists(LOGO_PATH):
            try:
                icon = tk.PhotoImage(file=LOGO_PATH)
                self.win.iconphoto(False, icon)
                self.icon = icon
            except Exception:
                pass

        # Логотип / заголовок
        if os.path.exists(LOGO_PATH):
            try:
                if PIL_AVAILABLE:
                    im = Image.open(LOGO_PATH).resize((140, 80))
                    self.logo_img = ImageTk.PhotoImage(im)
                else:
                    self.logo_img = tk.PhotoImage(file=LOGO_PATH)
                tk.Label(self.win, image=self.logo_img, bg=BG_MAIN).pack(pady=6)
            except Exception:
                tk.Label(self.win, text="Продукты", font=("Times New Roman", 16, "bold"), bg=BG_MAIN).pack(pady=8)
        else:
            tk.Label(self.win, text="Продукты", font=("Times New Roman", 16, "bold"), bg=BG_MAIN).pack(pady=8)

        frm = tk.Frame(self.win, bg=BG_MAIN)
        frm.pack(fill=tk.X, padx=12, pady=6)

        tk.Label(frm, text="Логин:", font=APP_FONT, bg=BG_MAIN).grid(row=0, column=0, sticky=tk.W, pady=4)
        self.ent_login = tk.Entry(frm, font=APP_FONT)
        self.ent_login.grid(row=0, column=1, sticky=tk.EW, padx=6)
        tk.Label(frm, text="Пароль:", font=APP_FONT, bg=BG_MAIN).grid(row=1, column=0, sticky=tk.W, pady=4)
        self.ent_pass = tk.Entry(frm, font=APP_FONT, show="*")
        self.ent_pass.grid(row=1, column=1, sticky=tk.EW, padx=6)
        frm.columnconfigure(1, weight=1)

        btn_fr = tk.Frame(self.win, bg=BG_MAIN)
        btn_fr.pack(pady=10)
        tk.Button(btn_fr, text="Войти", bg=BTN_ACCENT, font=APP_FONT, command=self.try_login).grid(row=0, column=0, padx=6)
        tk.Button(btn_fr, text="Войти как гость", bg=BG_SECOND, font=APP_FONT, command=self.login_guest).grid(row=0, column=1, padx=6)

    def try_login(self):
        login = self.ent_login.get().strip()
        pwd = self.ent_pass.get().strip()
        
        # Проверка на admin/admin
        if login == "admin" and pwd == "admin":
            self.win.destroy()
            self.on_success({"id": 1, "login": "admin", "role": "admin"})
            return
            
        if not login or not pwd:
            messagebox.showwarning("Ввод", "Введите логин и пароль")
            return
            
        try:
            con = get_db_connection()
            cur = con.cursor()
            # Проверяем существование таблицы пользователей
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='пользователи';")
            if cur.fetchone():
                cur.execute("SELECT id_пользователя, Логин, Пароль, РольСотрудника FROM пользователи WHERE Логин = ? AND Пароль = ? LIMIT 1;", (login, pwd))
                row = cur.fetchone()
                if row:
                    uid, login_db, pwd_db, role_raw = row
                    role = normalize_role(role_raw)
                    self.win.destroy()
                    self.on_success({"id": uid, "login": login_db, "role": role})
                else:
                    messagebox.showerror("Ошибка", "Неправильный логин или пароль")
            else:
                # Нет таблицы пользователей - только admin
                messagebox.showerror("Ошибка", "Неправильный логин или пароль")
            cur.close()
            con.close()
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))

    def login_guest(self):
        self.win.destroy()
        self.on_success({"id": None, "login": "Гость", "role": "guest"})

# ---------------- Main Application ----------------
class MainApp:
    def __init__(self, root, user_info):
        self.root = root
        self.user = user_info
        self.root.title(f"Магазин продуктов — {self.user['login']} ({self.user['role']})")
        self.root.geometry("1300x700")
        self.root.config(bg=BG_MAIN)
        
        # Иконка
        if os.path.exists(LOGO_PATH):
            try:
                icon = tk.PhotoImage(file=LOGO_PATH)
                self.root.iconphoto(False, icon)
                self.icon = icon
            except Exception:
                pass
                
        self.build_ui()

    def build_ui(self):
        # верхняя панель: логин/выход
        top = tk.Frame(self.root, bg=BG_MAIN)
        top.pack(fill=tk.X, padx=8, pady=6)

        tk.Label(top, text=f"Пользователь: {self.user['login']}", font=APP_FONT, bg=BG_MAIN).pack(side=tk.LEFT)
        tk.Button(top, text="Сменить пользователя", bg=BTN_ACCENT, font=APP_FONT, command=self.logout).pack(side=tk.RIGHT, padx=6)

        # Notebook (вкладки)
        self.nb = ttk.Notebook(self.root)
        self.nb.place(x=10, y=50, width=1280, height=630)

        # вкладка продуктов питания
        self.frame_products = tk.Frame(self.nb, bg=BG_MAIN)
        self.nb.add(self.frame_products, text="Продукты питания")
        self.build_products_tab()
        
        # вкладка клиентов
        if self.user['role'] in ("manager", "admin"):
            self.frame_clients = tk.Frame(self.nb, bg=BG_MAIN)
            self.nb.add(self.frame_clients, text="Оптовые клиенты")
            self.build_clients_tab()
        
        # вкладка заказов
        if self.user['role'] in ("manager", "admin"):
            self.frame_orders = tk.Frame(self.nb, bg=BG_MAIN)
            self.nb.add(self.frame_orders, text="Заказы")
            self.build_orders_tab()

    def logout(self):
        if not messagebox.askyesno("Выход", "Сменить пользователя?"):
            return
        self.root.destroy()
        main()

    # ---------------- Products tab - Продукты питания ----------------
    def build_products_tab(self):
        top = tk.Frame(self.frame_products, bg=BG_MAIN)
        top.pack(fill=tk.X, padx=6, pady=6)
        
        if self.user['role'] in ('admin', "manager"):
            # Поиск/фильтры/сортировка
            tk.Label(top, text="Поиск (вид изделия):", font=APP_FONT, bg=BG_MAIN).grid(row=0, column=0, sticky=tk.W)
            self.search_var = tk.StringVar()
            tk.Entry(top, textvariable=self.search_var, font=APP_FONT, width=30).grid(row=0, column=1, padx=6)

            tk.Label(top, text="Мин. цена:", font=APP_FONT, bg=BG_MAIN).grid(row=0, column=2, sticky=tk.W)
            self.min_price = tk.StringVar()
            tk.Entry(top, textvariable=self.min_price, font=APP_FONT, width=10).grid(row=0, column=3, padx=6)

            tk.Label(top, text="Макс. цена:", font=APP_FONT, bg=BG_MAIN).grid(row=0, column=4, sticky=tk.W)
            self.max_price = tk.StringVar()
            tk.Entry(top, textvariable=self.max_price, font=APP_FONT, width=10).grid(row=0, column=5, padx=6)

            tk.Label(top, text="Сортировка:", font=APP_FONT, bg=BG_MAIN).grid(row=0, column=6, sticky=tk.W)
            self.sort_cb = ttk.Combobox(top, values=["По умолчанию", "Цена ↑", "Цена ↓", "Название ↑", "Название ↓"], state="readonly", width=18)
            self.sort_cb.current(0)
            self.sort_cb.grid(row=0, column=7, padx=6)

            tk.Button(top, text="Применить", bg=BTN_ACCENT, font=APP_FONT, command=self.refresh_products).grid(row=0, column=8, padx=6)

            # CRUD buttons
            btns = tk.Frame(self.frame_products, bg=BG_MAIN)
            btns.pack(fill=tk.X, padx=6, pady=4)
            self.btn_view = tk.Button(btns, text="Открыть карточку", bg=BG_SECOND, font=APP_FONT, command=self.open_selected_product)
            self.btn_view.pack(side=tk.RIGHT, padx=4)
            
        if self.user['role'] == 'admin':
            self.btn_add = tk.Button(btns, text="Добавить продукт", bg=BTN_ACCENT, font=APP_FONT, command=self.add_product)
            self.btn_add.pack(side=tk.LEFT, padx=4)
            self.btn_edit = tk.Button(btns, text="Редактировать продукт", bg=BTN_ACCENT, font=APP_FONT, command=self.edit_product)
            self.btn_edit.pack(side=tk.LEFT, padx=4)
            self.btn_del = tk.Button(btns, text="Удалить продукт", bg=BTN_ACCENT, font=APP_FONT, command=self.delete_product)
            self.btn_del.pack(side=tk.LEFT, padx=4)

        # Колонки для таблицы продуктов питания
        self.prod_cols = ["Код_продукции", "Вид_изделия", "Страна_производитель", "Фирма_производитель", "Цена"]
        
        self.tree_prod = ttk.Treeview(self.frame_products, columns=self.prod_cols, show="headings", selectmode="browse")
        self.tree_prod.pack(fill=tk.BOTH, expand=1, padx=6, pady=6)
        
        for c in self.prod_cols:
            self.tree_prod.heading(c, text=c)
            self.tree_prod.column(c, width=140)
            
        # scrollbars
        sv = ttk.Scrollbar(self.frame_products, orient=tk.VERTICAL, command=self.tree_prod.yview)
        sv.pack(side=tk.RIGHT, fill=tk.Y)
        sh = ttk.Scrollbar(self.frame_products, orient=tk.HORIZONTAL, command=self.tree_prod.xview)
        sh.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_prod.configure(yscrollcommand=sv.set, xscrollcommand=sh.set)
        self.tree_prod.bind("<Double-1>", lambda e: self.open_selected_product())

        self.refresh_products()

    def refresh_products(self):
        for i in self.tree_prod.get_children():
            self.tree_prod.delete(i)
            
        try:
            con = get_db_connection()
            cur = con.cursor()
            
            sql = "SELECT Код_продукции, Вид_изделия, Страна_производитель, Фирма_производитель, Цена FROM продукты_питания"
            params = []
            
            if hasattr(self, 'search_var') and self.user['role'] in ("manager", "admin"):
                where = []
                if self.search_var.get().strip():
                    where.append("Вид_изделия LIKE ?")
                    params.append("%" + self.search_var.get().strip() + "%")
                if self.min_price.get().strip():
                    try:
                        where.append("Цена >= ?")
                        params.append(float(self.min_price.get().strip()))
                    except:
                        pass
                if self.max_price.get().strip():
                    try:
                        where.append("Цена <= ?")
                        params.append(float(self.max_price.get().strip()))
                    except:
                        pass
                if where:
                    sql += " WHERE " + " AND ".join(where)
                    
                sort = self.sort_cb.get()
                if sort == "Цена ↑":
                    sql += " ORDER BY Цена ASC"
                elif sort == "Цена ↓":
                    sql += " ORDER BY Цена DESC"
                elif sort == "Название ↑":
                    sql += " ORDER BY Вид_изделия ASC"
                elif sort == "Название ↓":
                    sql += " ORDER BY Вид_изделия DESC"
                    
            cur.execute(sql + ";", params)
            rows = cur.fetchall()
            cur.close()
            con.close()
            
            for r in rows:
                self.tree_prod.insert("", tk.END, values=r)
                
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))

    def open_selected_product(self):
        sel = self.tree_prod.focus()
        if not sel:
            messagebox.showinfo("Инфо", "Выберите продукт")
            return
            
        vals = self.tree_prod.item(sel, "values")
        code = vals[0]
        
        try:
            con = get_db_connection()
            cur = con.cursor()
            cur.execute("SELECT * FROM продукты_питания WHERE Код_продукции=? LIMIT 1;", (code,))
            row = cur.fetchone()
            cur.close()
            con.close()
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))
            return
            
        if row:
            # Карточка продукта
            w = tk.Toplevel(self.root)
            w.title(f"Карточка: {row[1]}")
            w.geometry("750x550")
            w.config(bg=BG_MAIN)
            
            if os.path.exists(LOGO_PATH):
                try:
                    icon = tk.PhotoImage(file=LOGO_PATH)
                    w.iconphoto(False, icon)
                    self.icon = icon
                except:
                    pass
                    
            # Верхняя часть с названием
            tk.Label(w, text=row[1], font=("Times New Roman", 18, "bold"), bg=BG_MAIN).pack(pady=10)
            
            # Основной фрейм для изображения и информации
            main_frame = tk.Frame(w, bg=BG_MAIN)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Левая часть - изображение
            left_frame = tk.Frame(main_frame, bg=BG_MAIN, width=250, height=250)
            left_frame.pack(side=tk.LEFT, padx=10)
            left_frame.pack_propagate(False)
            
            # Поиск изображения
            image_path = self.find_image_for_product(row[0], row[1])
            
            if image_path and os.path.exists(image_path):
                try:
                    if PIL_AVAILABLE:
                        im = Image.open(image_path)
                        im.thumbnail((220, 220), Image.Resampling.LANCZOS)
                        imgtk = ImageTk.PhotoImage(im)
                        img_label = tk.Label(left_frame, image=imgtk, bg=BG_MAIN)
                        img_label.image = imgtk
                        img_label.pack(expand=True)
                    else:
                        imgtk = tk.PhotoImage(file=image_path)
                        img_label = tk.Label(left_frame, image=imgtk, bg=BG_MAIN)
                        img_label.image = imgtk
                        img_label.pack(expand=True)
                except Exception as e:
                    tk.Label(left_frame, text=f"Ошибка загрузки\nизображения", bg=BG_MAIN, fg="red", font=APP_FONT).pack(expand=True)
            else:
                # Заглушка вместо изображения
                img_placeholder = tk.Label(left_frame, text="🖼️\nНет\nизображения", 
                                           bg="#F0F0F0", width=20, height=10, 
                                           font=("Arial", 12), relief=tk.RIDGE)
                img_placeholder.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
            
            # Правая часть - информация
            right_frame = tk.Frame(main_frame, bg=BG_MAIN)
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
            
            info_text = f"""
    Код продукции: {row[0]}
    Вид изделия: {row[1]}
    Страна-производитель: {row[2]}
    Фирма-производитель: {row[3]}
    Цена: {row[4]} руб.
    """
            info_label = tk.Label(right_frame, text=info_text, bg=BG_MAIN, 
                                  font=("Courier", 11), justify=tk.LEFT)
            info_label.pack(anchor=tk.W, pady=10)
            
            # Кнопки
            btnf = tk.Frame(w, bg=BG_MAIN)
            btnf.pack(pady=15)
            tk.Button(btnf, text="Закрыть", bg=BTN_ACCENT, font=APP_FONT, 
                     command=w.destroy).pack(side=tk.RIGHT, padx=6)
            
            if self.user['role'] == 'admin':
                tk.Button(btnf, text="Редактировать", bg=BTN_ACCENT, font=APP_FONT, 
                         command=lambda: [w.destroy(), self.edit_product(code)]).pack(side=tk.LEFT, padx=6)
                tk.Button(btnf, text="Удалить", bg=BTN_ACCENT, font=APP_FONT, 
                         command=lambda: [w.destroy(), self.delete_product(code)]).pack(side=tk.LEFT, padx=6)

    def find_image_for_product(self, code, name):
        """Поиск изображения для продукта"""
        # Пути для поиска изображений
        search_paths = [
            f"images/{code}.jpg",
            f"images/{code}.png",
            f"images/{code}.jpeg",
            f"images/{name}.jpg",
            f"images/{name}.png",
            f"images/{name}.jpeg",
            f"products/{code}.jpg",
            f"products/{code}.png",
            f"products/{name}.jpg",
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                return path
        
        return None

    def add_product(self):
        ProductEditor(self.root, None, on_done=self.refresh_products)

    def edit_product(self, code=None):
        if not code:
            sel = self.tree_prod.focus()
            if not sel:
                messagebox.showinfo("Инфо", "Выберите продукт")
                return
            code = self.tree_prod.item(sel, "values")[0]
        ProductEditor(self.root, code, on_done=self.refresh_products)

    def delete_product(self, code=None):
        if not code:
            sel = self.tree_prod.focus()
            if not sel:
                messagebox.showinfo("Инфо", "Выберите продукт")
                return
            code = self.tree_prod.item(sel, "values")[0]
            
        if not messagebox.askyesno("Подтвердите", f"Удалить продукт {code}?"):
            return
            
        try:
            con = get_db_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM продукты_питания WHERE Код_продукции=?;", (code,))
            con.commit()
            cur.close()
            con.close()
            messagebox.showinfo("Готово", "Продукт удалён")
            self.refresh_products()
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))
            
    # ---------------- Clients tab ----------------
    def build_clients_tab(self):
        top = tk.Frame(self.frame_clients, bg=BG_MAIN)
        top.pack(fill=tk.X, padx=6, pady=6)
        
        tk.Label(top, text="Оптовые клиенты", font=("Times New Roman", 14, "bold"), bg=BG_MAIN).pack(side=tk.LEFT)
        
        if self.user['role'] == 'admin':
            btnf = tk.Frame(self.frame_clients, bg=BG_MAIN)
            btnf.pack(fill=tk.X, padx=6, pady=4)
            tk.Button(btnf, text="Добавить клиента", bg=BTN_ACCENT, font=APP_FONT, command=self.add_client).pack(side=tk.LEFT, padx=4)
            tk.Button(btnf, text="Редактировать клиента", bg=BTN_ACCENT, font=APP_FONT, command=self.edit_client).pack(side=tk.LEFT, padx=4)
            tk.Button(btnf, text="Удалить клиента", bg=BTN_ACCENT, font=APP_FONT, command=self.delete_client).pack(side=tk.LEFT, padx=4)
        
        self.client_cols = ["Номер_клиента", "Фамилия", "Имя", "Отчество", "Город"]
        
        self.tree_clients = ttk.Treeview(self.frame_clients, columns=self.client_cols, show="headings", selectmode="browse")
        self.tree_clients.pack(fill=tk.BOTH, expand=1, padx=6, pady=6)
        
        for c in self.client_cols:
            self.tree_clients.heading(c, text=c)
            self.tree_clients.column(c, width=120)
            
        sv = ttk.Scrollbar(self.frame_clients, orient=tk.VERTICAL, command=self.tree_clients.yview)
        sv.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_clients.configure(yscrollcommand=sv.set)
        
        self.refresh_clients()
        
    def refresh_clients(self):
        for i in self.tree_clients.get_children():
            self.tree_clients.delete(i)
            
        try:
            con = get_db_connection()
            cur = con.cursor()
            cur.execute("SELECT Номер_клиента, Фамилия, Имя, Отчество, Город FROM оптовые_клиенты;")
            rows = cur.fetchall()
            cur.close()
            con.close()
            
            for r in rows:
                self.tree_clients.insert("", tk.END, values=r)
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))
            
    def add_client(self):
        ClientEditor(self.root, None, on_done=self.refresh_clients)
        
    def edit_client(self):
        sel = self.tree_clients.focus()
        if not sel:
            messagebox.showinfo("Инфо", "Выберите клиента")
            return
        client_id = self.tree_clients.item(sel, "values")[0]
        ClientEditor(self.root, client_id, on_done=self.refresh_clients)
        
    def delete_client(self):
        sel = self.tree_clients.focus()
        if not sel:
            messagebox.showinfo("Инфо", "Выберите клиента")
            return
        client_id = self.tree_clients.item(sel, "values")[0]
        
        if not messagebox.askyesno("Подтвердите", f"Удалить клиента {client_id}?"):
            return
            
        try:
            con = get_db_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM оптовые_клиенты WHERE Номер_клиента=?;", (client_id,))
            con.commit()
            cur.close()
            con.close()
            messagebox.showinfo("Готово", "Клиент удалён")
            self.refresh_clients()
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))
            
    # ---------------- Orders tab ----------------
    def build_orders_tab(self):
        top = tk.Frame(self.frame_orders, bg=BG_MAIN)
        top.pack(fill=tk.X, padx=6, pady=6)
        
        tk.Label(top, text="Заказы", font=("Times New Roman", 14, "bold"), bg=BG_MAIN).pack(side=tk.LEFT)
        
        btnf = tk.Frame(self.frame_orders, bg=BG_MAIN)
        btnf.pack(fill=tk.X, padx=6, pady=4)
        
        if self.user['role'] == 'admin':
            tk.Button(btnf, text="Добавить заказ", bg=BTN_ACCENT, font=APP_FONT, command=self.add_order).pack(side=tk.LEFT, padx=4)
            tk.Button(btnf, text="Редактировать заказ", bg=BTN_ACCENT, font=APP_FONT, command=self.edit_order).pack(side=tk.LEFT, padx=4)
            tk.Button(btnf, text="Удалить заказ", bg=BTN_ACCENT, font=APP_FONT, command=self.delete_order).pack(side=tk.LEFT, padx=4)
        
        self.order_cols = ["Номер_Заказа", "Код_продукции", "Номер_клиента", "Количество", "Скидка"]
        
        self.tree_orders = ttk.Treeview(self.frame_orders, columns=self.order_cols, show="headings", selectmode="browse")
        self.tree_orders.pack(fill=tk.BOTH, expand=1, padx=6, pady=6)
        
        for c in self.order_cols:
            self.tree_orders.heading(c, text=c)
            self.tree_orders.column(c, width=120)
            
        sv = ttk.Scrollbar(self.frame_orders, orient=tk.VERTICAL, command=self.tree_orders.yview)
        sv.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_orders.configure(yscrollcommand=sv.set)
        
        self.refresh_orders()
        
    def refresh_orders(self):
        for i in self.tree_orders.get_children():
            self.tree_orders.delete(i)
            
        try:
            con = get_db_connection()
            cur = con.cursor()
            cur.execute("""
                SELECT з.Номер_Заказа, з.Продукты_питания_Код_продукции, 
                       з.Номер_клиента, з.Количество, з.Скидка 
                FROM заказы з;
            """)
            rows = cur.fetchall()
            cur.close()
            con.close()
            
            for r in rows:
                self.tree_orders.insert("", tk.END, values=r)
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))
            
    def add_order(self):
        OrderEditor(self.root, None, on_done=self.refresh_orders)
        
    def edit_order(self):
        sel = self.tree_orders.focus()
        if not sel:
            messagebox.showinfo("Инфо", "Выберите заказ")
            return
        order_id = self.tree_orders.item(sel, "values")[0]
        OrderEditor(self.root, order_id, on_done=self.refresh_orders)
        
    def delete_order(self):
        sel = self.tree_orders.focus()
        if not sel:
            messagebox.showinfo("Инфо", "Выберите заказ")
            return
        order_id = self.tree_orders.item(sel, "values")[0]
        
        if not messagebox.askyesno("Подтвердите", f"Удалить заказ {order_id}?"):
            return
            
        try:
            con = get_db_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM заказы WHERE Номер_Заказа=?;", (order_id,))
            con.commit()
            cur.close()
            con.close()
            messagebox.showinfo("Готово", "Заказ удалён")
            self.refresh_orders()
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))

# ---------------- Product editor ----------------
class ProductEditor:
    def __init__(self, parent, code, on_done=None):
        self.parent = parent
        self.code = code
        self.on_done = on_done
        self.win = tk.Toplevel(parent)
        self.win.title("Добавить продукт" if not code else f"Редактировать {code}")
        self.win.geometry("560x500")
        self.win.config(bg=BG_MAIN)
        
        if os.path.exists(LOGO_PATH):
            try:
                icon = tk.PhotoImage(file=LOGO_PATH)
                self.win.iconphoto(False, icon)
                self.icon = icon
            except:
                pass
                
        self.build()
        if code:
            self.load_product()

    def build(self):
        frm = tk.Frame(self.win, bg=BG_MAIN)
        frm.pack(fill=tk.BOTH, expand=1, padx=8, pady=8)
        
        tk.Label(frm, text="Код продукции:", font=APP_FONT, bg=BG_MAIN).grid(row=0, column=0, sticky=tk.W, pady=4)
        self.e_code = tk.Entry(frm, font=APP_FONT)
        self.e_code.grid(row=0, column=1, sticky=tk.EW, padx=6)
        
        tk.Label(frm, text="Вид изделия:", font=APP_FONT, bg=BG_MAIN).grid(row=1, column=0, sticky=tk.W, pady=4)
        self.e_name = tk.Entry(frm, font=APP_FONT)
        self.e_name.grid(row=1, column=1, sticky=tk.EW, padx=6)
        
        tk.Label(frm, text="Страна-производитель:", font=APP_FONT, bg=BG_MAIN).grid(row=2, column=0, sticky=tk.W, pady=4)
        self.e_country = tk.Entry(frm, font=APP_FONT)
        self.e_country.grid(row=2, column=1, sticky=tk.EW, padx=6)
        
        tk.Label(frm, text="Фирма-производитель:", font=APP_FONT, bg=BG_MAIN).grid(row=3, column=0, sticky=tk.W, pady=4)
        self.e_firm = tk.Entry(frm, font=APP_FONT)
        self.e_firm.grid(row=3, column=1, sticky=tk.EW, padx=6)
        
        tk.Label(frm, text="Цена:", font=APP_FONT, bg=BG_MAIN).grid(row=4, column=0, sticky=tk.W, pady=4)
        self.e_price = tk.Entry(frm, font=APP_FONT)
        self.e_price.grid(row=4, column=1, sticky=tk.EW, padx=6)
        
        frm.columnconfigure(1, weight=1)
        
        btnf = tk.Frame(self.win, bg=BG_MAIN)
        btnf.pack(pady=10)
        tk.Button(btnf, text="Сохранить", bg=BTN_ACCENT, font=APP_FONT, command=self.save).pack(side=tk.LEFT, padx=6)
        tk.Button(btnf, text="Отмена", bg="#CCCCCC", font=APP_FONT, command=self.win.destroy).pack(side=tk.LEFT, padx=6)

    def load_product(self):
        try:
            con = get_db_connection()
            cur = con.cursor()
            cur.execute("SELECT * FROM продукты_питания WHERE Код_продукции=? LIMIT 1;", (self.code,))
            r = cur.fetchone()
            cur.close()
            con.close()
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))
            r = None
            
        if r:
            self.e_code.insert(0, r[0])
            self.e_code.config(state=tk.DISABLED)
            self.e_name.insert(0, r[1] or "")
            self.e_country.insert(0, r[2] or "")
            self.e_firm.insert(0, r[3] or "")
            if r[4] is not None:
                self.e_price.insert(0, str(r[4]))

    def save(self):
        code = self.e_code.get().strip()
        name = self.e_name.get().strip()
        country = self.e_country.get().strip()
        firm = self.e_firm.get().strip()
        price = self.e_price.get().strip()
        
        if not code or not name:
            messagebox.showwarning("Ошибка", "Заполните код и вид изделия")
            return
            
        try:
            price_v = int(price) if price else None
        except:
            messagebox.showwarning("Ошибка", "Цена должна быть числом")
            return
            
        try:
            con = get_db_connection()
            cur = con.cursor()
            
            if self.code is None:
                cur.execute("""INSERT INTO продукты_питания 
                            (Код_продукции, Вид_изделия, Страна_производитель, Фирма_производитель, Цена) 
                            VALUES(?, ?, ?, ?, ?);""", 
                            (code, name, country, firm, price_v))
            else:
                cur.execute("""UPDATE продукты_питания 
                            SET Вид_изделия=?, Страна_производитель=?, Фирма_производитель=?, Цена=? 
                            WHERE Код_продукции=?;""", 
                            (name, country, firm, price_v, self.code))
                            
            con.commit()
            cur.close()
            con.close()
            messagebox.showinfo("Готово", "Сохранено")
            self.win.destroy()
            if self.on_done:
                self.on_done()
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))

# ---------------- Client editor ----------------
class ClientEditor:
    def __init__(self, parent, client_id, on_done=None):
        self.parent = parent
        self.client_id = client_id
        self.on_done = on_done
        self.win = tk.Toplevel(parent)
        self.win.title("Добавить клиента" if not client_id else f"Редактировать клиента {client_id}")
        self.win.geometry("500x400")
        self.win.config(bg=BG_MAIN)
        
        if os.path.exists(LOGO_PATH):
            try:
                icon = tk.PhotoImage(file=LOGO_PATH)
                self.win.iconphoto(False, icon)
                self.icon = icon
            except:
                pass
                
        self.build()
        if client_id:
            self.load_client()

    def build(self):
        frm = tk.Frame(self.win, bg=BG_MAIN)
        frm.pack(fill=tk.BOTH, expand=1, padx=8, pady=8)
        
        tk.Label(frm, text="Номер клиента:", font=APP_FONT, bg=BG_MAIN).grid(row=0, column=0, sticky=tk.W, pady=4)
        self.e_id = tk.Entry(frm, font=APP_FONT)
        self.e_id.grid(row=0, column=1, sticky=tk.EW, padx=6)
        
        tk.Label(frm, text="Фамилия:", font=APP_FONT, bg=BG_MAIN).grid(row=1, column=0, sticky=tk.W, pady=4)
        self.e_surname = tk.Entry(frm, font=APP_FONT)
        self.e_surname.grid(row=1, column=1, sticky=tk.EW, padx=6)
        
        tk.Label(frm, text="Имя:", font=APP_FONT, bg=BG_MAIN).grid(row=2, column=0, sticky=tk.W, pady=4)
        self.e_name = tk.Entry(frm, font=APP_FONT)
        self.e_name.grid(row=2, column=1, sticky=tk.EW, padx=6)
        
        tk.Label(frm, text="Отчество:", font=APP_FONT, bg=BG_MAIN).grid(row=3, column=0, sticky=tk.W, pady=4)
        self.e_patr = tk.Entry(frm, font=APP_FONT)
        self.e_patr.grid(row=3, column=1, sticky=tk.EW, padx=6)
        
        tk.Label(frm, text="Адрес:", font=APP_FONT, bg=BG_MAIN).grid(row=4, column=0, sticky=tk.W, pady=4)
        self.e_address = tk.Entry(frm, font=APP_FONT)
        self.e_address.grid(row=4, column=1, sticky=tk.EW, padx=6)
        
        tk.Label(frm, text="Город:", font=APP_FONT, bg=BG_MAIN).grid(row=5, column=0, sticky=tk.W, pady=4)
        self.e_city = tk.Entry(frm, font=APP_FONT)
        self.e_city.grid(row=5, column=1, sticky=tk.EW, padx=6)
        
        frm.columnconfigure(1, weight=1)
        
        btnf = tk.Frame(self.win, bg=BG_MAIN)
        btnf.pack(pady=10)
        tk.Button(btnf, text="Сохранить", bg=BTN_ACCENT, font=APP_FONT, command=self.save).pack(side=tk.LEFT, padx=6)
        tk.Button(btnf, text="Отмена", bg="#CCCCCC", font=APP_FONT, command=self.win.destroy).pack(side=tk.LEFT, padx=6)

    def load_client(self):
        try:
            con = get_db_connection()
            cur = con.cursor()
            cur.execute("SELECT * FROM оптовые_клиенты WHERE Номер_клиента=? LIMIT 1;", (self.client_id,))
            r = cur.fetchone()
            cur.close()
            con.close()
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))
            r = None
            
        if r:
            self.e_id.insert(0, r[0])
            self.e_id.config(state=tk.DISABLED)
            self.e_surname.insert(0, r[1] or "")
            self.e_name.insert(0, r[2] or "")
            self.e_patr.insert(0, r[3] or "")
            self.e_address.insert(0, r[4] or "")
            self.e_city.insert(0, r[5] or "")

    def save(self):
        client_id = self.e_id.get().strip()
        surname = self.e_surname.get().strip()
        name = self.e_name.get().strip()
        patr = self.e_patr.get().strip()
        address = self.e_address.get().strip()
        city = self.e_city.get().strip()
        
        if not client_id or not surname or not name:
            messagebox.showwarning("Ошибка", "Заполните номер, фамилию и имя клиента")
            return
            
        try:
            con = get_db_connection()
            cur = con.cursor()
            
            if self.client_id is None:
                cur.execute("""INSERT INTO оптовые_клиенты 
                            (Номер_клиента, Фамилия, Имя, Отчество, Адрес, Город) 
                            VALUES(?, ?, ?, ?, ?, ?);""", 
                            (client_id, surname, name, patr, address, city))
            else:
                cur.execute("""UPDATE оптовые_клиенты 
                            SET Фамилия=?, Имя=?, Отчество=?, Адрес=?, Город=? 
                            WHERE Номер_клиента=?;""", 
                            (surname, name, patr, address, city, self.client_id))
                            
            con.commit()
            cur.close()
            con.close()
            messagebox.showinfo("Готово", "Сохранено")
            self.win.destroy()
            if self.on_done:
                self.on_done()
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))

# ---------------- Order editor ----------------
class OrderEditor:
    def __init__(self, parent, order_id, on_done=None):
        self.parent = parent
        self.order_id = order_id
        self.on_done = on_done
        self.win = tk.Toplevel(parent)
        self.win.title("Добавить заказ" if not order_id else f"Редактировать заказ {order_id}")
        self.win.geometry("500x450")
        self.win.config(bg=BG_MAIN)
        
        if os.path.exists(LOGO_PATH):
            try:
                icon = tk.PhotoImage(file=LOGO_PATH)
                self.win.iconphoto(False, icon)
                self.icon = icon
            except:
                pass
                
        self.build()
        if order_id:
            self.load_order()

    def build(self):
        frm = tk.Frame(self.win, bg=BG_MAIN)
        frm.pack(fill=tk.BOTH, expand=1, padx=8, pady=8)
        
        tk.Label(frm, text="Номер заказа:", font=APP_FONT, bg=BG_MAIN).grid(row=0, column=0, sticky=tk.W, pady=4)
        self.e_id = tk.Entry(frm, font=APP_FONT)
        self.e_id.grid(row=0, column=1, sticky=tk.EW, padx=6)
        
        tk.Label(frm, text="Код продукции:", font=APP_FONT, bg=BG_MAIN).grid(row=1, column=0, sticky=tk.W, pady=4)
        self.e_product = tk.Entry(frm, font=APP_FONT)
        self.e_product.grid(row=1, column=1, sticky=tk.EW, padx=6)
        
        tk.Label(frm, text="Номер клиента:", font=APP_FONT, bg=BG_MAIN).grid(row=2, column=0, sticky=tk.W, pady=4)
        self.e_client = tk.Entry(frm, font=APP_FONT)
        self.e_client.grid(row=2, column=1, sticky=tk.EW, padx=6)
        
        tk.Label(frm, text="Количество:", font=APP_FONT, bg=BG_MAIN).grid(row=3, column=0, sticky=tk.W, pady=4)
        self.e_qty = tk.Entry(frm, font=APP_FONT)
        self.e_qty.grid(row=3, column=1, sticky=tk.EW, padx=6)
        
        tk.Label(frm, text="Скидка (%):", font=APP_FONT, bg=BG_MAIN).grid(row=4, column=0, sticky=tk.W, pady=4)
        self.e_discount = tk.Entry(frm, font=APP_FONT)
        self.e_discount.grid(row=4, column=1, sticky=tk.EW, padx=6)
        
        frm.columnconfigure(1, weight=1)
        
        btnf = tk.Frame(self.win, bg=BG_MAIN)
        btnf.pack(pady=10)
        tk.Button(btnf, text="Сохранить", bg=BTN_ACCENT, font=APP_FONT, command=self.save).pack(side=tk.LEFT, padx=6)
        tk.Button(btnf, text="Отмена", bg="#CCCCCC", font=APP_FONT, command=self.win.destroy).pack(side=tk.LEFT, padx=6)

    def load_order(self):
        try:
            con = get_db_connection()
            cur = con.cursor()
            cur.execute("SELECT * FROM заказы WHERE Номер_Заказа=? LIMIT 1;", (self.order_id,))
            r = cur.fetchone()
            cur.close()
            con.close()
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))
            r = None
            
        if r:
            self.e_id.insert(0, r[0])
            self.e_id.config(state=tk.DISABLED)
            self.e_product.insert(0, r[1] or "")
            self.e_client.insert(0, r[2] or "")
            if r[3] is not None:
                self.e_qty.insert(0, str(r[3]))
            if r[4] is not None:
                self.e_discount.insert(0, str(r[4]))

    def save(self):
        order_id = self.e_id.get().strip()
        product_code = self.e_product.get().strip()
        client_id = self.e_client.get().strip()
        qty = self.e_qty.get().strip()
        discount = self.e_discount.get().strip()
        
        if not order_id or not product_code or not client_id:
            messagebox.showwarning("Ошибка", "Заполните номер заказа, код продукции и номер клиента")
            return
            
        try:
            qty_v = int(qty) if qty else None
        except:
            messagebox.showwarning("Ошибка", "Количество должно быть числом")
            return
            
        try:
            discount_v = int(discount) if discount else None
        except:
            messagebox.showwarning("Ошибка", "Скидка должна быть числом")
            return
            
        try:
            con = get_db_connection()
            cur = con.cursor()
            
            if self.order_id is None:
                cur.execute("""INSERT INTO заказы 
                            (Номер_Заказа, Продукты_питания_Код_продукции, Номер_клиента, Количество, Скидка) 
                            VALUES(?, ?, ?, ?, ?);""", 
                            (order_id, product_code, client_id, qty_v, discount_v))
            else:
                cur.execute("""UPDATE заказы 
                            SET Продукты_питания_Код_продукции=?, Номер_клиента=?, Количество=?, Скидка=? 
                            WHERE Номер_Заказа=?;""", 
                            (product_code, client_id, qty_v, discount_v, self.order_id))
                            
            con.commit()
            cur.close()
            con.close()
            messagebox.showinfo("Готово", "Сохранено")
            self.win.destroy()
            if self.on_done:
                self.on_done()
        except Exception as e:
            messagebox.showerror("Ошибка БД", str(e))

# ---------------- Entrypoint ----------------
def main():
    root = tk.Tk()
    root.withdraw()
    
    # Проверка существования базы данных
    if not os.path.exists(DB_PATH):
        messagebox.showerror("Ошибка", f"База данных не найдена по пути: {DB_PATH}")
        return
        
    def on_login(user_info):
        root.deiconify()
        MainApp(root, user_info)
        
    LoginWindow(root, on_login)
    root.mainloop()

if __name__ == "__main__":
    main()
