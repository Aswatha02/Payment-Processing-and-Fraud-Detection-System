-- init-databases.sql
-- Create all databases for each service

CREATE DATABASE auth_db;
CREATE DATABASE user_db;
CREATE DATABASE transaction_db;
CREATE DATABASE fraud_db;
CREATE DATABASE notification_db;
CREATE DATABASE wallet_db;
CREATE DATABASE audit_db;

-- Grant all privileges to postgres user on all databases
\c auth_db
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;

\c user_db
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;

\c transaction_db
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;

\c fraud_db
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;

\c notification_db
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;

\c wallet_db
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;

\c audit_db
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;

-- Output confirmation
\echo 'All databases created successfully!'