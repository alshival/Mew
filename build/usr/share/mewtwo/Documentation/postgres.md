# Example Documentation

This documentation covers how to add a new user, grant them necessary permissions, and whitelist them in the PostgreSQL server’s `pg_hba.conf` file.

## Connecting to the PostgreSQL Database

Users can connect to the PostgreSQL database locally using the following connection parameters:

- **Hostname:** `localhost`
- **Port:** `5445`
- **Username:** `<Your Postgres Username>`
- **Password:** `<Your Postgres Password>`

## 1. How to Add a New User & Grant Them Permissions to Databases

To add a new user in PostgreSQL and grant them permissions to specific databases, follow these steps:

### Step 1: Log in to the PostgreSQL Server
Log in to the PostgreSQL server using the `psql` command-line tool with a superuser account:
```bash
psql -U postgres -h localhost -p 5445
```

### Step 2: Create a New User
Create a new user by executing the following SQL command:
```sql
CREATE USER new_username WITH PASSWORD 'new_password';
```
Replace `new_username` with the desired username and `new_password` with a secure password.

### Step 3: Grant Permissions to the User
You can grant specific permissions to the new user for a particular database using the following commands:

#### Grant Connection Permission to a Database:
```sql
GRANT CONNECT ON DATABASE database_name TO new_username;
```

#### Grant Usage on a Schema:
```sql
GRANT USAGE ON SCHEMA schema_name TO new_username;
```

#### Grant Permission to All Tables in a Schema:
```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA schema_name TO new_username;
```

Replace `database_name` with the name of the database, `schema_name` with the schema, and `new_username` with the new user's username.

### Step 4: Verify User Permissions
To verify that the user has been granted the correct permissions, you can check the permissions using the following command:
```sql
\du new_username
```

## 2. How to Whitelist a User in `pg_hba.conf`

### Step 1: Locate the `pg_hba.conf` File
The `pg_hba.conf` file is typically located in the PostgreSQL data directory. You can find its exact location by running:
```bash
SHOW hba_file;
```

### Step 2: Edit the `pg_hba.conf` File
Open the `pg_hba.conf` file with your preferred text editor:
```bash
sudo nano /path/to/pg_hba.conf
```

### Step 3: Add a New Entry for the User
To whitelist the new user, add the following entry to the `pg_hba.conf` file:
```
# Allow new user to connect from any IP address
host    all    new_username    0.0.0.0/0    md5
```
Replace `new_username` with the new user’s name. This configuration allows the user to connect from any IP address.

### Step 4: Reload the PostgreSQL Configuration
After modifying the `pg_hba.conf` file, reload the PostgreSQL configuration for the changes to take effect:
```bash
sudo systemctl reload postgresql
```