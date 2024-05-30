import time
import requests
import sqlite3
import json
import sys


def job_create():
    # open the database
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Go through all addresses in which postcode = input
    c.execute(
        "SELECT unit_numb, st_no_from, street, st_ty_code, locality, postcode, state, easting, northing FROM list_address_points_statewide",
    )
    addresses = c.fetchall()

    # Create a table to store the addresses
    c.execute(
        """CREATE TABLE addresses (
            unit_numb TEXT,
            st_no_from TEXT,
            street TEXT,
            st_ty_code TEXT,
            locality TEXT,
            postcode TEXT,
            state TEXT,
            easting TEXT,
            northing TEXT,
            iiNet_response JSON,
            iiNet_response_retrieved_at DATETIME DEFAULT NULL
        )"""
    )

    # Insert the addresses into the table
    c.executemany(
        "INSERT INTO addresses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)",
        addresses,
    )

    # commit the changes
    conn.commit()

    # Close the database
    conn.close()


def job_run_one(filter_postcode=None):
    # open the database
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Go through all addresses in which postcode = input
    c.execute(
        "SELECT unit_numb, st_no_from, street, st_ty_code, locality, postcode, state, iiNet_response, rowid FROM addresses"
        + " WHERE iiNet_response IS NULL AND iiNet_response_retrieved_at IS NULL"
        + ("" if filter_postcode is None else " AND postcode = ?")
        + " ORDER BY RANDOM() LIMIT 1",
        (filter_postcode,),
    )
    address = c.fetchone()

    # If there are no addresses left, exit
    if not address:
        print("No addresses left")
        conn.close()
        return False

    # set the iiNet_response_retrieved_at to the current time
    while True:
        try:
            c.execute(
                "UPDATE addresses SET iiNet_response_retrieved_at = datetime('now') WHERE rowid = ?",
                (address[8],),
            )
            break
        except sqlite3.OperationalError as e:
            print(e)
            return True

    # commit the changes
    conn.commit()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
        "uuid": "f08f168a-2d21-4375-b13b-59fa473a816c",
        "Origin": "https://www.iinet.net.au",
        "Connection": "keep-alive",
        "Referer": "https://www.iinet.net.au/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    address_json = {
        "brand": "IINET",
        "addressDetails": {
            "unitNumber": address[0].strip(),
            "streetNumber": str(int(float(address[1]))),
            "streetName": address[2].strip(),
            "streetType": address[3].strip(),
            "suburb": address[4].strip(),
            "postcode": address[5],
            "state": address[6].strip(),
            "country": "AUSTRALIA",
            "customField4": "undefinedUnitPrefix:|LotNumber:",
            "isManualInput": True,
        },
        "fsu": False,
    }

    json_data = {
        "address": json.dumps(address_json),
        "pageOrigin": "FIXEDWIRELESS5G",
    }

    response = requests.post(
        "https://pc.iinet.net.au/product-configurator/api/oneSqByAddress/",
        headers=headers,
        json=json_data,
    )

    print(
        response.status_code,
        address_json["addressDetails"]["unitNumber"]
        + "/"
        + address_json["addressDetails"]["streetNumber"]
        + " "
        + address_json["addressDetails"]["streetName"]
        + " "
        + address_json["addressDetails"]["streetType"]
        + " "
        + address_json["addressDetails"]["suburb"]
        + " "
        + address_json["addressDetails"]["postcode"],
        "is",
        response.json().get("formed_fulladdress", "not found"),
    )

    # Update the iiNet_response in the database
    while True:
        try:
            c.execute(
                "UPDATE addresses SET iiNet_response = ? WHERE rowid = ?",
                (response.text, address[8]),
            )
            break
        except sqlite3.OperationalError as e:
            print(e)
            time.sleep(0.001)

    conn.commit()

    # Close the database
    conn.close()

    return True


def job_run(filter_postcode=None):
    while job_run_one(filter_postcode):
        pass


if __name__ == "__main__":
    if sys.argv[1] == "create":
        job_create()
    elif sys.argv[1] == "run":
        job_run(filter_postcode=int(sys.argv[2]) if len(sys.argv) == 3 else None)
