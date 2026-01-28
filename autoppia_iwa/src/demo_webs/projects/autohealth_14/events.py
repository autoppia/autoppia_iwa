from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue


class BookAppointmentEvent(Event, BaseEventValidator):
    event_name: str = "BOOK_APPOINTMENT"
    # Core appointment fields (semantic values for prompts)
    date: str | None = None
    doctor_name: str | None = None
    speciality: str | None = None
    time: str | None = None
    # Patient information fields (semantic values for prompts)
    patient_name: str | None = None
    patient_email: str | None = None
    patient_phone: str | None = None
    reason_for_visit: str | None = None
    # Insurance fields
    insurance_provider: str | None = None
    insurance_number: str | None = None
    # Emergency contact fields
    emergency_contact: str | None = None
    emergency_phone: str | None = None
    # Additional fields
    notes: str | None = None
    # Action and source metadata
    action: str | None = None  # "open_booking_modal" or "confirm_booking"
    success: bool | None = None  # True when booking confirmed
    source: str | None = None  # "appointments_table", "doctors_page", etc.

    class ValidationCriteria(BaseModel):
        # Core appointment fields
        date: str | CriterionValue | None = None
        doctor_name: str | CriterionValue | None = None
        speciality: str | CriterionValue | None = None
        time: str | CriterionValue | None = None
        # Patient information fields
        patient_name: str | CriterionValue | None = None
        patient_email: str | CriterionValue | None = None
        patient_phone: str | CriterionValue | None = None
        reason_for_visit: str | CriterionValue | None = None
        # Insurance fields
        insurance_provider: str | CriterionValue | None = None
        insurance_number: str | CriterionValue | None = None
        # Emergency contact fields
        emergency_contact: str | CriterionValue | None = None
        emergency_phone: str | CriterionValue | None = None
        # Additional fields
        notes: str | CriterionValue | None = None
        # Action and source metadata
        action: str | CriterionValue | None = None
        success: bool | CriterionValue | None = None
        source: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                # Core appointment fields
                self._validate_field(self.date, criteria.date),
                self._validate_field(self.doctor_name, criteria.doctor_name),
                self._validate_field(self.speciality, criteria.speciality),
                self._validate_field(self.time, criteria.time),
                # Patient information fields
                self._validate_field(self.patient_name, criteria.patient_name),
                self._validate_field(self.patient_email, criteria.patient_email),
                self._validate_field(self.patient_phone, criteria.patient_phone),
                self._validate_field(self.reason_for_visit, criteria.reason_for_visit),
                # Insurance fields
                self._validate_field(self.insurance_provider, criteria.insurance_provider),
                self._validate_field(self.insurance_number, criteria.insurance_number),
                # Emergency contact fields
                self._validate_field(self.emergency_contact, criteria.emergency_contact),
                self._validate_field(self.emergency_phone, criteria.emergency_phone),
                # Additional fields
                self._validate_field(self.notes, criteria.notes),
                # Action and source metadata
                self._validate_field(self.action, criteria.action),
                self._validate_field(self.success, criteria.success),
                self._validate_field(self.source, criteria.source),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "BookAppointmentEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            # Core appointment fields (map camelCase to snake_case)
            date=data.get("date"),
            doctor_name=data.get("doctorName"),
            speciality=data.get("specialty"),
            time=data.get("time"),
            # Patient information fields
            patient_name=data.get("patientName"),
            patient_email=data.get("patientEmail"),
            patient_phone=data.get("patientPhone"),
            reason_for_visit=data.get("reasonForVisit"),
            # Insurance fields
            insurance_provider=data.get("insuranceProvider"),
            insurance_number=data.get("insuranceNumber"),
            # Emergency contact fields
            emergency_contact=data.get("emergencyContact"),
            emergency_phone=data.get("emergencyPhone"),
            # Additional fields
            notes=data.get("notes"),
            # Action and source metadata
            action=data.get("action"),
            success=data.get("success"),
            source=data.get("source"),
        )


