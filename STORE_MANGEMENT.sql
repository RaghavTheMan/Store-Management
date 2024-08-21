create database dbms_project;
use dbms_project;
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    user_email VARCHAR(100)
);
CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(255) NOT NULL,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) -- Assuming there's a table named 'users' with a 'user_id' column
);
CREATE TABLE bill (
    user_id INT,
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_date DATE,
    bill_cus_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
alter table bill add column (bill_amount int);
CREATE TABLE login (
    login_id INT AUTO_INCREMENT PRIMARY KEY,
    login_password VARCHAR(255) NOT NULL,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) -- Assuming there's a table named 'users' with a 'user_id' column
);
CREATE TABLE permission (
    per_id INT AUTO_INCREMENT PRIMARY KEY,
    per_name VARCHAR(255) NOT NULL,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) -- Assuming there's a table named 'users' with a 'user_id' column
);
CREATE TABLE customer (
    user_id INT,
    cus_id INT AUTO_INCREMENT PRIMARY KEY,
    cus_name VARCHAR(255),
    cus_mobile1 VARCHAR(15),
    cus_mobile2 VARCHAR(15),
    FOREIGN KEY (user_id) REFERENCES users(user_id) -- Assuming there's a table named 'users' with a 'user_id' column
);
CREATE TABLE product (
    prod_id INT AUTO_INCREMENT PRIMARY KEY,
    prod_name VARCHAR(100),
    prod_num VARCHAR(20),
    prod_type VARCHAR(50),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
alter table product add column (prod_amount int);
create user raghav identified by 'blablacar';
grant all on dbms_project to raghav;
create user monish identified by 'blablacar';
grant all on dbms_project to monish;
create user anusha identified by 'blablacar';
grant all on dbms_project to anusha;
create user public identified by 'mini123';
grant select on dbms_project.* to public;
CREATE TABLE date_of_login (
    user_id INT,
    login_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
DELIMITER //
CREATE TRIGGER user_login_trigger AFTER INSERT ON users
FOR EACH ROW
BEGIN
    INSERT INTO date_of_login (user_id, login_date) VALUES (NEW.user_id, NOW());
END;
//
DELIMITER ;
CREATE TABLE tax (
    tax_id INT AUTO_INCREMENT PRIMARY KEY,
    tax_name VARCHAR(50),
    tax_rate DECIMAL(5,2) -- Assuming tax rates are stored as decimals
);
SELECT bill_id,bill_amount FROM bill
UNION
SELECT tax_name, tax_rate FROM tax;
INSERT INTO users (username, user_email) VALUES
('raghav', 'rp3419@srmist.edu.in'),
('monish', 'mv1512@srmist.edu.in'),
('anusha', 'as6921@srmist.edu.in'),
('genreal', 'gn3169@srmist.edu.in');
INSERT INTO customer (user_id, cus_name, cus_mobile1, cus_mobile2) VALUES
(1, 'John Doe', '9876543210', '8765432109'),
(2, 'Jane Smith', '8765432109', NULL),
(3, 'Alice Johnson', '7654321098', '7654321097'),
(1, 'Michael Brown', '6543210987', NULL),
(2, 'Emily Davis', '5432109876', '4321098765'),
(3, 'Christopher Wilson', '4321098765', NULL),
(1, 'Sarah Miller', '3210987654', NULL),
(2, 'Matthew Taylor', '2109876543', '1098765432'),
(3, 'Amanda Martinez', '1098765432', '0987654321'),
(1, 'Daniel Anderson', '9988776655', NULL),
(2, 'Jessica White', '8877665544', '7766554433'),
(3, 'David Garcia', '7766554433', NULL),
(1, 'Laura Thompson', '6655443322', NULL),
(2, 'Andrew Thomas', '5544332211', '4433221100'),
(3, 'Jennifer Harris', '4433221100', '3322110099');

INSERT INTO product (prod_name, prod_num, prod_type, user_id) VALUES
('Laptop', 'P001', 'Electronics', 1),
('Smartphone', 'P002', 'Electronics', 2),
('Coffee Maker', 'P003', 'Appliances', 1),
('Headphones', 'P004', 'Electronics', 3),
('Television', 'P005', 'Electronics', 2),
('Toaster', 'P006', 'Appliances', 1),
('Blender', 'P007', 'Appliances', 3),
('Tablet', 'P008', 'Electronics', 2),
('Microwave', 'P009', 'Appliances', 1),
('Camera', 'P010', 'Electronics', 3),
('Printer', 'P011', 'Electronics', 2),
('Refrigerator', 'P012', 'Appliances', 1),
('Gaming Console', 'P013', 'Electronics', 3),
('Vacuum Cleaner', 'P014', 'Appliances', 2),
('Hair Dryer', 'P015', 'Appliances', 1);

CREATE VIEW final_bill_view AS
SELECT u.username, u.user_email, c.cus_name, c.cus_mobile1, c.cus_mobile2, p.prod_name, p.prod_num, p.prod_type
FROM users u
JOIN customer c ON u.user_id = c.user_id
JOIN product p ON u.user_id = p.user_id;
SELECT * FROM final_bill_view;

SELECT u.username, COUNT(*) AS total_orders
FROM users u
JOIN customer c ON u.user_id = c.user_id
GROUP BY u.username;

CREATE TABLE failed_login_attempts (
    user_id INT,
    attempts INT DEFAULT 0,
    last_attempt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

DELIMITER //
CREATE TRIGGER check_failed_logins
AFTER INSERT ON login
FOR EACH ROW
BEGIN
    DECLARE attempts_count INT;

    -- Get the current number of failed login attempts for the user
    SELECT attempts INTO attempts_count FROM failed_login_attempts WHERE user_id = NEW.user_id;

    -- Increment the attempts count
    SET attempts_count = attempts_count + 1;

    -- Update the attempts count in the table
    UPDATE failed_login_attempts SET attempts = attempts_count WHERE user_id = NEW.user_id;

    -- If the attempts count reaches 3, raise an error
    IF attempts_count >= 3 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Too many failed login attempts. Customer data will be truncated.';
    END IF;
END;
//
DELIMITER ;
-- END
