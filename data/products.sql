CREATE TABLE if not exists products (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- internal stable id
  product_id      TEXT UNIQUE NOT NULL,         -- เช่น "PHN-APL-IPH15-128-BLK"
  name            TEXT NOT NULL,
  brand           TEXT NOT NULL,
  category        TEXT NOT NULL CHECK (category IN ('phone','laptop','accessory')),

  price_cents     INTEGER NOT NULL CHECK (price_cents >= 0),
  currency        CHAR(3) NOT NULL DEFAULT 'USD',

  -- for typo/aliases
  aliases         TEXT[] NOT NULL DEFAULT '{}',  -- เช่น {"iphone15","ไอโฟน 15","ip 15"}

  -- specs
  specs           JSONB NOT NULL DEFAULT '{}'::jsonb,

  -- rating
  rating          NUMERIC(2,1),                  -- 0.0-5.0 (optional)
  popularity      INTEGER NOT NULL DEFAULT 0,    -- optional

  image_url       TEXT,
  is_active       BOOLEAN NOT NULL DEFAULT TRUE,

  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- index
CREATE INDEX if not exists products_category_idx ON products(category);
CREATE INDEX if not exists products_brand_idx ON products(brand);
CREATE INDEX if not exists products_price_idx ON products(price_cents);
CREATE INDEX if not exists products_specs_gin_idx ON products USING GIN (specs);

-- Apple
INSERT INTO products
(product_id, name, brand, category, price_cents, currency, aliases, specs, rating, popularity)
VALUES
('A1001','iPhone 16','Apple','phone',79900,'USD',
 ARRAY['iphone16'],
 '{ "brand":"Apple","model":"iPhone 16","chip":"A18","battery_mah":3279,
    "camera_rear_mp":48,"camera_front_mp":12,"screen_size_inch":6.1,
    "refresh_rate_hz":60,"network":"5G","weight_g":172 }',
 4.8,150),

('A1002','iPhone 16 Pro','Apple','phone',99900,'USD',
 ARRAY['iphone16pro'],
 '{ "brand":"Apple","model":"iPhone 16 Pro","chip":"A18 Pro","battery_mah":3350,
    "camera_rear_mp":48,"camera_front_mp":12,"screen_size_inch":6.1,
    "refresh_rate_hz":120,"network":"5G","weight_g":187 }',
 4.9,180),

('A1003','iPhone 16 Pro Max','Apple','phone',119900,'USD',
 ARRAY['iphone16promax'],
 '{ "brand":"Apple","model":"iPhone 16 Pro Max","chip":"A18 Pro","battery_mah":4422,
    "camera_rear_mp":48,"camera_front_mp":12,"screen_size_inch":6.7,
    "refresh_rate_hz":120,"network":"5G","weight_g":221 }',
 4.9,200);

--Samsung
INSERT INTO products
(product_id, name, brand, category, price_cents, currency, aliases, specs, rating, popularity)
VALUES
('S2001','Galaxy S25 Ultra','Samsung','phone',129900,'USD',
 ARRAY['galaxys25ultra','s25ultra'],
 '{ "brand":"Samsung","model":"Galaxy S25 Ultra","chip":"Snapdragon 8 Gen 4",
    "battery_mah":5000,"camera_rear_mp":200,"camera_front_mp":12,
    "screen_size_inch":6.8,"refresh_rate_hz":120,"network":"5G","weight_g":233 }',
 4.8,170),

('S2002','Galaxy S25','Samsung','phone',79900,'USD',
 ARRAY['galaxys25'],
 '{ "brand":"Samsung","model":"Galaxy S25","chip":"Snapdragon 8 Gen 4",
    "battery_mah":4000,"camera_rear_mp":50,"camera_front_mp":12,
    "screen_size_inch":6.2,"refresh_rate_hz":120,"network":"5G","weight_g":168 }',
 4.6,130),