class AppointmentBookedSuccessfullyEvent(Event, BaseEventValidator):
    event_name: str = "APPOINTMENT_BOOKED_SUCCESSFULLY"
    date: str | None = None
    doctor_name: str | None = None
    emergency_contact: str | None = None
    emergency_phone: str | None = None
    insurance_number: str | None = None
    insurance_provider: str | None = None
    notes: str | None = None
    patient_name: str | None = None
    patient_email: str | None = None
    patient_phone: str | None = None
    reason_for_visit: str | None = None
    speciality: str | None = None
    time: str | None = None

    class ValidationCriteria(BaseModel):
        date: str | CriterionValue | None = None
        doctor_name: str | CriterionValue | None = None
        emergency_contact: str | CriterionValue | None = None
        emergency_phone: str | CriterionValue | None = None
        insurance_number: str | CriterionValue | None = None
        insurance_provider: str | CriterionValue | None = None
        notes: str | CriterionValue | None = None
        patient_name: str | CriterionValue | None = None
        patient_email: str | CriterionValue | None = None
        patient_phone: str | CriterionValue | None = None
        reason_for_visit: str | CriterionValue | None = None
        speciality: str | CriterionValue | None = None
        time: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.date, criteria.date),
                self._validate_field(self.doctor_name, criteria.doctor_name),
                self._validate_field(self.speciality, criteria.speciality),
                self._validate_field(self.emergency_contact, criteria.emergency_contact),
                self._validate_field(self.emergency_phone, criteria.emergency_phone),
                self._validate_field(self.insurance_number, criteria.insurance_number),
                self._validate_field(self.insurance_provider, criteria.insurance_provider),
                self._validate_field(self.notes, criteria.notes),
                self._validate_field(self.patient_name, criteria.patient_name),
                self._validate_field(self.patient_email, criteria.patient_email),
                self._validate_field(self.patient_phone, criteria.patient_phone),
                self._validate_field(self.reason_for_visit, criteria.reason_for_visit),
                self._validate_field(self.speciality, criteria.speciality),
                self._validate_field(self.time, criteria.time),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "AppointmentBookedSuccessfullyEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            date=data.get("date"),
            doctor_name=data.get("doctorName"),
            speciality=data.get("specialty"),
            emergency_contact=data.get("emergencyContact"),
            emergency_phone=data.get("emergencyPhone"),
            insurance_number=data.get("insuranceNumber"),
            insurance_provider=data.get("insuranceProvider"),
            notes=data.get("notes"),
            patient_name=data.get("patientName"),
            patient_email=data.get("patientEmail"),
            patient_phone=data.get("patientPhone"),
            reason_for_visit=data.get("reasonForVisit"),
            time=data.get("time"),
        )


class CancelBookAppointmentEvent(Event, BaseEventValidator):
    event_name: str = "CANCEL_BOOK_APPOINTMENT"
    date: str | None = None
    doctor_name: str | None = None
    speciality: str | None = None
    time: str | None = None

    class ValidationCriteria(BaseModel):
        date: str | CriterionValue | None = None
        doctor_name: str | CriterionValue | None = None
        speciality: str | CriterionValue | None = None
        time: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.date, criteria.date),
                self._validate_field(self.doctor_name, criteria.doctor_name),
                self._validate_field(self.speciality, criteria.speciality),
                self._validate_field(self.time, criteria.time),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "CancelBookAppointmentEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            date=data.get("date"),
            time=data.get("time"),
            speciality=data.get("specialty"),
            doctor_name=data.get("doctorName"),
        )


class ViewPrescriptionEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_PRESCRIPTION"
    doctor_name: str | None = None
    dosage: str | None = None
    medicine_name: str | None = None
    start_date: str | None = None
    category: str | None = None
    status: str | None = None

    class ValidationCriteria(BaseModel):
        doctor_name: str | CriterionValue | None = None
        medicine_name: str | CriterionValue | None = None
        start_date: str | CriterionValue | None = None
        dosage: str | CriterionValue | None = None
        category: str | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.doctor_name, criteria.doctor_name),
                self._validate_field(self.medicine_name, criteria.medicine_name),
                self._validate_field(self.start_date, criteria.start_date),
                self._validate_field(self.dosage, criteria.dosage),
                self._validate_field(self.category, criteria.category),
                self._validate_field(self.status, criteria.status),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewPrescriptionEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            doctor_name=data.get("doctorName"),
            medicine_name=data.get("medicineName"),
            start_date=data.get("startDate"),
            dosage=data.get("dosage"),
            category=data.get("category"),
            status=data.get("status"),
        )


class FilterBySpecialityEvent(Event, BaseEventValidator):
    event_name: str = "FILTER_BY_SPECIALTY"
    status: str | None = None

    class ValidationCriteria(BaseModel):
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.status, criteria.status),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "FilterBySpecialityEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            status=data.get("status"),
        )


