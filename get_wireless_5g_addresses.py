import time
import requests
import sqlite3
import json
import sys


def get_wireless_5g_addresses():
    # open the database
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # lookup all addresses that have iiNet_response listed
    c.execute(
        "SELECT unit_numb, st_no_from, street, st_ty_code, locality, easting, northing, iiNet_response FROM addresses"
        + " WHERE iiNet_response IS NOT NULL"
    )
    addresses = c.fetchall()

    for address in addresses:
        if json.loads(address[7]).get("WIRELESS5G", {}).get("res") != -1:
            # print(address[7])
            print(
                f"Address: {address[0].strip()} {int(float(address[1]))} {address[2].strip()} {address[3].strip()} {address[4].strip()}"
            )

    # commit the changes
    conn.commit()

    # Close the database
    conn.close()


if __name__ == "__main__":
    get_wireless_5g_addresses()