('S2003','Galaxy A55 5G','Samsung','phone',44900,'USD',
 ARRAY['galaxya55','a55'],
 '{ "brand":"Samsung","model":"Galaxy A55 5G","chip":"Exynos 1480",
    "battery_mah":5000,"camera_rear_mp":50,"camera_front_mp":32,
    "screen_size_inch":6.6,"refresh_rate_hz":120,"network":"5G","weight_g":213 }',
 4.5,110);

--Xiaomi
INSERT INTO products
(product_id, name, brand, category, price_cents, currency, aliases, specs, rating, popularity)
VALUES
('X3001','Xiaomi 15','Xiaomi','phone',69900,'USD',
 ARRAY['xiaomi15'],
 '{ "brand":"Xiaomi","model":"Xiaomi 15","chip":"Snapdragon 8 Gen 4",
    "battery_mah":4800,"camera_rear_mp":50,"camera_front_mp":32,
    "screen_size_inch":6.36,"refresh_rate_hz":120,"network":"5G","weight_g":191 }',
 4.6,140),

('X3002','Xiaomi 15 Ultra','Xiaomi','phone',99900,'USD',
 ARRAY['xiaomi15ultra'],
 '{ "brand":"Xiaomi","model":"Xiaomi 15 Ultra","chip":"Snapdragon 8 Gen 4",
    "battery_mah":5300,"camera_rear_mp":200,"camera_front_mp":32,
    "screen_size_inch":6.73,"refresh_rate_hz":120,"network":"5G","weight_g":229 }',
 4.8,160),

('X3003','Redmi Note 13 Pro','Xiaomi','phone',34900,'USD',
 ARRAY['redminote13pro'],
 '{ "brand":"Xiaomi","model":"Redmi Note 13 Pro","chip":"Snapdragon 7s Gen 2",
    "battery_mah":5100,"camera_rear_mp":200,"camera_front_mp":16,
    "screen_size_inch":6.67,"refresh_rate_hz":120,"network":"5G","weight_g":187 }',
 4.5,120);

--Oppo
INSERT INTO products
(product_id, name, brand, category, price_cents, currency, aliases, specs, rating, popularity)
VALUES
('O4001','OPPO Find X7 Ultra','OPPO','phone',99900,'USD',
 ARRAY['findx7ultra'],
 '{ "brand":"OPPO","model":"Find X7 Ultra","chip":"Snapdragon 8 Gen 3",
    "battery_mah":5000,"camera_rear_mp":50,"camera_front_mp":32,
    "screen_size_inch":6.82,"refresh_rate_hz":120,"network":"5G","weight_g":221 }',
 4.7,125),

('O4002','OPPO Reno11 Pro','OPPO','phone',59900,'USD',
 ARRAY['reno11pro'],
 '{ "brand":"OPPO","model":"Reno11 Pro","chip":"Dimensity 8200",
    "battery_mah":4700,"camera_rear_mp":50,"camera_front_mp":32,
    "screen_size_inch":6.7,"refresh_rate_hz":120,"network":"5G","weight_g":181 }',
 4.5,95),

('O4003','OPPO A78 5G','OPPO','phone',29900,'USD',
 ARRAY['oppoa78'],
 '{ "brand":"OPPO","model":"A78 5G","chip":"Dimensity 700",
    "battery_mah":5000,"camera_rear_mp":50,"camera_front_mp":8,
    "screen_size_inch":6.56,"refresh_rate_hz":90,"network":"5G","weight_g":188 }',
 4.3,80);

--Vivo
INSERT INTO products
(product_id, name, brand, category, price_cents, currency, aliases, specs, rating, popularity)
VALUES
('V5001','vivo X200 Pro','vivo','phone',89900,'USD',
 ARRAY['vivox200pro'],
 '{ "brand":"vivo","model":"X200 Pro","chip":"Dimensity 9300",
    "battery_mah":5400,"camera_rear_mp":50,"camera_front_mp":32,
    "screen_size_inch":6.78,"refresh_rate_hz":120,"network":"5G","weight_g":225 }',
 4.7,110),