class RefillRequestEvent(Event, BaseEventValidator):
    event_name: str = "REFILL_PRESCRIPTION"
    medicine_name: str | None = None


    class ValidationCriteria(BaseModel):
        medicine_name: str | CriterionValue | None = None
        doctor_name: str | CriterionValue | None = None
        dosage: str | CriterionValue | None = None
        start_date: str | CriterionValue | None = None
        category: str | CriterionValue | None = None
        status: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.medicine_name, criteria.medicine_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "RefillRequestEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            medicine_name=data.get("medicineName"),
        )


class UploadHealthDataEvent(Event, BaseEventValidator):
    event_name: str = "UPLOAD_HEALTH_DATA"
    file_count: int | None = None
    file_names: list[str] | None = None
    upload_timestamp: str | None = None

    class ValidationCriteria(BaseModel):
        file_count: int | CriterionValue | None = None
        file_names: list[str] | CriterionValue | None = None
        upload_timestamp: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.file_count, criteria.file_count),
                self._validate_field(self.file_names, criteria.file_names),
                self._validate_field(self.upload_timestamp, criteria.upload_timestamp),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "UploadHealthDataEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        raw_names = data.get("fileNames") or data.get("file_names") or []
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            file_count=data.get("fileCount") or data.get("file_count"),
            file_names=raw_names if isinstance(raw_names, list) else [],
            upload_timestamp=data.get("uploadTimestamp") or data.get("upload_timestamp"),
        )


class ViewHealthMetricsEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_HEALTH_METRICS"
    record_title: str | None = None
    record_type: str | None = None
    record_date: str | None = None

    class ValidationCriteria(BaseModel):
        record_title: str | CriterionValue | None = None
        record_type: str | CriterionValue | None = None
        record_date: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.record_title, criteria.record_title),
                self._validate_field(self.record_type, criteria.record_type),
                self._validate_field(self.record_date, criteria.record_date),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewHealthMetricsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            record_title=data.get("recordTitle"),
            record_type=data.get("recordType"),
            record_date=data.get("recordDate"),
        )


class FilterByCategoryEvent(Event, BaseEventValidator):
    event_name: str = "FILTER_BY_CATEGORY"
    category: str | None = None

    class ValidationCriteria(BaseModel):
        category: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.category, criteria.category),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "FilterByCategoryEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            category=data.get("category"),
        )


class ViewDoctorProfileEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_DOCTOR_PROFILE"
    doctor_name: str | None = None
    rating: float | None = None
    speciality: str | None = None

    class ValidationCriteria(BaseModel):
        doctor_name: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        speciality: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.doctor_name, criteria.doctor_name),
                self._validate_field(self.rating, criteria.rating),
                self._validate_field(self.speciality, criteria.speciality),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewDoctorProfileEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            doctor_name=data.get("doctorName"),
            rating=data.get("rating"),
            speciality=data.get("specialty"),
        )


