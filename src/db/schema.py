from db.connection import get_connection

def create_tables():
    con = get_connection()

    con.execute("""
        CREATE TABLE IF NOT EXISTS champions (
            champion_id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL,
            tier INTEGER NOT NULL,
            image_url VARCHAR,
            set_no INTEGER NOT NULL
        );
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS traits (
            trait_id VARCHAR PRIMARY KEY,
            name VARCHAR NOT NULL,
            image_url VARCHAR,
            set_no INTEGER NOT NULL
        );
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS champion_traits (
            champion_id VARCHAR NOT NULL,
            trait_id VARCHAR NOT NULL,
            PRIMARY KEY (champion_id, trait_id)
        );
    """)

    con.close()