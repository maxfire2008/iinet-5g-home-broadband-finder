import time
import requests
import sqlite3
import json
import sys


def retroactively_add_easting_northing():
    # open the database
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # lookup all addresses and update easting and northing in one SQL statement
    c.execute(
        "UPDATE addresses SET easting = (SELECT easting FROM list_address_points_statewide WHERE unit_numb = addresses.unit_numb AND st_no_from = addresses.st_no_from AND street = addresses.street AND st_ty_code = addresses.st_ty_code AND locality = addresses.locality LIMIT 1), "
        "northing = (SELECT northing FROM list_address_points_statewide WHERE unit_numb = addresses.unit_numb AND st_no_from = addresses.st_no_from AND street = addresses.street AND st_ty_code = addresses.st_ty_code AND locality = addresses.locality LIMIT 1)"
    )

    # commit the changes
    conn.commit()

    # Close the database
    conn.close()


if __name__ == "__main__":
    retroactively_add_easting_northing()
