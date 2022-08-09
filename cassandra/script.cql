CREATE KEYSPACE IF NOT EXISTS eth_eco 
WITH REPLICATION = 
{'class':'SimpleStrategy', 'replication_factor':'1'};

CREATE TABLE IF NOT EXISTS eth_eco.stats_table (
uuid TEXT,
id TEXT,
symbol TEXT,
name TEXT,
current_price FLOAT,
market_cap FLOAT,
market_cap_rank FLOAT,
total_volume FLOAT,
high_24h FLOAT,
low_24h FLOAT,
price_change_24h FLOAT,
price_change_percentage_24h FLOAT,
PRIMARY KEY((uuid), id));

INSERT INTO eth_eco.stats_table (uuid, id, symbol, name, current_price, market_cap, market_cap_rank, total_volume, high_24h, low_24h, price_change_24h, price_change_percentage_24h, market_cap_change_24h, market_cap_change_percentage_24h)
  VALUES  ('ethereum', 'eth', 'Ethereum', 'https://assets.coingecko.com/coins/images/279/large/ethereum.png?1595348880', '1709.8', 205324423655, 2, 9103171292, 1720.38, 1673.45, -5.831259119289371, -0.33989, -490176041.47094727, -0.23816);