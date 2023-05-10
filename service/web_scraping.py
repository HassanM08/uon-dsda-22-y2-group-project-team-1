import re
import requests
from typing import Dict

import pandas as pd
from bs4 import BeautifulSoup as bs

from service import BRANCHES_URL, ESTATE_AGENTS_URL


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
    property_types = [
        "semi detached",
        "link detached",
        "detached",
        "end terrace",
        "mid terrace",
        "flat",
        "bungalow",
        "land/plot",
        "house",
        "property"
    ]
    _data = data.copy()
    _data["property type"] = "0"

    for index in _data.index:
        description = _data["description"][index].lower().replace("-", " ")
        for type in property_types:
            if type in description:
                _data["property type"] = type
            
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
