-- Sample database initialization script
-- This creates sample tables and data for testing the SQL AI Agent

-- Create sample users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    age INTEGER CHECK (age > 0),
    city VARCHAR(100),
    country VARCHAR(100) DEFAULT 'USA',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sample orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_name VARCHAR(200) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price > 0),
    total_amount DECIMAL(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled'))
);

-- Create sample categories table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sample products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample categories
INSERT INTO categories (name, description) VALUES
('Electronics', 'Electronic devices and accessories'),
('Books', 'Physical and digital books'),
('Clothing', 'Apparel and fashion items'),
('Home & Garden', 'Home improvement and gardening supplies'),
('Sports', 'Sports equipment and accessories')
ON CONFLICT (name) DO NOTHING;

-- Insert sample products
INSERT INTO products (name, category_id, price, stock_quantity, description) VALUES
('Laptop Pro 15"', 1, 1299.99, 50, 'High-performance laptop for professionals'),
('Wireless Headphones', 1, 199.99, 100, 'Noise-cancelling wireless headphones'),
('Programming Guide', 2, 49.99, 200, 'Complete guide to modern programming'),
('Fiction Novel', 2, 14.99, 150, 'Bestselling fiction novel'),
('Cotton T-Shirt', 3, 24.99, 300, 'Comfortable cotton t-shirt'),
('Running Shoes', 5, 89.99, 75, 'Professional running shoes'),
('Garden Tool Set', 4, 79.99, 40, 'Complete set of garden tools'),
('Yoga Mat', 5, 34.99, 120, 'Non-slip yoga mat'),
('Coffee Maker', 4, 129.99, 60, 'Automatic coffee maker'),
('Smartphone', 1, 699.99, 80, 'Latest smartphone with advanced features')
ON CONFLICT DO NOTHING;

-- Insert sample users
INSERT INTO users (name, email, age, city, country) VALUES
('John Doe', 'john.doe@example.com', 30, 'New York', 'USA'),
('Jane Smith', 'jane.smith@example.com', 25, 'Los Angeles', 'USA'),
('Bob Johnson', 'bob.johnson@example.com', 35, 'Chicago', 'USA'),
('Alice Brown', 'alice.brown@example.com', 28, 'Houston', 'USA'),
('Charlie Wilson', 'charlie.wilson@example.com', 32, 'Phoenix', 'USA'),
('Diana Davis', 'diana.davis@example.com', 27, 'Philadelphia', 'USA'),
('Edward Miller', 'edward.miller@example.com', 41, 'San Antonio', 'USA'),
('Fiona Garcia', 'fiona.garcia@example.com', 29, 'San Diego', 'USA'),
('George Martinez', 'george.martinez@example.com', 33, 'Dallas', 'USA'),
('Helen Rodriguez', 'helen.rodriguez@example.com', 26, 'San Jose', 'USA')
ON CONFLICT (email) DO NOTHING;

-- Insert sample orders
INSERT INTO orders (user_id, product_name, quantity, unit_price, status) VALUES
(1, 'Laptop Pro 15"', 1, 1299.99, 'delivered'),
(1, 'Wireless Headphones', 1, 199.99, 'delivered'),
(2, 'Cotton T-Shirt', 2, 24.99, 'shipped'),
(2, 'Running Shoes', 1, 89.99, 'processing'),
(3, 'Programming Guide', 1, 49.99, 'delivered'),
(3, 'Coffee Maker', 1, 129.99, 'shipped'),
(4, 'Yoga Mat', 1, 34.99, 'delivered'),
(4, 'Fiction Novel', 3, 14.99, 'delivered'),
(5, 'Smartphone', 1, 699.99, 'processing'),
(5, 'Garden Tool Set', 1, 79.99, 'pending'),
(6, 'Wireless Headphones', 1, 199.99, 'delivered'),
(7, 'Cotton T-Shirt', 1, 24.99, 'shipped'),
(8, 'Running Shoes', 1, 89.99, 'delivered'),
(9, 'Programming Guide', 2, 49.99, 'processing'),
(10, 'Yoga Mat', 1, 34.99, 'delivered')
ON CONFLICT DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_city ON users(city);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);

-- Create a view for order summary
CREATE OR REPLACE VIEW order_summary AS
SELECT 
    u.name as customer_name,
    u.email,
    u.city,
    o.id as order_id,
    o.product_name,
    o.quantity,
    o.unit_price,
    o.total_amount,
    o.status,
    o.order_date
FROM users u
JOIN orders o ON u.id = o.user_id;

-- Create a view for sales analytics
CREATE OR REPLACE VIEW sales_analytics AS
SELECT 
    DATE_TRUNC('month', order_date) as month,
    COUNT(*) as total_orders,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value,
    COUNT(DISTINCT user_id) as unique_customers
FROM orders
WHERE status IN ('delivered', 'shipped')
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

-- Add some helpful comments
COMMENT ON TABLE users IS 'Customer information table';
COMMENT ON TABLE orders IS 'Order transactions table';
COMMENT ON TABLE categories IS 'Product categories lookup table';
COMMENT ON TABLE products IS 'Product catalog table';
COMMENT ON VIEW order_summary IS 'Detailed order information with customer details';
COMMENT ON VIEW sales_analytics IS 'Monthly sales analytics and metrics';

-- Print completion message
DO $$
BEGIN
    RAISE NOTICE 'Sample database initialized successfully!';
    RAISE NOTICE 'Tables created: users, orders, categories, products';
    RAISE NOTICE 'Views created: order_summary, sales_analytics';
    RAISE NOTICE 'Sample data inserted for testing SQL AI Agent';
END $$;
