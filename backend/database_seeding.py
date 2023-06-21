from datetime import datetime

from service.web_scraping import get_your_move_all_houses_for_sale
from backend.database_library import table_from_df


def run_script():
    
    start_time = datetime.now()
    print(f"{start_time} Running seeding script...")

    for_sale_data = get_your_move_all_houses_for_sale()
    table_from_df(for_sale_data, "for_sale")

    end_time = datetime.now()
    total_time = end_time - start_time
    print(f"Total time: {total_time}")


if __name__ == "__main__":
    run_script()