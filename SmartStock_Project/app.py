import customtkinter as ctk
from tkinter import messagebox, ttk
import os
import sys

# Allow direct execution of the packaged script, where database.py is in _internal.
_internal_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_internal')
if os.path.isdir(_internal_dir):
    sys.path.insert(0, _internal_dir)

import database
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime

# --- MODERN BLUE & WHITE THEME CONFIGURATION ---
ctk.set_appearance_mode("Dark")  # Clean dark background paired with Modern Blue accent
ctk.set_default_color_theme("blue")

# Theme Colors Palette
COLOR_PRIMARY_BLUE = "#1E88E5"       # Modern Electric/Royal Blue
COLOR_HOVER_BLUE = "#1565C0"         # Darker Blue on hover
COLOR_CARD_BG = "#212121"            # Clean Slate Dark Gray
COLOR_TEXT_WHITE = "#FFFFFF"         # Bright White text
COLOR_TEXT_SUBTLE = "#B0BEC5"        # Soft Gray/White
COLOR_DANGER_RED = "#E53935"         # Modern Coral Red
COLOR_DANGER_HOVER = "#C62828"       # Dark Red

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SmartStock - System Login")
        self.geometry("400x360")
        self.resizable(False, False)

        database.init_db()

        # Login Header Card
        self.card = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=12)
        self.card.pack(pady=25, padx=25, fill="both", expand=True)

        ctk.CTkLabel(
            self.card, 
            text="🔐 SmartStock Login", 
            font=ctk.CTkFont(size=22, weight="bold"), 
            text_color=COLOR_TEXT_WHITE
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            self.card, 
            text="Inventory Management System", 
            font=ctk.CTkFont(size=12), 
            text_color=COLOR_TEXT_SUBTLE
        ).pack(pady=(0, 15))

        self.entry_user = ctk.CTkEntry(
            self.card, 
            placeholder_text="👤 Username", 
            width=260, 
            fg_color="#2C2C2C", 
            border_color=COLOR_PRIMARY_BLUE
        )
        self.entry_user.pack(pady=8)

        self.entry_pass = ctk.CTkEntry(
            self.card, 
            placeholder_text="🔑 Password", 
            show="*", 
            width=260, 
            fg_color="#2C2C2C", 
            border_color=COLOR_PRIMARY_BLUE
        )
        self.entry_pass.pack(pady=8)

        self.btn_login = ctk.CTkButton(
            self.card, 
            text="🚀 Login to Dashboard", 
            width=260, 
            fg_color=COLOR_PRIMARY_BLUE, 
            hover_color=COLOR_HOVER_BLUE, 
            font=ctk.CTkFont(weight="bold"), 
            command=self.login
        )
        self.btn_login.pack(pady=20)

    def login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()

        role = database.authenticate_user(username, password)

        if role:
            database.log_activity(username, "User Logged In")
            self.withdraw()
            SmartStockApp(self, username, role)
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.")

class UpdateStockWindow(ctk.CTkToplevel):
    def __init__(self, parent, item, refresh_callback, current_user):
        super().__init__(parent)
        self.title("✏️ Update Stock & Product Details")
        self.geometry("420x380")
        self.attributes('-topmost', True)
        
        self.product_id = item[0]
        self.refresh_callback = refresh_callback
        self.current_user = current_user

        ctk.CTkLabel(
            self, 
            text=f"✏️ Update Item #{self.product_id}", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color=COLOR_TEXT_WHITE
        ).pack(pady=15)

        self.entry_name = ctk.CTkEntry(self, placeholder_text="Product Name", border_color=COLOR_PRIMARY_BLUE)
        self.entry_name.insert(0, item[1])
        self.entry_name.pack(pady=6, padx=25, fill="x")

        self.entry_category = ctk.CTkEntry(self, placeholder_text="Category", border_color=COLOR_PRIMARY_BLUE)
        self.entry_category.insert(0, item[2])
        self.entry_category.pack(pady=6, padx=25, fill="x")

        self.entry_price = ctk.CTkEntry(self, placeholder_text="Price (PHP)", border_color=COLOR_PRIMARY_BLUE)
        self.entry_price.insert(0, str(item[3]))
        self.entry_price.pack(pady=6, padx=25, fill="x")

        self.entry_qty = ctk.CTkEntry(self, placeholder_text="Quantity", border_color=COLOR_PRIMARY_BLUE)
        self.entry_qty.insert(0, str(item[4]))
        self.entry_qty.pack(pady=6, padx=25, fill="x")

        ctk.CTkButton(
            self, 
            text="💾 Save Changes", 
            command=self.save_changes, 
            fg_color=COLOR_PRIMARY_BLUE, 
            hover_color=COLOR_HOVER_BLUE, 
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=20)

    def save_changes(self):
        try:
            database.update_product(
                self.product_id,
                self.entry_name.get(),
                self.entry_category.get(),
                float(self.entry_price.get()),
                int(self.entry_qty.get())
            )
            database.log_activity(self.current_user, f"Updated Product ID {self.product_id}")
            messagebox.showinfo("Success", "Product updated successfully!")
            self.after(120, self._finish_save)
        except ValueError:
            messagebox.showerror("Error", "Invalid inputs!")

    def _finish_save(self):
        self.refresh_callback()
        self.destroy()

