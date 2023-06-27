from datetime import datetime

from service.web_scraping import (
    get_rightmove_all_sold_houses, get_your_move_all_houses_for_sale
)
from backend.database_library import table_from_df


def seed_for_sale_houses():
    
    start_time = datetime.now()
    print(f"{start_time} Running seeding script...")

    houses_for_sale = get_your_move_all_houses_for_sale()
    table_from_df(houses_for_sale, "houses_for_sale")
    end_time = datetime.now()
    total_time = end_time - start_time

    print(houses_for_sale)
    print(f"Total time: {total_time}")


def seed_sold_houses():
    
    start_time = datetime.now()
    print(f"{start_time} Running seeding script...")

    sold_houses = get_rightmove_all_sold_houses()
    table_from_df(sold_houses, "sold_houses")
    end_time = datetime.now()
    total_time = end_time - start_time

    print(sold_houses)
    print(f"Total time: {total_time}")


if __name__ == "__main__":
    seed_sold_houses()
    seed_for_sale_houses()

