CREATE KEYSPACE IF NOT EXISTS eth_eco 
WITH REPLICATION = 
{'class':'SimpleStrategy', 'replication_factor':'1'};

CREATE TABLE IF NOT EXISTS eth_eco.eco_table (
uuid UUID,
id TEXT,
symbol TEXT,
name TEXT,
image TEXT, 
current_price FLOAT, 
market_cap FLOAT,
market_cap_rank INT,
fully_diluted_valuation TEXT,
total_volume INT,
high_24h FLOAT,
low_24h FLOAT,
price_change_24h FLOAT, 
price_change_percentage_24h FLOAT, 
market_cap_change_24h FLOAT,
market_cap_change_percentage_24h FLOAT,
circulating_supply FLOAT,
total_supply FLOAT,
max_supply FLOAT, 
ath FLOAT, 
atl_change_percentage FLOAT,
atl_date TIMESTAMP,
roi TEXT,
last_updated TIMESTAMP,
price_change_percentage_1h_in_currency FLOAT, 
PRIMARY KEY((uuiid), id));