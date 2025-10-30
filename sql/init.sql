CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT
);

INSERT INTO products (name, description) VALUES
('Laptop', 'A high-performance laptop designed for both professional work and gaming. It features a fast processor, ample storage, and a stunning display, making it ideal for multitasking, programming, and creative work.'),
('Phone', 'A modern smartphone equipped with a high-resolution camera, long-lasting battery, and sleek design. Perfect for photography enthusiasts and daily productivity tasks.'),
('Headphones', 'Noise-cancelling over-ear headphones with crystal-clear audio quality and comfortable padding. Ideal for music lovers and frequent travelers who need to block out ambient noise.'),
('Monitor', 'A 27-inch 4K ultra HD monitor with vivid colors, fast refresh rate, and adjustable stand. Great for video editing, gaming, and office work.'),
('Keyboard', 'A mechanical keyboard with tactile switches, RGB backlighting, and customizable macros. Designed for gamers and programmers seeking speed and precision.'),
('Tablet', 'A lightweight tablet with high-resolution display, long battery life, and smooth performance. Suitable for reading, streaming, and creative work on the go.'),  
('Speaker', 'A portable Bluetooth speaker that delivers deep bass and clear sound. Compact design allows it to be used indoors or outdoors, making it ideal for parties and casual listening.');

CREATE ROLE replication_user WITH LOGIN REPLICATION;

GRANT CREATE ON DATABASE dlt_data TO replication_user;