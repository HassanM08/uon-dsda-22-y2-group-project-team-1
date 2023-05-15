import pandas as pd
import numpy as np

def get_postcode_mapping_table():

    postcode = pd.read_csv('postcode_map.csv')

    return postcode