('V5002','vivo V40 5G','vivo','phone',49900,'USD',
 ARRAY['vivov40'],
 '{ "brand":"vivo","model":"V40 5G","chip":"Snapdragon 7 Gen 3",
    "battery_mah":5000,"camera_rear_mp":64,"camera_front_mp":50,
    "screen_size_inch":6.78,"refresh_rate_hz":120,"network":"5G","weight_g":190 }',
 4.5,90),

('V5003','vivo Y100','vivo','phone',29900,'USD',
 ARRAY['vivoy100'],
 '{ "brand":"vivo","model":"Y100","chip":"Dimensity 6020",
    "battery_mah":5000,"camera_rear_mp":64,"camera_front_mp":16,
    "screen_size_inch":6.38,"refresh_rate_hz":90,"network":"5G","weight_g":184 }',
 4.2,70);

INSERT INTO products
(product_id, name, brand, category, price_cents, currency, aliases, specs, rating, popularity, image_url)
VALUES
-- =========================
-- Dell
-- =========================
('31001', 'Dell XPS 13 (9340)', 'Dell', 'laptop', 129900, 'USD',
 ARRAY['xps13','xps 13 9340','เดล xps 13','xps9340'],
 '{
   "brand":"Dell",
   "model":"XPS 13 (9340)",
   "processor":"Intel Core Ultra 7 155H",
   "graphics":"Intel Arc (integrated)",
   "display":"OLED",
   "screen_size_inch":13.4,
   "screen_resolution":"2880x1800",
   "screen_refresh_hz":120,
   "ram_gb":16,
   "ram_type":"LPDDR5x",
   "storage_gb":512,
   "storage_type":"NVMe SSD",
   "battery_wh":55,
   "os":"Windows 11",
   "dimension_mm":"295.3x199.0x15.3",
   "net_weight_kg":1.18
 }'::jsonb,
 4.7, 120, NULL
),

('31002', 'Dell Inspiron 14 Plus (7440)', 'Dell', 'laptop', 79999, 'USD',
 ARRAY['inspiron14plus','inspiron 7440','เดล inspiron 7440'],
 '{
   "brand":"Dell",
   "model":"Inspiron 14 Plus (7440)",
   "processor":"Intel Core Ultra 7 (Series 1)",
   "graphics":"Intel Arc (integrated)",
   "display":"IPS",
   "screen_size_inch":14.0,
   "screen_resolution":"2240x1400",
   "screen_refresh_hz":60,
   "ram_gb":16,
   "ram_type":"LPDDR5x",
   "storage_gb":512,
   "storage_type":"NVMe SSD",
   "battery_wh":64,
   "os":"Windows 11",
   "dimension_mm":"314.0x226.0x16.0",
   "net_weight_kg":1.60
 }'::jsonb,
 4.4, 85, NULL
),

('31003', 'Dell Alienware m16 R2', 'Dell', 'laptop', 149999, 'USD',
 ARRAY['alienware m16 r2','m16r2'],
 '{
   "brand":"Dell",
   "model":"Alienware m16 R2",
   "processor":"Intel Core Ultra 9 (Series 1)",
   "graphics":"NVIDIA GeForce RTX (varies by config)",
   "display":"IPS",
   "screen_size_inch":16.0,
   "screen_resolution":"2560x1600",
   "screen_refresh_hz":240,
   "ram_gb":16,
   "ram_type":"DDR5",
   "storage_gb":1000,
   "storage_type":"NVMe SSD",
   "battery_wh":90,
   "os":"Windows 11",
   "dimension_mm":"365.0x289.0x23.0",
   "net_weight_kg":2.61
 }'::jsonb,
 4.6, 95, NULL
),

