import unittest

from ecorecord_triage.dataset import build_dataset
from ecorecord_triage.validators import (
    check_basis_of_record, check_coordinates, check_dates,
    check_identification, check_verifiability,
)


class ValidatorTests(unittest.TestCase):
    def test_dataset_mutation_labels_match_reference_validators(self):
        # Controlled mutations are independently labelled in the generator.
        for case in build_dataset():
            record = case["record"]
            actual = set(
                check_basis_of_record(record)
                + check_coordinates(record)
                + check_dates(record)
                + check_verifiability(record)
                + check_identification(record)
            )
            self.assertEqual(actual, set(case["expected_issue_codes"]), case["case_id"])

    def test_zero_coordinate(self):
        self.assertEqual(check_coordinates({"decimalLatitude": 0, "decimalLongitude": 0}), ["ZERO_COORDINATE"])

    def test_coordinate_bounds(self):
        self.assertEqual(check_coordinates({"decimalLatitude": 91, "decimalLongitude": 0}), ["COORDINATE_OUT_OF_RANGE"])

    def test_date_mismatch(self):
        record = {"eventDate": "2024-06-01", "year": 2023, "month": 6, "day": 1}
        self.assertEqual(check_dates(record), ["RECORDED_DATE_MISMATCH"])

    def test_specimen_does_not_require_media_or_ids(self):
        record = {"basisOfRecord": "PreservedSpecimen", "hasMedia": False, "identificationCount": 0}
        self.assertEqual(check_verifiability(record), [])
        self.assertEqual(check_identification(record), [])

    def test_invalid_basis_of_record(self):
        self.assertEqual(check_basis_of_record({"basisOfRecord": "MadeUp"}), ["BASIS_OF_RECORD_INVALID"])


if __name__ == "__main__":
    unittest.main()