class ContactDoctorEvent(Event, BaseEventValidator):
    event_name: str = "CONTACT_DOCTOR"
    # Doctor Information (constraints for benchmark verification)
    doctor_id: str | None = None
    doctor_name: str | None = None
    speciality: str | None = None
    # Patient Information
    patient_name: str | None = None
    patient_email: str | None = None
    patient_phone: str | None = None
    # Message Information (constraints for benchmark verification)
    subject: str | None = None
    message: str | None = None
    urgency: str | None = None  # "low" | "medium" | "high"
    preferred_contact_method: str | None = None  # "email" | "phone" | "either"
    appointment_request: bool | None = None
    # Action and success metadata
    action: str | None = None  # "send_message"
    success: bool | None = None  # True when contact is sent
    contact_timestamp: str | None = None  # ISO timestamp

    class ValidationCriteria(BaseModel):
        # Doctor Information
        doctor_id: str | CriterionValue | None = None
        doctor_name: str | CriterionValue | None = None
        speciality: str | CriterionValue | None = None
        # Patient Information
        patient_name: str | CriterionValue | None = None
        patient_email: str | CriterionValue | None = None
        patient_phone: str | CriterionValue | None = None
        # Message Information
        subject: str | CriterionValue | None = None
        message: str | CriterionValue | None = None
        urgency: str | CriterionValue | None = None
        preferred_contact_method: str | CriterionValue | None = None
        appointment_request: bool | CriterionValue | None = None
        # Action and success metadata
        action: str | CriterionValue | None = None
        success: bool | CriterionValue | None = None
        contact_timestamp: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.doctor_id, criteria.doctor_id),
                self._validate_field(self.doctor_name, criteria.doctor_name),
                self._validate_field(self.speciality, criteria.speciality),
                self._validate_field(self.patient_name, criteria.patient_name),
                self._validate_field(self.patient_email, criteria.patient_email),
                self._validate_field(self.patient_phone, criteria.patient_phone),
                self._validate_field(self.subject, criteria.subject),
                self._validate_field(self.message, criteria.message),
                self._validate_field(self.urgency, criteria.urgency),
                self._validate_field(self.preferred_contact_method, criteria.preferred_contact_method),
                self._validate_field(self.appointment_request, criteria.appointment_request),
                self._validate_field(self.action, criteria.action),
                self._validate_field(self.success, criteria.success),
                self._validate_field(self.contact_timestamp, criteria.contact_timestamp),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ContactDoctorEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            user_id=base_event.user_id,
            web_agent_id=base_event.web_agent_id,
            # Doctor Information (map camelCase to snake_case)
            doctor_id=data.get("doctorId"),
            doctor_name=data.get("doctorName"),
            speciality=data.get("specialty"),
            # Patient Information
            patient_name=data.get("patientName"),
            patient_email=data.get("patientEmail"),
            patient_phone=data.get("patientPhone"),
            # Message Information
            subject=data.get("subject"),
            message=data.get("message"),
            urgency=data.get("urgency"),
            preferred_contact_method=data.get("preferredContactMethod"),
            appointment_request=data.get("appointmentRequest"),
            # Action and success metadata
            action=data.get("action"),
            success=data.get("success"),
            contact_timestamp=data.get("contactTimestamp"),
        )


class DoctorContactedSuccessfullyEvent(Event, BaseEventValidator):
    event_name: str = "DOCTOR_CONTACTED_SUCCESSFULLY"
    doctor_name: str | None = None
    message: str | None = None
    patient_email: str | None = None
    patient_name: str | None = None
    patient_phone: str | None = None
    preferred_contact_method: str | None = None
    speciality: str | None = None
    subject: str | None = None
    urgency: str | None = None
    appointment_request: bool | None = None

    class ValidationCriteria(BaseModel):
        doctor_name: str | CriterionValue | None = None
        message: str | CriterionValue | None = None
        patient_email: str | CriterionValue | None = None
        patient_name: str | CriterionValue | None = None
        patient_phone: str | CriterionValue | None = None
        preferred_contact_method: str | CriterionValue | None = None
        speciality: str | CriterionValue | None = None
        subject: str | CriterionValue | None = None
        urgency: str | CriterionValue | None = None
        appointment_request: bool | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.doctor_name, criteria.doctor_name),
                self._validate_field(self.message, criteria.message),
                self._validate_field(self.patient_email, criteria.patient_email),
                self._validate_field(self.patient_name, criteria.patient_name),
                self._validate_field(self.patient_phone, criteria.patient_phone),
                self._validate_field(self.preferred_contact_method, criteria.preferred_contact_method),
                self._validate_field(self.speciality, criteria.speciality),
                self._validate_field(self.subject, criteria.subject),
                self._validate_field(self.urgency, criteria.urgency),
                self._validate_field(self.appointment_request, criteria.appointment_request),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "DoctorContactedSuccessfullyEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        return cls(
            event_name=base_event.event_name,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            timestamp=base_event.timestamp,
            doctor_name=data.get("doctorName"),
            message=data.get("message"),
            patient_email=data.get("patientEmail"),
            patient_name=data.get("patientName"),
            patient_phone=data.get("patientPhone"),
            preferred_contact_method=data.get("preferredContactMethod"),
            speciality=data.get("specialty"),
            subject=data.get("subject"),
            urgency=data.get("urgency"),
            appointment_request=data.get("appointmentRequest"),
        )


class CancelContactDoctorEvent(Event, BaseEventValidator):
    event_name: str = "CANCEL_CONTACT_DOCTOR"
    doctor_name: str | None = None
    speciality: str | None = None

    class ValidationCriteria(BaseModel):
        doctor_name: str | CriterionValue | None = None
        speciality: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.doctor_name, criteria.doctor_name),
                self._validate_field(self.speciality, criteria.speciality),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "CancelContactDoctorEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            doctor_name=data.get("doctorName"),
            speciality=data.get("specialty"),
        )


class ViewReviewsEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_REVIEWS"
    doctor_name: str | None = None
    rating: float | None = None
    speciality: str | None = None

    class ValidationCriteria(BaseModel):
        doctor_name: str | CriterionValue | None = None
        rating: float | CriterionValue | None = None
        speciality: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.doctor_name, criteria.doctor_name),
                self._validate_field(self.speciality, criteria.speciality),
                self._validate_field(self.rating, criteria.rating),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewReviewsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            doctor_name=data.get("doctorName"),
            speciality=data.get("specialty"),
            rating=data.get("rating"),
        )


class SortReviewsEvent(Event, BaseEventValidator):
    event_name: str = "SORT_REVIEWS"
    doctor_name: str | None = None
    sort_order: str | None = None
    speciality: str | None = None

    class ValidationCriteria(BaseModel):
        doctor_name: str | CriterionValue | None = None
        sort_order: str | CriterionValue | None = None
        speciality: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.doctor_name, criteria.doctor_name),
                self._validate_field(self.sort_order, criteria.sort_order),
                self._validate_field(self.speciality, criteria.speciality),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SortReviewsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            doctor_name=data.get("doctorName"),
            speciality=data.get("specialty"),
            sort_order=data.get("sortOrder"),
        )


class FilterReviewsEvent(Event, BaseEventValidator):
    event_name: str = "FILTER_REVIEWS"
    doctor_name: str | None = None
    filter_rating: int | None = None
    speciality: str | None = None

    class ValidationCriteria(BaseModel):
        doctor_name: str | CriterionValue | None = None
        filter_rating: int | CriterionValue | None = None
        speciality: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.doctor_name, criteria.doctor_name),
                self._validate_field(self.filter_rating, criteria.filter_rating),
                self._validate_field(self.speciality, criteria.speciality),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "FilterReviewsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            doctor_name=data.get("doctorName"),
            speciality=data.get("specialty"),
            filter_rating=data.get("filterRating"),
        )


class CancelViewReviewsEvent(Event, BaseEventValidator):
    event_name: str = "CANCEL_VIEW_REVIEWS"
    doctor_name: str | None = None
    speciality: str | None = None

    class ValidationCriteria(BaseModel):
        doctor_name: str | CriterionValue | None = None
        speciality: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.doctor_name, criteria.doctor_name),
                self._validate_field(self.speciality, criteria.speciality),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "CancelViewReviewsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data")
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            doctor_name=data.get("doctorName"),
            speciality=data.get("specialty"),
        )


EVENTS = [
    BookAppointmentEvent,
    AppointmentBookedSuccessfullyEvent,
    CancelBookAppointmentEvent,
    ViewPrescriptionEvent,
    FilterBySpecialityEvent,
    RefillRequestEvent,
    UploadHealthDataEvent,
    ViewHealthMetricsEvent,
    FilterByCategoryEvent,
    ViewDoctorProfileEvent,
    ContactDoctorEvent,
    DoctorContactedSuccessfullyEvent,
    CancelContactDoctorEvent,
    ViewReviewsEvent, 
    FilterReviewsEvent,
    SortReviewsEvent,
    CancelViewReviewsEvent,
]

BACKEND_EVENT_TYPES = {
    "BOOK_APPOINTMENT": BookAppointmentEvent,
    "APPOINTMENT_BOOKED_SUCCESSFULLY": AppointmentBookedSuccessfullyEvent,
    "CANCEL_BOOK_APPOINTMENT": CancelBookAppointmentEvent,
    "VIEW_PRESCRIPTION": ViewPrescriptionEvent,
    "FILTER_BY_SPECIALTY": FilterBySpecialityEvent,
    "REFILL_PRESCRIPTION": RefillRequestEvent,
    "UPLOAD_HEALTH_DATA": UploadHealthDataEvent,
    "VIEW_HEALTH_METRICS": ViewHealthMetricsEvent,
    "FILTER_BY_CATEGORY": FilterByCategoryEvent,
    "VIEW_DOCTOR_PROFILE": ViewDoctorProfileEvent,
    "CONTACT_DOCTOR": ContactDoctorEvent,
    "DOCTOR_CONTACTED_SUCCESSFULLY": DoctorContactedSuccessfullyEvent,
    "CANCEL_CONTACT_DOCTOR": CancelContactDoctorEvent,
    "VIEW_REVIEWS": ViewReviewsEvent,
    "FILTER_REVIEWS": FilterReviewsEvent,
    "SORT_REVIEWS": SortReviewsEvent,
    "CANCEL_VIEW_REVIEWS": CancelViewReviewsEvent,
}
