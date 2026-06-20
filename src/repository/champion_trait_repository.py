from db.connection import get_connection


def find_traits_by_champion_id(champion_id):
    con = get_connection()

    rows = con.execute(
        """
        SELECT 
            ct.champion_id,
            t.trait_id,
            t.name AS trait_name,
            t.image_url AS trait_image_url
        FROM champion_traits ct
        JOIN traits t
            ON ct.trait_id = t.trait_id
        WHERE ct.champion_id = ?
        ORDER BY t.name
        """,
        [champion_id],
    ).fetchall()

    con.close()
    return rows


def find_champions_by_trait_id(trait_id):
    con = get_connection()

    rows = con.execute(
        """
        SELECT 
            ct.trait_id,
            c.champion_id,
            c.name AS champion_name,
            c.tier,
            c.image_url AS champion_image_url,
            c.set_no
        FROM champion_traits ct
        JOIN champions c
            ON ct.champion_id = c.champion_id
        WHERE ct.trait_id = ?
        ORDER BY c.tier, c.name
        """,
        [trait_id],
    ).fetchall()

    con.close()
    return rows


def find_all_champion_traits():
    con = get_connection()

    rows = con.execute(
        """
        SELECT 
            c.name AS champion_name,
            c.tier,
            t.name AS trait_name
        FROM champion_traits ct
        JOIN champions c
            ON ct.champion_id = c.champion_id
        JOIN traits t
            ON ct.trait_id = t.trait_id
        ORDER BY c.tier, c.name, t.name
        """
    ).fetchall()

    con.close()
    return rows