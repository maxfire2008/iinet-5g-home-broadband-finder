import time
import requests
import sqlite3
import json
import sys


def retroactively_add_easting_northing():
    # open the database
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # lookup all addresses
    c.execute(
        "SELECT unit_numb, st_no_from, street, st_ty_code, locality, postcode, state FROM addresses"
    )
    addresses = c.fetchall()

    # lookup each address in the list_address_points_statewide table
    # match unit_numb, st_no_from, street, st_ty_code, locality, postcode, state

    for address in addresses:
        c.execute(
            "SELECT easting, northing FROM list_address_points_statewide "
            + "WHERE unit_numb = ? AND st_no_from = ? AND street = ? AND st_ty_code = ? AND locality = ? AND postcode = ? AND state = ?",
            address,
        )
        easting_northing = c.fetchone()

        if easting_northing is not None:
            c.execute(
                "UPDATE addresses SET easting = ?, northing = ? "
                + "WHERE unit_numb = ? AND st_no_from = ? AND street = ? AND st_ty_code = ? AND locality = ? AND postcode = ? AND state = ?",
                (*easting_northing, *address),
            )
        else:
            print("No easting/northing found for address:", address)

    # commit the changes
    conn.commit()

    # Close the database
    conn.close()


if __name__ == "__main__":
    retroactively_add_easting_northing()
