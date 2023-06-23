import re
import requests
from typing import Dict

import pandas as pd
from bs4 import BeautifulSoup as bs

from service import BRANCHES_URL, ESTATE_AGENTS_URL, PROPERTY_TYPES


def get_your_move_branches() -> str:
    """Returns the Your Move branch locations.
    """
    page = requests.get(BRANCHES_URL)
    soup = bs(page.content, "html.parser")
    results = soup.findAll('h2', class_="branch-thumbnail__title")
    return [branch.text for branch in results]

def get_your_move_houses_for_sale_at_branch(
    branch: str, max_pages: int = 11
) -> Dict[str, str]:
    """Returns the houses for sale on your move at a specified branch.
    """
    for_sale_dictionary = {
        "property_id": [],
        "description": [],
        "price": [],
        "beds": [],
        "baths": [],
        "branch": [],
    }

    _branch = branch.lower().replace(" ", "-")
    print(_branch)
    
    for page in range(1, max_pages):
        URL = (
            f"{ESTATE_AGENTS_URL}/{_branch}/"
            f"find-property-for-sale/!/page/{page}"
        )
        page_content = requests.get(URL)
        soup = bs(page_content.content, "html.parser")
        results = soup.findAll("div", id=lambda x: x and x.startswith('property_'))
        
        if results:
            print(page)
            for result in results:
                property_id = re.findall("property_[0-9]{10}", result.prettify())
                if property_id:
                    try:
                        property_id = property_id[0]
                        price = result.find_all(
                            "div", class_="property-thumbnail__price"
                        )[0].text.strip()
                        description = result.find_all(
                            "div", class_="property-thumbnail__description"
                        )[0].text.strip()
                        beds = result.find_all(
                            "div",
                            class_=(
                                "property-thumbnail-icon property-thumbnail-icon--beds"
                            )
                        )[0].text
                        baths = result.find_all(
                            "div",
                            class_=(
                                "property-thumbnail-icon property-thumbnail-icon--baths"
                            )
                        )[0].text
                        for_sale_dictionary["property_id"].append(property_id)
                        for_sale_dictionary["description"].append(description)
                        for_sale_dictionary["price"].append(price)
                        for_sale_dictionary["beds"].append(beds)
                        for_sale_dictionary["baths"].append(baths)
                        for_sale_dictionary["branch"].append(branch)
                    except IndexError:
                        continue

    return pd.DataFrame(for_sale_dictionary)

def get_property_postcode(data: pd.DataFrame) -> pd.DataFrame:
    """Returns the right move property data with the post code extracted from the
    description.

    """
    _data = data.copy()
    _data["post code"] = "0"
    check_post_code = re.compile("^([A-Z]{1}|[A-Z]{2})([0-9]{1}|[0-9]{2})$")

    for index in _data.index:
        post_code = _data["description"][index].split(", ")[-1]
        match = check_post_code.match(post_code)
        if match: 
            _data.at[index, "post code"] = post_code
            
    return _data

def get_property_type(data: pd.DataFrame) -> pd.DataFrame:
    """Returns the right move property data with the property type extracted from the
    description.

    """
    _data = data.copy()
    _data["property type"] = "0"

    for index in _data.index:
        description = _data["description"][index].lower().replace("-", " ")
        for property_type in PROPERTY_TYPES:
            if property_type in description:
                _data.at[index, "property type"] = property_type

    return _data

def get_your_move_all_houses_for_sale() -> pd.DataFrame:
    """Returns the houses for sale on your move across all branches.
    """
    branches = get_your_move_branches()
    all_houses_for_sale = False

    for branch in branches:
        if all_houses_for_sale is False:
            all_houses_for_sale = get_your_move_houses_for_sale_at_branch(branch)
        else:
            houses_for_sale_at_branch = get_your_move_houses_for_sale_at_branch(branch)
            all_houses_for_sale = pd.concat(
                [houses_for_sale_at_branch, all_houses_for_sale], axis=0
            )

    all_houses_for_sale.reset_index(inplace=True, drop=True)
    all_houses_for_sale = get_property_postcode(all_houses_for_sale)
    all_houses_for_sale = get_property_type(all_houses_for_sale)

    return all_houses_for_sale