-- =========================
-- HP
-- =========================
('31004', 'HP Spectre x360 14 (2024)', 'HP', 'laptop', 139999, 'USD',
 ARRAY['spectre x360 14','spectre14','hp spectre 14'],
 '{
   "brand":"HP",
   "model":"Spectre x360 14 (2024)",
   "processor":"Intel Core Ultra 7 155H",
   "graphics":"Intel Arc (integrated)",
   "display":"OLED",
   "screen_size_inch":14.0,
   "screen_resolution":"2880x1800",
   "screen_refresh_hz":120,
   "ram_gb":16,
   "ram_type":"LPDDR5x",
   "storage_gb":1000,
   "storage_type":"NVMe SSD",
   "battery_wh":68,
   "os":"Windows 11",
   "dimension_mm":"313.0x220.0x16.9",
   "net_weight_kg":1.56
 }'::jsonb,
 4.7, 110, NULL
),

('31005', 'HP Envy x360 14 (2024)', 'HP', 'laptop', 99999, 'USD',
 ARRAY['envy x360 14','envy14','hp envy x360 14'],
 '{
   "brand":"HP",
   "model":"Envy x360 14 (2024)",
   "processor":"Intel Core Ultra 5 (Series 1)",
   "graphics":"Intel Arc (integrated)",
   "display":"OLED",
   "screen_size_inch":14.0,
   "screen_resolution":"2880x1800",
   "screen_refresh_hz":120,
   "ram_gb":16,
   "ram_type":"LPDDR5x",
   "storage_gb":512,
   "storage_type":"NVMe SSD",
   "battery_wh":59,
   "os":"Windows 11",
   "dimension_mm":"313.0x218.0x16.9",
   "net_weight_kg":1.39
 }'::jsonb,
 4.5, 90, NULL
),

('31006', 'HP OMEN Transcend 14 (2024)', 'HP', 'laptop', 149999, 'USD',
 ARRAY['omen transcend 14','transcend14','hp omen transcend 14'],
 '{
   "brand":"HP",
   "model":"OMEN Transcend 14 (2024)",
   "processor":"Intel Core Ultra 9 (Series 1)",
   "graphics":"NVIDIA GeForce RTX (varies by config)",
   "display":"OLED",
   "screen_size_inch":14.0,
   "screen_resolution":"2880x1800",
   "screen_refresh_hz":120,
   "ram_gb":16,
   "ram_type":"DDR5",
   "storage_gb":1000,
   "storage_type":"NVMe SSD",
   "battery_wh":71,
   "os":"Windows 11",
   "dimension_mm":"314.0x234.0x18.0",
   "net_weight_kg":1.63
 }'::jsonb,
 4.6, 105, NULL
),

-- =========================
-- Lenovo
-- =========================
('31007', 'Lenovo ThinkPad X1 Carbon Gen 12', 'Lenovo', 'laptop', 159999, 'USD',
 ARRAY['x1 carbon gen 12','thinkpad x1 carbon 12','x1carbon12'],
 '{
   "brand":"Lenovo",
   "model":"ThinkPad X1 Carbon Gen 12",
   "processor":"Intel Core Ultra 7 155U",
   "graphics":"Intel integrated graphics",
   "display":"IPS",
   "screen_size_inch":14.0,
   "screen_resolution":"1920x1200",
   "screen_refresh_hz":60,
   "ram_gb":16,
   "ram_type":"LPDDR5x",
   "storage_gb":512,
   "storage_type":"NVMe SSD",
   "battery_wh":57,
   "os":"Windows 11 Pro",
   "dimension_mm":"315.6x222.5x15.4",
   "net_weight_kg":1.08
 }'::jsonb,
 4.8, 130, NULL
),

('31008', 'Lenovo Yoga Pro 9i Gen 9 (16")', 'Lenovo', 'laptop', 169999, 'USD',
 ARRAY['yoga pro 9i gen 9','yoga pro 9i 16','yogapro9i'],
 '{
   "brand":"Lenovo",
   "model":"Yoga Pro 9i Gen 9 (16\")",
   "processor":"Intel Core Ultra 9 (Series 1)",
   "graphics":"NVIDIA GeForce RTX (varies by config)",
   "display":"Mini-LED",
   "screen_size_inch":16.0,
   "screen_resolution":"3200x2000",
   "screen_refresh_hz":165,
   "ram_gb":32,
   "ram_type":"LPDDR5x",
   "storage_gb":1000,
   "storage_type":"NVMe SSD",
   "battery_wh":84,
   "os":"Windows 11",
   "dimension_mm":"362.0x253.0x18.0",
   "net_weight_kg":1.95
 }'::jsonb,
 4.7, 115, NULL
),

