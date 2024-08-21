import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector

class StoreManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stor   e Management System")
        self.root.geometry("800x600")

        # Notebook for tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=1)

        # Role selection frame
        self.role_frame = tk.Frame(self.notebook)
        self.notebook.add(self.role_frame, text="Login")

        self.role_label = tk.Label(self.role_frame, text="Select Role:")
        self.role_label.pack(pady=10)

        self.role_var = tk.StringVar()
        self.role_var.set("Admin")

        self.admin_radio = tk.Radiobutton(self.role_frame, text="Admin", variable=self.role_var, value="Admin")
        self.admin_radio.pack()

        self.employee_radio = tk.Radiobutton(self.role_frame, text="Employee", variable=self.role_var, value="Employee")
        self.employee_radio.pack()

        self.role_button = tk.Button(self.role_frame, text="Continue", command=self.load_login)
        self.role_button.pack(pady=10)

        # Database connection
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="Root@123",
            database="dbms_project"
        )
        self.cursor = self.db.cursor()
        self.failed_login_attempts = 0

    def load_login(self):
        self.role_frame.pack_forget()

        # Login frame
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(fill=tk.BOTH, expand=1)

        self.username_label = tk.Label(self.login_frame, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack()
        self.password_label = tk.Label(self.login_frame, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.pack()
        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        if role == "Admin":
            query = "SELECT * FROM login WHERE username=%s AND login_password=%s AND user_id IN (SELECT user_id FROM roles WHERE role_name = 'Admin')"
        else:
            query = "SELECT * FROM login WHERE username=%s AND login_password=%s AND user_id IN (SELECT user_id FROM roles WHERE role_name = 'Employee')"

        self.cursor.execute(query, (username, password))
        user = self.cursor.fetchone()
        if user:
            self.failed_login_attempts = 0  # Reset failed login attempts
            self.load_main_page()
            self.login_frame.pack_forget()  # Forget the login frame after successful login
        else:
            self.failed_login_attempts += 1
            if self.failed_login_attempts >= 3:
                self.load_main_page(restrict_customer_tab=True, restrict_bills_tab=True)
            else:
                messagebox.showerror("Login", "Invalid username or password")

    def load_main_page(self, restrict_customer_tab=False, restrict_bills_tab=False):
        # Customers tab
        self.customers_frame = tk.Frame(self.notebook)
        if not restrict_customer_tab:
            self.notebook.add(self.customers_frame, text="Customers")
            if self.role_var.get() == "Admin":
                # Display both mobile number columns for the Admin
                self.customers_table = ttk.Treeview(self.customers_frame, columns=('Name', 'Mobile 1', 'Mobile 2'))
                self.customers_table.heading('#0', text='CUSTOMER ID')
                self.customers_table.heading('Name', text='NAME')
                self.customers_table.heading('Mobile 1', text='Mobile NUMBER')
                self.customers_table.heading('Mobile 2', text='Mobile NUMBER 2')
                self.customers_table.pack(fill=tk.BOTH, expand=1)
            else:
                # Display only the name column for the Employee
                self.customers_table = ttk.Treeview(self.customers_frame, columns=('Name',))
                self.customers_table.heading('#0', text='CUSTOMER ID')
                self.customers_table.heading('Name', text='NAME')
                self.customers_table.pack(fill=tk.BOTH, expand=1)
            self.load_customers()

        # Products tab and other tabs remain the same
        self.products_frame = tk.Frame(self.notebook)
        self.notebook.add(self.products_frame, text="Products")
        self.products_table = ttk.Treeview(self.products_frame,
                                           columns=('Name', 'Number', 'Type', 'Amount'))  # Added 'Amount' column
        self.products_table.heading('#0', text='ID')
        self.products_table.heading('Name', text='Name')
        self.products_table.heading('Number', text='Number')
        self.products_table.heading('Type', text='Type')
        self.products_table.heading('Amount', text='Amount')  # Heading for Amount column
        self.products_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.load_products()

        if self.role_var.get() == "Admin":
            # Add edit button for Admin
            self.edit_product_button = tk.Button(self.products_frame, text="Edit Selected Product",
                                                 command=self.edit_product)
            self.edit_product_button.pack(side=tk.BOTTOM, pady=5)

        # Cart tab
        self.cart_frame = tk.Frame(self.notebook)
        self.notebook.add(self.cart_frame, text="Cart")
        self.cart_table = ttk.Treeview(self.cart_frame, columns=('Name', 'Amount'))  # Added 'Amount' column for Cart
        self.cart_table.heading('#0', text='ID')
        self.cart_table.heading('Name', text='Name')
        self.cart_table.heading('Amount', text='Amount')
        self.cart_table.pack(fill=tk.BOTH, expand=1)
        self.total_label = tk.Label(self.cart_frame, text="Total: $0.00")
        self.total_label.pack(side=tk.BOTTOM)

        # Add a Buy button to the cart tab
        self.buy_button = tk.Button(self.cart_frame, text="Buy", command=self.generate_bill)
        self.buy_button.pack(side=tk.BOTTOM, pady=5)

        if self.role_var.get() == "Admin":
            # Bills tab
            self.bills_frame = tk.Frame(self.notebook)
            if not restrict_bills_tab:
                self.notebook.add(self.bills_frame, text="Bills")
                self.bills_table = ttk.Treeview(self.bills_frame, columns=('ID', 'Amount', 'Date', 'Customer ID'))
                self.bills_table.heading('#0', text='Bill ID')
                self.bills_table.heading('ID', text='ID')
                self.bills_table.heading('Amount', text='Customer ID')
                self.bills_table.heading('Date', text='Amount')
                self.bills_table.heading('Customer ID', text='Date')
                self.bills_table.pack(fill=tk.BOTH, expand=1)
                self.load_bills()

        # Remove login tab
        self.notebook.forget(0)

        # Add to Cart button
        self.add_to_cart_button = tk.Button(self.products_frame, text="Add Selected to Cart",
                                            command=self.add_selected_to_cart)
        self.add_to_cart_button.pack(side=tk.BOTTOM, pady=5)

        # Add Customer button
        if self.role_var.get() == "Admin" or not restrict_customer_tab:
            self.add_customer_button = tk.Button(self.customers_frame, text="Add Customer", command=self.add_customer)
            self.add_customer_button.pack(side=tk.BOTTOM, pady=5)

    def load_customers(self):
        self.cursor.execute("SELECT * FROM customer")
        customers = self.cursor.fetchall()
        for customer in customers:
            self.customers_table.insert('', 'end', text=customer[1], values=(customer[2], customer[3], customer[4]))

    def add_customer(self):
        add_customer_window = tk.Toplevel(self.root)
        add_customer_window.title("Add Customer")

        name_label = tk.Label(add_customer_window, text="Name:")
        name_label.grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(add_customer_window)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        mobile_label = tk.Label(add_customer_window, text="Mobile:")
        mobile_label.grid(row=1, column=0, padx=5, pady=5)
        self.mobile_entry = tk.Entry(add_customer_window)
        self.mobile_entry.grid(row=1, column=1, padx=5, pady=5)

        add_button = tk.Button(add_customer_window, text="Add", command=self.save_customer)
        add_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def save_customer(self):
        name = self.name_entry.get()
        mobile = self.mobile_entry.get()

        if not name or not mobile:
            messagebox.showerror("Add Customer", "Please enter Name and Mobile.")
            return

        # Insert customer details into the database
        self.cursor.execute("INSERT INTO customer (cus_name, mobile) VALUES (%s, %s)", (name, mobile))
        self.db.commit()

        # Refresh the customers table
        self.customers_table.delete(*self.customers_table.get_children())
        self.load_customers()

        # Close the add customer window
        self.root.focus_set()
        messagebox.showinfo("Add Customer", "Customer added successfully.")

    def load_products(self):
        self.cursor.execute("SELECT * FROM product")
        products = self.cursor.fetchall()
        for product in products:
            if len(product) >= 6:  # Ensure that the product tuple has at least 6 elements
                product_id = product[0]
                self.products_table.insert('', 'end', text=product_id, values=(product[1], product[2], product[3], product[5]))  # Product prices at index 5
            else:
                print("Incomplete product data:", product)

    def add_selected_to_cart(self):
        selected_item = self.products_table.focus()
        if not selected_item:
            messagebox.showerror("Add to Cart", "Please select a product.")
            return

        product_id = self.products_table.item(selected_item)['text']
        self.cursor.execute("SELECT * FROM product WHERE prod_id = %s", (product_id,))
        product = self.cursor.fetchone()
        self.cart_table.insert('', 'end', text=product[0], values=(product[1], product[5]))
        self.update_total()
        messagebox.showinfo("Add to Cart", "Product added to cart successfully.")

    def generate_bill(self):
        if not self.cart_table.get_children():
            messagebox.showerror("Generate Bill", "Your cart is empty.")
            return

        # Open a window to enter user ID, customer ID, and bill date
        bill_info_window = tk.Toplevel(self.root)
        bill_info_window.title("Bill Information")

        user_id_label = tk.Label(bill_info_window, text="User ID:")
        user_id_label.grid(row=0, column=0, padx=5, pady=5)
        self.user_id_entry = tk.Entry(bill_info_window)
        self.user_id_entry.grid(row=0, column=1, padx=5, pady=5)

        cus_id_label = tk.Label(bill_info_window, text="Customer ID:")
        cus_id_label.grid(row=1, column=0, padx=5, pady=5)
        self.cus_id_entry = tk.Entry(bill_info_window)
        self.cus_id_entry.grid(row=1, column=1, padx=5, pady=5)

        date_label = tk.Label(bill_info_window, text="Date (YYYY-MM-DD):")
        date_label.grid(row=2, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(bill_info_window)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        confirm_button = ttk.Button(bill_info_window, text="Confirm", command=self.confirm_bill)
        confirm_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def confirm_bill(self):
        user_id = self.user_id_entry.get()
        cus_id = self.cus_id_entry.get()
        date = self.date_entry.get()

        if not user_id or not cus_id or not date:
            messagebox.showerror("Confirm Bill", "Please enter User ID, Customer ID, and Date.")
            return

        # Calculate total amount
        total_amount = sum(float(self.cart_table.item(item, 'values')[1]) for item in self.cart_table.get_children())

        # Insert bill details into the database
        self.cursor.execute("INSERT INTO bill (user_id, cus_id, bill_amount, bill_date) VALUES (%s, %s, %s, %s)",
                            (user_id, cus_id, total_amount, date))
        self.db.commit()

        # Get the last inserted bill ID
        bill_id = self.cursor.lastrowid

        # Insert bill details into the bill table
        self.bills_table.insert('', 'end', values=(bill_id, user_id, total_amount, date, cus_id))

        # Clear cart
        self.cart_table.delete(*self.cart_table.get_children())
        self.update_total()

        # Close bill info window
        self.root.focus_set()

        messagebox.showinfo("Confirm Bill", "Bill confirmed and added to the database.")

    def load_bills(self):
        self.bills_table.delete(*self.bills_table.get_children())
        self.cursor.execute("SELECT * FROM bill")
        bills = self.cursor.fetchall()
        for bill in bills:
            # Fetch the corresponding customer ID and name from the customer table
            self.cursor.execute("SELECT cus_id, cus_name FROM customer WHERE cus_id = %s", (bill[2],))
            customer = self.cursor.fetchone()
            if customer:
                cus_id = customer[0]
                cus_name = customer[1]
            else:
                cus_id = "Unknown"
                cus_name = "Unknown"

            self.bills_table.insert('', 'end', values=(bill[0], bill[1], bill[4], bill[3], cus_id))

    def update_total(self):
        total_amount = sum(float(self.cart_table.item(item, 'values')[1]) for item in self.cart_table.get_children())
        self.total_label.config(text=f"Total: ${total_amount:.2f}")

    def edit_product(self):
        selected_item = self.products_table.focus()
        if not selected_item:
            messagebox.showerror("Edit Product", "Please select a product to edit.")
            return

        product_id = self.products_table.item(selected_item)['text']
        edit_window = tk.Toplevel()
        edit_window.title("Edit Product")

        # Fetching current product details
        self.cursor.execute("SELECT * FROM product WHERE prod_id = %s", (product_id,))
        product = self.cursor.fetchone()

        # Labels and Entry widgets for editing product details
        name_label = tk.Label(edit_window, text="Name:")
        name_label.grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(edit_window)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.insert(0, product[1])

        number_label = tk.Label(edit_window, text="Number:")
        number_label.grid(row=1, column=0, padx=5, pady=5)
        self.number_entry = tk.Entry(edit_window)
        self.number_entry.grid(row=1, column=1, padx=5, pady=5)
        self.number_entry.insert(0, product[2])

        type_label = tk.Label(edit_window, text="Type:")
        type_label.grid(row=2, column=0, padx=5, pady=5)
        self.type_entry = tk.Entry(edit_window)
        self.type_entry.grid(row=2, column=1, padx=5, pady=5)
        self.type_entry.insert(0, product[3])

        save_button = ttk.Button(edit_window, text="Save", command=lambda: self.save_product(edit_window, product_id))
        save_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def save_product(self, edit_window, product_id):
        name = self.name_entry.get()
        number = self.number_entry.get()
        type = self.type_entry.get()

        # Update product details in the database
        self.cursor.execute("UPDATE product SET product_name = %s, product_number = %s, product_type = %s WHERE prod_id = %s",
                            (name, number, type, product_id))
        self.db.commit()

        # Close the edit window
        edit_window.destroy()

        # Refresh the products table
        self.products_table.delete(*self.products_table.get_children())
        self.load_products()
        messagebox.showinfo("Edit Product", "Product details updated successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = StoreManagementApp(root)
    root.mainloop()
