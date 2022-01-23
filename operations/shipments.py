from email import message_from_file
from pathlib import Path
from urllib.parse import unquote

import pandas as pd
from unidecode import unidecode


def parse_subject(subject) -> str:
    """
    Gets shipment id from the email's subject

    :param subject: subject line from the email
    :return: shipment id (as str)
    """
    parts = subject.split()
    return parts[1]


def decode_city(city: str) -> str:
    """
    Correct city names containing foreign characters

    :return: corrected name
    """
    return unidecode(unquote(city.replace("=", "%")))


def extract_cards(body):
    """
    Extracts the lines containing ordered cards from the emails body

    :param body:  string with emails body text
    :return: list of lines containing bought cards and their price
    """
    record = False
    card_lines = []

    for line in str(body).split("\n"):
        if record and line.startswith("Shipping"):
            break

        if record and line.strip() != "":
            card_lines.append(line)

        if line.startswith("+++++++"):
            record = True

    return card_lines


def parse_cards(body) -> (int, float):
    """
    Extracts the total number cards bought (taking playsets into account) and the total value of those cards

    :param body: string with emails body text
    :return: tuple with card count and total value
    """
    card_data = extract_cards(body)

    card_count = 0
    card_value = 0

    for c in card_data:
        current_count = int(c.split("x")[0])
        current_value = float(c.split()[-2].replace(",", ".")) * current_count

        if "[Playset]" in c:
            current_count *= 4

        card_count += current_count
        card_value += current_value

    return card_count, card_value


def parse_shipping(body) -> float:
    """
    Extracts shipping costs from the mails body

    :param body: string with emails body text
    :return: shipping costs (float)
    """
    shipping_cost = 0
    for line in str(body).split("\n"):
        if line.startswith("Shipping"):
            shipping_cost = float(
                line.replace("Shipping", "").strip().split()[0].replace(",", ".")
            )

    return shipping_cost


def parse_address(body) -> (str, str, str):
    """
    Parses the address out of the emails body, returns zip code, city and country

    :param body: string with emails body text
    :return: tuple with zip, city and country of recipient
    """
    record = False
    address_lines = []

    for line in str(body).split("\n"):
        if line.startswith("Tracking:"):
            break

        if record and line.strip() != "":
            address_lines.append(line)

        if line.startswith("Status: Paid"):
            record = True

    zip_code = address_lines[-2].split()[0]
    city = " ".join(address_lines[-2].split()[1:])
    country = address_lines[-1]

    return zip_code, city, country


def parse_eml(file: str) -> dict:
    """
    Parses an email (eml file) with the shipping request from CardMarket.

    Will parse the shipment_id, order_date, total card value and total card count along with components from the
    recipient's address (only zip, city and country)

    :param file: path to the eml file
    :return: dictionary with data extracted from the email
    """
    output = {}
    with open(file) as fin:
        data = message_from_file(fin)

        body = str(data.get_payload(0)).replace("=\n", "")

        output["shipment_id"] = parse_subject(data["subject"])
        output["order_date"] = data["date"]

        zip_code, city, country = parse_address(body)

        output["zip"] = zip_code
        output["city"] = decode_city(city)
        output["country"] = country

        card_count, card_value = parse_cards(body)

        output["card_count"] = card_count
        output["card_value"] = card_value

        output["shipping"] = parse_shipping(body)

    return output


def read_folder(path: str):
    output = []
    files = Path(path).glob("Shipment*.eml")
    for file in files:
        output.append(parse_eml(file))

    return output


def add_new_shipments(df: pd.DataFrame, folder_path):
    shipment_data = read_folder(folder_path)

    for sd in shipment_data:
        if not sd["shipment_id"] in list(df["shipment_id"].astype(str)):
            df = df.append(sd, ignore_index=True)

    return df