('31009', 'Lenovo Legion Pro 7i Gen 9 (16")', 'Lenovo', 'laptop', 199999, 'USD',
 ARRAY['legion pro 7i gen 9','legion pro 7i 16','legionpro7i'],
 '{
   "brand":"Lenovo",
   "model":"Legion Pro 7i Gen 9 (16\")",
   "processor":"Intel Core i9 HX (varies by config)",
   "graphics":"NVIDIA GeForce RTX (varies by config)",
   "display":"IPS",
   "screen_size_inch":16.0,
   "screen_resolution":"2560x1600",
   "screen_refresh_hz":240,
   "ram_gb":32,
   "ram_type":"DDR5",
   "storage_gb":1000,
   "storage_type":"NVMe SSD",
   "battery_wh":99.99,
   "os":"Windows 11",
   "dimension_mm":"364.0x262.0x26.0",
   "net_weight_kg":2.80
 }'::jsonb,
 4.6, 125, NULL
);

INSERT INTO products
(product_id, name, brand, category, price_cents, currency, aliases, specs, rating, popularity, image_url)
VALUES
-- =================================
-- Charger / Adapter (5)
-- =================================
('40001','Apple 20W USB-C Power Adapter','Apple','accessory',1900,'USD',
 ARRAY['apple 20w charger'],
 '{
   "type":"charger",
   "output_watt":20,
   "port":"USB-C",
   "fast_charge":true,
   "compatibility":"iPhone, iPad",
   "weight_g":60
 }',4.6,120,NULL),

('40002','Anker Nano II 65W Charger','Anker','accessory',5999,'USD',
 ARRAY['anker 65w','anker nano ii'],
 '{
   "type":"charger",
   "output_watt":65,
   "port":"USB-C",
   "fast_charge":true,
   "gan":true,
   "weight_g":112
 }',4.8,200,NULL),

('40003','Samsung 25W Super Fast Charging','Samsung','accessory',2499,'USD',
 ARRAY['samsung 25w charger'],
 '{
   "type":"charger",
   "output_watt":25,
   "port":"USB-C",
   "fast_charge":true,
   "compatibility":"Galaxy devices",
   "weight_g":63
 }',4.5,110,NULL),

('40004','UGREEN 100W USB-C Charger','UGREEN','accessory',7499,'USD',
 ARRAY['ugreen 100w'],
 '{
   "type":"charger",
   "output_watt":100,
   "port":"USB-C x2",
   "fast_charge":true,
   "gan":true,
   "weight_g":215
 }',4.7,150,NULL),

('40005','Baseus Car Charger 65W','Baseus','accessory',3999,'USD',
 ARRAY['baseus car charger'],
 '{
   "type":"car_charger",
   "output_watt":65,
   "port":"USB-C + USB-A",
   "fast_charge":true,
   "weight_g":90
 }',4.4,95,NULL),

-- =================================
-- Headphone / Earbuds (5)
-- =================================
('40006','Apple AirPods Pro (2nd Gen)','Apple','accessory',24900,'USD',
 ARRAY['airpods pro 2'],
 '{
   "type":"earbuds",
   "wireless":true,
   "noise_cancelling":true,
   "battery_hours":30,
   "water_resistant":"IPX4",
   "weight_g":56
 }',4.8,300,NULL),

('40007','Sony WH-1000XM5','Sony','accessory',39900,'USD',
 ARRAY['sony xm5'],
 '{
   "type":"headphone",
   "wireless":true,
   "noise_cancelling":true,
   "battery_hours":30,
   "weight_g":250
 }',4.9,280,NULL),

