from db.connection import get_connection

def find_all_champions():
    con = get_connection()

    rows = con.execute("""
        SELECT champion_id, name, tier, image_url, set_no
        FROM champions
        ORDER BY tier, name
    """).fetchall()

    con.close()
    return rows


def search_champions_by_name(keyword):
    con = get_connection()

    rows = con.execute("""
        SELECT champion_id, name, tier, image_url, set_no
        FROM champions
        WHERE lower(name) LIKE lower(?)
        ORDER BY tier, name
    """, [f"%{keyword}%"]).fetchall()

    con.close()
    return rows


def find_champion_detail(champion_id):
    con = get_connection()

    rows = con.execute("""
        SELECT 
            c.champion_id,
            c.name AS champion_name,
            c.tier,
            c.image_url AS champion_image_url,
            t.trait_id,
            t.name AS trait_name,
            t.image_url AS trait_image_url
        FROM champions c
        LEFT JOIN champion_traits ct ON c.champion_id = ct.champion_id
        LEFT JOIN traits t ON ct.trait_id = t.trait_id
        WHERE c.champion_id = ?
        ORDER BY t.name
    """, [champion_id]).fetchall()

    con.close()
    return rows