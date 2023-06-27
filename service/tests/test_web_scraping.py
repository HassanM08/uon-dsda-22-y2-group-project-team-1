import pandas as pd

from service.web_scraping import get_property_postcode, get_property_type


class TestGetPropertyPostcode:
    """
    """

    def test_output_is_as_expected(self):
        """Tests that the get_property_postcode function extracts post-codes as
        expected.

        """
        # SETUP
        descriptions = [
            "something, here, DE14",
            "another, thing, here, SW4",
            "third, description, B5",
            "fourth, B23",
            "incorrect, postcode, b 23"
        ]
        post_codes = ["DE14", "SW4", "B5", "B23", "0"]
        input_data = pd.DataFrame({"description": descriptions})
        expected_output = pd.DataFrame(
            {
                "description": descriptions,
                "post code": post_codes,
            }
        )

        # CALL
        results = get_property_postcode(input_data)

        # ASSERT
        pd.testing.assert_frame_equal(results, expected_output)


class TestGetPropertyType:
    """
    """

    def test_output_is_as_expected(self):
        """Tests that the get_property_type function extracts property types as
        expected.

        """
        # SETUP
        descriptions = [
            "something, semi-detached, DE14",
            "another, link-detached, here, SW4",
            "third, detached, B5",
            "fourth, flat, B23",
            "incorrect, mansion, b 23"
        ]
        property_type = ["semi detached", "link detached", "detached", "flat", "0"]
        input_data = pd.DataFrame({"description": descriptions})
        expected_output = pd.DataFrame(
            {
                "description": descriptions,
                "property type": property_type,
            }
        )

        # CALL
        results = get_property_type(input_data)

        # ASSERT
        pd.testing.assert_frame_equal(results, expected_output)