('40008','Samsung Galaxy Buds2 Pro','Samsung','accessory',22900,'USD',
 ARRAY['galaxy buds2 pro'],
 '{
   "type":"earbuds",
   "wireless":true,
   "noise_cancelling":true,
   "battery_hours":29,
   "water_resistant":"IPX7",
   "weight_g":43
 }',4.7,190,NULL),

('40009','JBL Tune 510BT','JBL','accessory',5900,'USD',
 ARRAY['jbl tune 510bt'],
 '{
   "type":"headphone",
   "wireless":true,
   "noise_cancelling":false,
   "battery_hours":40,
   "weight_g":160
 }',4.4,140,NULL),

('40010','Nothing Ear (2)','Nothing','accessory',14900,'USD',
 ARRAY['nothing ear 2'],
 '{
   "type":"earbuds",
   "wireless":true,
   "noise_cancelling":true,
   "battery_hours":36,
   "weight_g":52
 }',4.6,160,NULL),

-- =================================
-- Keyboard / Mouse (5)
-- =================================
('40011','Logitech MX Master 3S','Logitech','accessory',9999,'USD',
 ARRAY['mx master 3s'],
 '{
   "type":"mouse",
   "wireless":true,
   "dpi":8000,
   "battery_days":70,
   "weight_g":141
 }',4.9,260,NULL),

('40012','Logitech MX Keys','Logitech','accessory',11999,'USD',
 ARRAY['mx keys keyboard'],
 '{
   "type":"keyboard",
   "wireless":true,
   "layout":"full-size",
   "battery_days":10,
   "weight_g":810
 }',4.7,210,NULL),

('40013','Keychron K6 Mechanical Keyboard','Keychron','accessory',8999,'USD',
 ARRAY['keychron k6'],
 '{
   "type":"keyboard",
   "wireless":true,
   "mechanical":true,
   "layout":"65%",
   "weight_g":940
 }',4.6,170,NULL),

('40014','Razer DeathAdder V2','Razer','accessory',6999,'USD',
 ARRAY['deathadder v2'],
 '{
   "type":"mouse",
   "wireless":false,
   "dpi":20000,
   "rgb":true,
   "weight_g":82
 }',4.5,150,NULL),

('40015','Apple Magic Keyboard','Apple','accessory',9999,'USD',
 ARRAY['magic keyboard'],
 '{
   "type":"keyboard",
   "wireless":true,
   "layout":"compact",
   "battery_days":30,
   "weight_g":239
 }',4.4,180,NULL),

-- =================================
-- Bag / Case / Stand (5)
-- =================================
('40016','Incase ICON Backpack','Incase','accessory',19900,'USD',
 ARRAY['incase icon backpack'],
 '{
   "type":"bag",
   "capacity_l":20,
   "laptop_size_inch":15,
   "water_resistant":true,
   "weight_g":1300
 }',4.6,90,NULL),

('40017','Tomtoc Laptop Sleeve 14-inch','Tomtoc','accessory',3499,'USD',
 ARRAY['tomtoc sleeve 14'],
 '{
   "type":"sleeve",
   "laptop_size_inch":14,
   "water_resistant":true,
   "weight_g":280
 }',4.5,110,NULL),

('40018','Apple iPhone 15 Silicone Case','Apple','accessory',4900,'USD',
 ARRAY['iphone silicone case'],
 '{
   "type":"phone_case",
   "material":"silicone",
   "compatibility":"iPhone 15",
   "weight_g":35
 }',4.3,140,NULL),

('40019','UGREEN Laptop Stand','UGREEN','accessory',3999,'USD',
 ARRAY['ugreen laptop stand'],
 '{
   "type":"stand",
   "material":"aluminum",
   "adjustable":true,
   "weight_g":750
 }',4.6,125,NULL),

('40020','Baseus Phone Holder Desk Stand','Baseus','accessory',1999,'USD',
 ARRAY['baseus phone stand'],
 '{
   "type":"phone_stand",
   "material":"plastic",
   "adjustable":true,
   "weight_g":180
 }',4.4,100,NULL);
