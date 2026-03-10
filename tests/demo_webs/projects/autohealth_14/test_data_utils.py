"""Tests for autohealth_14 data_utils (extract and transform helpers)."""

from autoppia_iwa.src.demo_webs.projects.autohealth_14 import data_utils


class TestExtractHealthDataset:
    def test_none_returns_none(self):
        assert data_utils.extract_health_dataset(None, "appointments") is None

    def test_list_passthrough(self):
        payload = [{"id": 1}, {"id": 2}]
        assert data_utils.extract_health_dataset(payload, "x") == payload

    def test_dict_with_entity_type_list_returns_list(self):
        payload = {"appointments": [{"id": 1, "doctorName": "Dr. X"}]}
        assert data_utils.extract_health_dataset(payload, "appointments") == [{"id": 1, "doctorName": "Dr. X"}]

    def test_dict_missing_key_returns_none(self):
        payload = {"doctors": []}
        assert data_utils.extract_health_dataset(payload, "appointments") is None

    def test_dict_value_not_list_returns_none(self):
        payload = {"appointments": "not-a-list"}
        assert data_utils.extract_health_dataset(payload, "appointments") is None


class TestTransformAppointmentsToModified:
    def test_camel_case_to_snake(self):
        appointments = [
            {"id": 1, "doctorName": "Dr. A", "specialty": "Cardiology"},
        ]
        result = data_utils.transform_appointments_to_modified(appointments)
        assert result == [
            {"id": 1, "doctor_name": "Dr. A", "speciality": "Cardiology"},
        ]

    def test_empty_list(self):
        assert data_utils.transform_appointments_to_modified([]) == []


class TestTransformDoctorsToModified:
    def test_name_and_specialty_and_fee(self):
        doctors = [
            {"name": "Dr. B", "specialty": "GP", "consultationFee": 100},
        ]
        result = data_utils.transform_doctors_to_modified(doctors)
        assert result[0]["doctor_name"] == "Dr. B"
        assert result[0]["speciality"] == "GP"
        assert result[0]["consultation_fee"] == 100
        assert result[0]["pricing"] == "under150"

    def test_pricing_under150(self):
        result = data_utils.transform_doctors_to_modified([{"consultationFee": 100}])
        assert result[0]["pricing"] == "under150"

    def test_pricing_150_250(self):
        result = data_utils.transform_doctors_to_modified([{"consultationFee": 200}])
        assert result[0]["pricing"] == "150-250"

    def test_pricing_250_plus(self):
        result = data_utils.transform_doctors_to_modified([{"consultationFee": 300}])
        assert result[0]["pricing"] == "250+"

    def test_rating_clamped_and_rounded(self):
        result = data_utils.transform_doctors_to_modified([{"rating": 4.567}])
        assert result[0]["rating"] == 4.6

    def test_primary_language_from_languages(self):
        result = data_utils.transform_doctors_to_modified([{"languages": ["English", "Spanish"]}])
        assert result[0]["primary_language"] == "English"

    def test_primary_language_empty(self):
        result = data_utils.transform_doctors_to_modified([{}])
        assert result[0].get("primary_language") is None


class TestTransformPrescriptionsToModified:
    def test_camel_to_snake(self):
        prescriptions = [
            {
                "medicineName": "Aspirin",
                "doctorName": "Dr. C",
                "startDate": "2025-01-01",
                "refillsRemaining": 3,
            },
        ]
        result = data_utils.transform_prescriptions_to_modified(prescriptions)
        assert result[0]["medicine_name"] == "Aspirin"
        assert result[0]["doctor_name"] == "Dr. C"
        assert result[0]["start_date"] == "2025-01-01"
        assert result[0]["refills_remaining"] == 3


class TestTransformMedicalRecordsToModified:
    def test_camel_to_snake(self):
        records = [
            {"title": "Checkup", "date": "2025-01-01", "type": "note", "doctorName": "Dr. D"},
        ]
        result = data_utils.transform_medical_records_to_modified(records)
        assert result[0]["record_title"] == "Checkup"
        assert result[0]["record_date"] == "2025-01-01"
        assert result[0]["record_type"] == "note"
        assert result[0]["doctor_name"] == "Dr. D"