class SmartStockApp(ctk.CTkToplevel):
    def __init__(self, login_window, username, role):
        super().__init__(login_window)

        self.login_window = login_window
        self.username = username
        self.role = role

        self.title(f"SmartStock - Inventory System | User: {self.username} ({self.role})")
        self.geometry("1180x800")
        self.minsize(980, 680)
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self._search_after_id = None
        self.all_products = []

        self.create_widgets()
        self.load_data(refresh=True)

    def create_widgets(self):
        self.header_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=12)
        self.header_frame.pack(pady=(16, 4), padx=22, fill="x")

        title_group = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_group.pack(side="left", padx=20, pady=12)
        ctk.CTkLabel(
            title_group, text="SmartStock", font=ctk.CTkFont(size=23, weight="bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_group, text=f"Inventory dashboard  |  Signed in as {self.username} ({self.role})",
            font=ctk.CTkFont(size=12), text_color=COLOR_TEXT_SUBTLE
        ).pack(anchor="w", pady=(2, 0))
        ctk.CTkButton(
            self.header_frame, text="Log out", fg_color=COLOR_DANGER_RED,
            hover_color=COLOR_DANGER_HOVER, width=100,
            font=ctk.CTkFont(weight="bold"), command=self.logout
        ).pack(side="right", padx=20, pady=12)

        self.tabview = ctk.CTkTabview(
            self, width=1120, height=680,
            segmented_button_selected_color=COLOR_PRIMARY_BLUE,
            segmented_button_selected_hover_color=COLOR_HOVER_BLUE,
            segmented_button_font=ctk.CTkFont(size=15, weight="bold")
        )
        self.tabview._segmented_button.configure(height=40)
        self.tabview.pack(pady=8, padx=22, fill="both", expand=True)
        self.tab_add = self.tabview.add("Add Product")
        self.tab_view = self.tabview.add("Inventory")
        self.tab_report = self.tabview.add("Reports")

        ctk.CTkLabel(
            self.tab_add, text="Add a product", font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(anchor="w", padx=24, pady=(22, 3))
        ctk.CTkLabel(
            self.tab_add, text="Enter the product details below. All fields are required.",
            text_color=COLOR_TEXT_SUBTLE
        ).pack(anchor="w", padx=24, pady=(0, 14))

        add_card = ctk.CTkFrame(self.tab_add, fg_color=COLOR_CARD_BG, corner_radius=12)
        add_card.pack(anchor="n", padx=24, pady=5, fill="x")
        add_card.grid_columnconfigure(0, weight=1, uniform="product_fields")
        add_card.grid_columnconfigure(1, weight=1, uniform="product_fields")
        ctk.CTkLabel(add_card, text="Product name", text_color=COLOR_TEXT_SUBTLE).grid(
            row=0, column=0, sticky="w", padx=(22, 12), pady=(20, 4)
        )
        ctk.CTkLabel(add_card, text="Category", text_color=COLOR_TEXT_SUBTLE).grid(
            row=0, column=1, sticky="w", padx=(12, 22), pady=(20, 4)
        )
        self.entry_name = ctk.CTkEntry(
            add_card, placeholder_text="e.g. Arabica Coffee", height=40,
            border_color=COLOR_PRIMARY_BLUE
        )
        self.entry_name.grid(row=1, column=0, sticky="ew", padx=(22, 12), pady=(0, 16))
        self.entry_category = ctk.CTkEntry(
            add_card, placeholder_text="e.g. Beverages", height=40,
            border_color=COLOR_PRIMARY_BLUE
        )
        self.entry_category.grid(row=1, column=1, sticky="ew", padx=(12, 22), pady=(0, 16))
        ctk.CTkLabel(add_card, text="Price (PHP)", text_color=COLOR_TEXT_SUBTLE).grid(
            row=2, column=0, sticky="w", padx=(22, 12), pady=(0, 4)
        )
        ctk.CTkLabel(add_card, text="Quantity in stock", text_color=COLOR_TEXT_SUBTLE).grid(
            row=2, column=1, sticky="w", padx=(12, 22), pady=(0, 4)
        )
        self.entry_price = ctk.CTkEntry(
            add_card, placeholder_text="e.g. 99.50", height=40,
            border_color=COLOR_PRIMARY_BLUE
        )
        self.entry_price.grid(row=3, column=0, sticky="ew", padx=(22, 12), pady=(0, 20))
        self.entry_qty = ctk.CTkEntry(
            add_card, placeholder_text="e.g. 25", height=40,
            border_color=COLOR_PRIMARY_BLUE
        )
        self.entry_qty.grid(row=3, column=1, sticky="ew", padx=(12, 22), pady=(0, 20))
        self.btn_add = ctk.CTkButton(
            add_card, text="Save product", height=40, width=180,
            fg_color=COLOR_PRIMARY_BLUE, hover_color=COLOR_HOVER_BLUE,
            font=ctk.CTkFont(weight="bold"), command=self.add_product
        )
        self.btn_add.grid(row=4, column=0, columnspan=2, pady=(0, 22))

        stats_frame = ctk.CTkFrame(self.tab_view, fg_color="transparent")
        stats_frame.pack(fill="x", padx=12, pady=(12, 8))
        stat_specs = [
            ("Products", "0", "Unique items", "#42A5F5"),
            ("Units in stock", "0", "Across all products", "#66BB6A"),
            ("Low stock", "0", "5 units or fewer", "#FFB74D"),
            ("Inventory value", "PHP 0.00", "Based on current stock", "#BA68C8"),
        ]
        self.stat_values = []
        for index, (title, value, detail, accent) in enumerate(stat_specs):
            stats_frame.grid_columnconfigure(index, weight=1, uniform="stats")
            card = ctk.CTkFrame(stats_frame, fg_color=COLOR_CARD_BG, corner_radius=10)
            card.grid(row=0, column=index, sticky="ew", padx=5)
            ctk.CTkLabel(card, text=title, text_color=COLOR_TEXT_SUBTLE).pack(
                anchor="w", padx=14, pady=(11, 1)
            )
            value_label = ctk.CTkLabel(
                card, text=value, text_color=accent,
                font=ctk.CTkFont(size=20, weight="bold")
            )
            value_label.pack(anchor="w", padx=14)
            ctk.CTkLabel(card, text=detail, text_color=COLOR_TEXT_SUBTLE).pack(
                anchor="w", padx=14, pady=(1, 11)
            )
            self.stat_values.append(value_label)

        self.top_bar = ctk.CTkFrame(self.tab_view, fg_color="transparent")
        self.top_bar.pack(pady=(5, 8), padx=16, fill="x")
        ctk.CTkLabel(
            self.top_bar, text="Products", font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left", padx=(0, 14))
        self.search_entry = ctk.CTkEntry(
            self.top_bar, placeholder_text="Search by product name or category...",
            height=36, border_color=COLOR_PRIMARY_BLUE
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", self.schedule_search)
        ctk.CTkButton(
            self.top_bar, text="Clear", width=72, height=36,
            fg_color="#455A64", hover_color="#37474F", command=self.clear_search
        ).pack(side="left", padx=(8, 0))
        ctk.CTkButton(
            self.top_bar, text="Refresh", width=86, height=36, command=self.load_data
        ).pack(side="left", padx=(8, 0))
        self.btn_edit_selected = ctk.CTkButton(
            self.top_bar, text="Edit selected", width=112, height=36,
            state="disabled", command=self.edit_selected
        )
        self.btn_edit_selected.pack(side="left", padx=(8, 0))
        self.btn_delete_selected = ctk.CTkButton(
            self.top_bar, text="Delete selected", width=124, height=36,
            fg_color=COLOR_DANGER_RED, hover_color=COLOR_DANGER_HOVER,
            state="disabled", command=self.delete_selected
        )
        self.btn_delete_selected.pack(side="left", padx=(8, 0))
        self.lbl_stats = ctk.CTkLabel(self.tab_view, text="", text_color=COLOR_TEXT_SUBTLE)
        self.lbl_stats.pack(anchor="w", padx=22, pady=(0, 3))
        table_frame = ctk.CTkFrame(self.tab_view, fg_color=COLOR_CARD_BG, corner_radius=10)
        table_frame.pack(pady=(2, 12), padx=16, fill="both", expand=True)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Inventory.Treeview", background="#252525", fieldbackground="#252525",
            foreground=COLOR_TEXT_WHITE, rowheight=32, borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Inventory.Treeview.Heading", background="#343434", foreground=COLOR_TEXT_WHITE,
            relief="flat", padding=(8, 8), font=("Segoe UI", 10, "bold")
        )
        style.map(
            "Inventory.Treeview", background=[("selected", COLOR_PRIMARY_BLUE)],
            foreground=[("selected", "#FFFFFF")]
        )
        columns = ("number", "name", "category", "price", "quantity", "status")
        self.product_table = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse",
            style="Inventory.Treeview"
        )
        column_specs = (
            ("number", "ID", 55, False), ("name", "Product name", 250, True),
            ("category", "Category", 160, True), ("price", "Price", 125, False),
            ("quantity", "Stock", 90, False), ("status", "Status", 110, False),
        )
        for column, heading, width, stretch in column_specs:
            self.product_table.heading(column, text=heading)
            self.product_table.column(column, width=width, minwidth=width, stretch=stretch)
        self.product_table.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.product_table.yview)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=10)
        self.product_table.configure(yscrollcommand=scrollbar.set)
        self.product_table.tag_configure("low_stock", foreground="#FF8A80")
        self.product_table.tag_configure("alternate", background="#2B2B2B")
        self.product_table.bind("<<TreeviewSelect>>", self.on_product_selected)

        report_card = ctk.CTkFrame(self.tab_report, fg_color=COLOR_CARD_BG, corner_radius=12)
        report_card.pack(anchor="n", fill="x", padx=24, pady=24)
        ctk.CTkLabel(
            report_card, text="Inventory report", font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(anchor="w", padx=22, pady=(20, 4))
        ctk.CTkLabel(
            report_card, text="Export all products, prices, and stock quantities to a PDF report.",
            text_color=COLOR_TEXT_SUBTLE
        ).pack(anchor="w", padx=22, pady=(0, 12))
        self.btn_pdf = ctk.CTkButton(
            report_card, text="Export PDF", fg_color="#2E7D32", hover_color="#1B5E20",
            font=ctk.CTkFont(weight="bold"), command=self.generate_pdf, width=160, height=38
        )
        self.btn_pdf.pack(anchor="w", padx=22, pady=(0, 20))
        self.tabview.set("Inventory")

    def logout(self):
        confirm = messagebox.askyesno("Log Out", "Are you sure you want to log out?")
        if confirm:
            database.log_activity(self.username, "User Logged Out")
            self.after(120, self._finish_logout)

    def _finish_logout(self):
        self.destroy()
        self.login_window.deiconify()

    def close_app(self):
        self.login_window.destroy()

    def add_product(self):
        name = self.entry_name.get().strip()
        category = self.entry_category.get().strip()
        price_text = self.entry_price.get().strip()
        quantity_text = self.entry_qty.get().strip()

        if not all((name, category, price_text, quantity_text)):
            messagebox.showwarning("Missing information", "Please complete all product fields.")
            return

        try:
            price = float(price_text)
            quantity = int(quantity_text)
            if price < 0 or quantity < 0:
                messagebox.showwarning("Invalid values", "Price and quantity cannot be negative.")
                return
        except ValueError:
            messagebox.showerror(
                "Invalid values",
                "Enter a valid number for price and a whole number for quantity."
            )
            return

        database.add_product(name, category, price, quantity)
        database.log_activity(self.username, f"Added Product '{name}'")
        messagebox.showinfo("Product saved", f"{name} was added to your inventory.")
        self.clear_entries()
        self.load_data()
        self.tabview.set("Inventory")

    def clear_entries(self):
        self.entry_name.delete(0, 'end')
        self.entry_category.delete(0, 'end')
        self.entry_price.delete(0, 'end')
        self.entry_qty.delete(0, 'end')

    def schedule_search(self, _event=None):
        if self._search_after_id is not None:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(250, self._run_search)

    def _run_search(self):
        self._search_after_id = None
        self.load_data(refresh=False)

    def clear_search(self):
        if self._search_after_id is not None:
            self.after_cancel(self._search_after_id)
            self._search_after_id = None
        self.search_entry.delete(0, "end")
        self.load_data(refresh=False)

    def on_product_selected(self, _event=None):
        selected = bool(self.product_table.selection())
        state = "normal" if selected else "disabled"
        self.btn_edit_selected.configure(state=state)
        self.btn_delete_selected.configure(state=state)

    def edit_selected(self):
        selected = self.product_table.selection()
        if not selected:
            return
        item = self.product_by_id.get(int(selected[0]))
        if item:
            UpdateStockWindow(self, item, self.load_data, self.username)

    def delete_selected(self):
        selected = self.product_table.selection()
        if not selected:
            return
        item = self.product_by_id.get(int(selected[0]))
        if item:
            self.delete_item(item[0], item[1])

    def load_data(self, refresh=True):
        if refresh:
            self.all_products = sorted(database.fetch_products(), key=lambda item: item[0])
        self.product_by_id = {item[0]: item for item in self.all_products}

        query = self.search_entry.get().strip().casefold()
        if query:
            records = [
                item for item in self.all_products
                if query in item[1].casefold() or query in item[2].casefold()
            ]
        else:
            records = self.all_products

        total_qty = sum(item[4] for item in self.all_products)
        total_value = sum(item[3] * item[4] for item in self.all_products)
        low_stock_count = sum(1 for item in self.all_products if item[4] <= 5)
        self.stat_values[0].configure(text=f"{len(self.all_products):,}")
        self.stat_values[1].configure(text=f"{total_qty:,}")
        self.stat_values[2].configure(text=f"{low_stock_count:,}")
        self.stat_values[3].configure(text=f"PHP {total_value:,.2f}")
        if not records and query:
            self.lbl_stats.configure(text="No products match your search.")
        elif not records:
            self.lbl_stats.configure(text="No products yet. Add your first product to get started.")
        else:
            self.lbl_stats.configure(
                text=f"Showing {len(records):,} of {len(self.all_products):,} products"
            )

        current_rows = self.product_table.get_children()
        if current_rows:
            self.product_table.delete(*current_rows)
        for row_number, item in enumerate(records, start=1):
            quantity = item[4]
            status = "Low stock" if quantity <= 5 else "In stock"
            tags = ("low_stock",) if quantity <= 5 else (
                ("alternate",) if row_number % 2 == 0 else ()
            )
            self.product_table.insert(
                "", "end", iid=str(item[0]),
                values=(
                    row_number, item[1], item[2], f"PHP {item[3]:,.2f}",
                    f"{quantity:,}", status
                ),
                tags=tags
            )
        self.on_product_selected()

    def delete_item(self, product_id, product_name):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{product_name}'?")
        if confirm:
            self.after(120, lambda: self._finish_delete(product_id, product_name))

    def _finish_delete(self, product_id, product_name):
        database.delete_product(product_id)
        database.log_activity(self.username, f"Deleted Product ID {product_id} ({product_name})")
        self.load_data()

    def generate_pdf(self):
        records = database.fetch_products()
        if not records:
            messagebox.showwarning("No Products", "There are no products to export.")
            return

        filename = f"Inventory_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        
        c.setFont("Helvetica-Bold", 18)
        c.drawString(180, 750, "SmartStock Inventory Report")
        
        c.setFont("Helvetica", 10)
        c.drawString(50, 730, f"Date Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | By: {self.username}")
        c.line(50, 720, 550, 720)

        y = 690
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "ID")
        c.drawString(90, y, "Name")
        c.drawString(220, y, "Category")
        c.drawString(340, y, "Price (PHP)")
        c.drawString(440, y, "Quantity")

        y -= 20
        c.setFont("Helvetica", 10)
        for item in records:
            if y < 50:
                c.showPage()
                y = 750
            c.drawString(50, y, str(item[0]))
            c.drawString(90, y, str(item[1]))
            c.drawString(220, y, str(item[2]))
            c.drawString(340, y, f"{item[3]:.2f}")
            c.drawString(440, y, str(item[4]))
            y -= 18

        c.save()
        database.log_activity(self.username, f"Exported PDF Report: {filename}")
        messagebox.showinfo("Export Successful", "The PDF report was saved and opened.")
        os.startfile(filename)

if __name__ == "__main__":
    login_app = LoginWindow()
    login_app.mainloop()
