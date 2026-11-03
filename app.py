import customtkinter as ctk
from tkinter import messagebox
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
            self.destroy()
            app = SmartStockApp(username, role)
            app.mainloop()
        else:
            messagebox.showerror("Login Failed", "Maling Username o Password!")

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
            self.refresh_callback()
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid inputs!")

class SmartStockApp(ctk.CTk):
    def __init__(self, username, role):
        super().__init__()

        self.username = username
        self.role = role

        self.title(f"SmartStock - Inventory System | User: {self.username} ({self.role})")
        self.geometry("980x700")

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # --- TOP HEADER BAR ---
        self.header_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=10)
        self.header_frame.pack(pady=(15, 5), padx=20, fill="x")

        # System Title with Symbol
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text=f"📦 SmartStock Dashboard ({self.role})", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLOR_TEXT_WHITE
        )
        self.title_label.pack(side="left", padx=20, pady=12)

        # RED LOG OUT BUTTON WITH SYMBOL
        self.btn_logout = ctk.CTkButton(
            self.header_frame, 
            text="🚪 Log Out", 
            fg_color=COLOR_DANGER_RED, 
            hover_color=COLOR_DANGER_HOVER, 
            width=100, 
            font=ctk.CTkFont(weight="bold"), 
            command=self.logout
        )
        self.btn_logout.pack(side="right", padx=20, pady=12)

        # --- TABVIEW MENU ---
        self.tabview = ctk.CTkTabview(
            self, 
            width=940, 
            height=580, 
            segmented_button_selected_color=COLOR_PRIMARY_BLUE, 
            segmented_button_selected_hover_color=COLOR_HOVER_BLUE
        )
        self.tabview.pack(pady=10, padx=20, fill="both", expand=True)

        self.tab_add = self.tabview.add("➕ Add Product")
        self.tab_view = self.tabview.add("👁️ View & Search")
        self.tab_report = self.tabview.add("📊 Reports & PDF")

        # --- TAB 1: ADD PRODUCT ---
        add_card = ctk.CTkFrame(self.tab_add, fg_color=COLOR_CARD_BG, corner_radius=12, width=520)
        add_card.pack(pady=30, padx=20)

        ctk.CTkLabel(
            add_card, 
            text="➕ Register New Product", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(pady=15)

        self.entry_name = ctk.CTkEntry(add_card, placeholder_text="🏷️ Product Name", width=320, border_color=COLOR_PRIMARY_BLUE)
        self.entry_name.pack(pady=8, padx=25)

        self.entry_category = ctk.CTkEntry(add_card, placeholder_text="📁 Category", width=320, border_color=COLOR_PRIMARY_BLUE)
        self.entry_category.pack(pady=8, padx=25)

        self.entry_price = ctk.CTkEntry(add_card, placeholder_text="₱ Price (PHP)", width=320, border_color=COLOR_PRIMARY_BLUE)
        self.entry_price.pack(pady=8, padx=25)

        self.entry_qty = ctk.CTkEntry(add_card, placeholder_text="🔢 Quantity", width=320, border_color=COLOR_PRIMARY_BLUE)
        self.entry_qty.pack(pady=8, padx=25)

        self.btn_add = ctk.CTkButton(
            add_card, 
            text="💾 Save Product Entry", 
            width=220, 
            fg_color=COLOR_PRIMARY_BLUE, 
            hover_color=COLOR_HOVER_BLUE, 
            font=ctk.CTkFont(weight="bold"), 
            command=self.add_product
        )
        self.btn_add.pack(pady=20)

        # --- TAB 2: VIEW, SEARCH, UPDATE & DELETE ---
        self.top_bar = ctk.CTkFrame(self.tab_view, fg_color="transparent")
        self.top_bar.pack(pady=10, padx=10, fill="x")

        self.search_entry = ctk.CTkEntry(
            self.top_bar, 
            placeholder_text="🔍 Search Name or Category...", 
            width=300, 
            border_color=COLOR_PRIMARY_BLUE
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_data())

        self.lbl_stats = ctk.CTkLabel(
            self.top_bar, 
            text="Total Items: 0 | Total Value: ₱0.00", 
            font=ctk.CTkFont(weight="bold"), 
            text_color=COLOR_TEXT_WHITE
        )
        self.lbl_stats.pack(side="right")

        # Table Display Frame
        self.display_frame = ctk.CTkScrollableFrame(self.tab_view, width=880, height=390, fg_color=COLOR_CARD_BG)
        self.display_frame.pack(pady=5, padx=10, fill="both", expand=True)

        # --- TAB 3: REPORTS ---
        report_card = ctk.CTkFrame(self.tab_report, fg_color=COLOR_CARD_BG, corner_radius=12, width=520)
        report_card.pack(pady=40, padx=20)

        ctk.CTkLabel(
            report_card, 
            text="📊 Export Inventory Report", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT_WHITE
        ).pack(pady=15)

        ctk.CTkLabel(
            report_card, 
            text="Generate and download complete product stock summaries formatted into an official PDF document.", 
            wraplength=360, 
            text_color=COLOR_TEXT_SUBTLE
        ).pack(pady=5)

        self.btn_pdf = ctk.CTkButton(
            report_card, 
            text="📄 Export PDF Report", 
            fg_color="#2E7D32", 
            hover_color="#1B5E20", 
            font=ctk.CTkFont(weight="bold"), 
            command=self.generate_pdf, 
            width=220
        )
        self.btn_pdf.pack(pady=25)

    def logout(self):
        confirm = messagebox.askyesno("Log Out", "Sigurado ka bang gusto mong mag-log out?")
        if confirm:
            database.log_activity(self.username, "User Logged Out")
            self.destroy()
            login = LoginWindow()
            login.mainloop()

    def add_product(self):
        name = self.entry_name.get()
        category = self.entry_category.get()
        price = self.entry_price.get()
        quantity = self.entry_qty.get()

        if not name or not category or not price or not quantity:
            messagebox.showwarning("Input Error", "Paki-punan ang lahat ng field!")
            return

        try:
            database.add_product(name, category, float(price), int(quantity))
            database.log_activity(self.username, f"Added Product '{name}'")
            messagebox.showinfo("Success", f"Matagumpay na naidagdag ang '{name}'!")
            self.clear_entries()
            self.load_data()
            self.tabview.set("👁️ View & Search")
        except ValueError:
            messagebox.showerror("Format Error", "Ang Price at Quantity ay dapat numero!")

    def clear_entries(self):
        self.entry_name.delete(0, 'end')
        self.entry_category.delete(0, 'end')
        self.entry_price.delete(0, 'end')
        self.entry_qty.delete(0, 'end')

    def load_data(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        query = self.search_entry.get()
        records = database.fetch_products(query)

        total_qty = sum(r[4] for r in records)
        total_val = sum(r[3] * r[4] for r in records)
        self.lbl_stats.configure(text=f"Total Items: {total_qty} | Total Value: ₱{total_val:,.2f}")

        headers = ["ID", "Name", "Category", "Price", "Qty", "Status", "Actions"]
        for col_idx, text in enumerate(headers):
            lbl = ctk.CTkLabel(self.display_frame, text=text, font=ctk.CTkFont(weight="bold"), text_color=COLOR_TEXT_SUBTLE)
            lbl.grid(row=0, column=col_idx, padx=12, pady=8)

        for row_idx, item in enumerate(records, start=1):
            qty = item[4]
            status_text = "⚠️ LOW STOCK" if qty < 5 else "✅ OK"
            status_color = "#FF5252" if qty < 5 else "#66BB6A"

            ctk.CTkLabel(self.display_frame, text=str(item[0]), text_color=COLOR_TEXT_WHITE).grid(row=row_idx, column=0, padx=12, pady=4)
            ctk.CTkLabel(self.display_frame, text=item[1], text_color=COLOR_TEXT_WHITE).grid(row=row_idx, column=1, padx=12, pady=4)
            ctk.CTkLabel(self.display_frame, text=item[2], text_color=COLOR_TEXT_WHITE).grid(row=row_idx, column=2, padx=12, pady=4)
            ctk.CTkLabel(self.display_frame, text=f"₱{item[3]:.2f}", text_color=COLOR_TEXT_WHITE).grid(row=row_idx, column=3, padx=12, pady=4)
            ctk.CTkLabel(self.display_frame, text=str(qty), text_color=COLOR_TEXT_WHITE).grid(row=row_idx, column=4, padx=12, pady=4)
            
            lbl_status = ctk.CTkLabel(self.display_frame, text=status_text, text_color=status_color, font=ctk.CTkFont(weight="bold"))
            lbl_status.grid(row=row_idx, column=5, padx=12, pady=4)

            btn_frame = ctk.CTkFrame(self.display_frame, fg_color="transparent")
            btn_frame.grid(row=row_idx, column=6, padx=5, pady=4)

            update_btn = ctk.CTkButton(
                btn_frame, 
                text="✏️ Update", 
                width=85, 
                fg_color=COLOR_PRIMARY_BLUE, 
                hover_color=COLOR_HOVER_BLUE, 
                command=lambda itm=item: UpdateStockWindow(self, itm, self.load_data, self.username)
            )
            update_btn.pack(side="left", padx=2)

            del_btn = ctk.CTkButton(
                btn_frame, 
                text="🗑️ Delete", 
                fg_color=COLOR_DANGER_RED, 
                hover_color=COLOR_DANGER_HOVER, 
                width=70, 
                command=lambda pid=item[0], pname=item[1]: self.delete_item(pid, pname)
            )
            del_btn.pack(side="left", padx=2)

    def delete_item(self, product_id, product_name):
        confirm = messagebox.askyesno("Confirm Delete", f"Sigurado ka bang gusto mong idelete ang '{product_name}'?")
        if confirm:
            database.delete_product(product_id)
            database.log_activity(self.username, f"Deleted Product ID {product_id} ({product_name})")
            self.load_data()

    def generate_pdf(self):
        records = database.fetch_products()
        if not records:
            messagebox.showwarning("Warning", "Walang laman ang database para i-export!")
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
        messagebox.showinfo("Export Successful", f"Na-save at binubuksan ang PDF Report!")
        os.startfile(filename)

if __name__ == "__main__":
    login_app = LoginWindow()
    login_app.mainloop()