def get_rightmove_sold_address(property_data: str) -> str:
    """Returns the address from some web-scraped property data.
    """
    match = re.compile('.+,propertyType').search(property_data)
    _match = match.group()
    _item = ""
    for item in _match.split(",")[:-1]:
        _item += item + ","
    address = _item[:-1]
    return address

def get_rightmove_sold_property_type(property_data: str) -> str:
    """Returns the property type from some web-scraped property data.
    """
    match = re.compile('propertyType:.+,bedrooms').search(property_data)
    _match = match.group()
    _pattern = re.compile(':.+,')
    match = _pattern.search(_match)
    property_type = match.group()[1:-1]
    return property_type

def get_rightmove_sold_bedrooms(property_data: str) -> str:
    """Returns the bedroom information from some web-scraped property data.
    """
    match = re.compile('bedrooms:.+,images').search(property_data)
    _match = match.group()
    _pattern = re.compile(':.+,')
    match = _pattern.search(_match)
    bedrooms = match.group()[1:-1]
    return bedrooms

def get_rightmove_sold_price_and_date(property_data: str) -> str:
    """Returns the sale information from some web-scraped property data.
    """
    match = re.compile('transactions:\[.+,location:').search(property_data)
    _match = match.group()
    match = re.compile('{.+}').search(_match)
    sold_info = match.group().split('},{')
    sale_info = []
    for _property in sold_info:
        price_match = re.compile('£.+,dateSold').search(_property)
        price = price_match.group().split(",d")[0]
        date_match = re.compile('dateSold:.+,tenure').search(_property)
        _date = date_match.group().split(":")[1]
        date = _date.split(",")[0]
        sale_info += [(price, date)]
        
    return sale_info

def get_rightmove_sold_properties_by_location(branch: str) -> pd.DataFrame:
    """Returns the houses sold on rightmove for a provided locations.
    """
    URL = (
        f"https://www.rightmove.co.uk/house-prices/{branch}.html?"
        f"country=england&searchLocation={branch}"
    )
    page = requests.get(URL)
    soup = bs(page.content, "html.parser")
    
    results = soup.findAll('script', string=re.compile("window.__PRELOADED_STATE__"))
    sold_data = False
    print(branch)
    for result in results:
        _results = result.text.split(r'{"address":')
        some_results = _results[1:-1] + [_results[-1].split("detailUrl")[0]]
        for _property in range(len(some_results)):
            individual_property = some_results[_property].replace('"', '')
            address = get_rightmove_sold_address(individual_property)
            property_type = get_rightmove_sold_property_type(individual_property)
            bedrooms = get_rightmove_sold_bedrooms(individual_property)
            sale_info = get_rightmove_sold_price_and_date(individual_property)

            for sale in sale_info:
                if sold_data is False:
                    sold_data = pd.DataFrame(
                        {
                            "location": branch,
                            "address": address,
                            "property type": property_type,
                            "bedrooms": bedrooms,
                            "sale price": sale[0],
                            "sale date": sale[1],
                        }, 
                        index=[0]
                    )
                else:
                    new_sold_data = pd.DataFrame(
                        {
                            "location": branch,
                            "address": address,
                            "property type": property_type,
                            "bedrooms": bedrooms,
                            "sale price": sale[0],
                            "sale date": sale[1],
                        },
                        index=[0]
                    )
                    sold_data = pd.concat(
                        [sold_data, new_sold_data]
                    )
    if sold_data is False:
        return pd.DataFrame(
            {
                "location": [0],
                "address": [0],
                "property type": [0],
                "bedrooms": [0],
                "sale price": [0],
                "sale date": [0],
            },
            index=[0]
        )

    sold_data.reset_index(drop=True, inplace=True)

    return sold_data

def get_rightmove_all_sold_houses() -> pd.DataFrame:
    """Returns the houses sold on rightmove across all your move branch locations.
    """
    branches = get_your_move_branches()
    all_sold_houses = False

    for branch in branches:
        if all_sold_houses is False:
            all_sold_houses = get_rightmove_sold_properties_by_location(branch)
        else:
            houses_sold_at_location = get_rightmove_sold_properties_by_location(branch)
            all_sold_houses = pd.concat(
                [houses_sold_at_location, all_sold_houses], axis=0
            )

    all_sold_houses.reset_index(inplace=True, drop=True)

    return all_sold_houses