from db.connection import get_connection


def find_all_traits():
    con = get_connection()

    rows = con.execute(
        """
        SELECT trait_id, name, image_url, set_no
        FROM traits
        ORDER BY name
        """
    ).fetchall()

    con.close()
    return rows


def search_traits_by_name(keyword):
    con = get_connection()

    rows = con.execute(
        """
        SELECT trait_id, name, image_url, set_no
        FROM traits
        WHERE lower(name) LIKE lower(?)
        ORDER BY name
        """,
        [f"%{keyword}%"],
    ).fetchall()

    con.close()
    return rows


def find_trait_by_id(trait_id):
    con = get_connection()

    row = con.execute(
        """
        SELECT trait_id, name, image_url, set_no
        FROM traits
        WHERE trait_id = ?
        """,
        [trait_id],
    ).fetchone()

    con.close()
    return row