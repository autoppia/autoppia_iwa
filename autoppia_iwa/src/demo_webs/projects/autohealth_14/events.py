from pydantic import BaseModel

from autoppia_iwa.src.demo_webs.projects.base_events import BaseEventValidator, Event
from autoppia_iwa.src.demo_webs.projects.criterion_helper import CriterionValue


class BookAppointmentEvent(Event, BaseEventValidator):
    event_name: str = "BOOK_APPOINTMENT"
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
        if criteria is None:
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
    def parse(cls, backend_event: "BackendEvent") -> "BookAppointmentEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data") or {}
        doctor = data.get("doctor") if isinstance(data.get("doctor"), dict) else {}
        appointment = data.get("appointment") if isinstance(data.get("appointment"), dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            date=data.get("date") or appointment.get("date"),
            doctor_name=data.get("doctorName") or doctor.get("name"),
            speciality=data.get("specialty") or doctor.get("specialty"),
            time=data.get("time") or appointment.get("time"),
        )


class OpenAppointmentFormEvent(Event, BaseEventValidator):
    """Fired when user clicks Book Appointment and opens the appointment booking form/modal."""
    event_name: str = "OPEN_APPOINTMENT_FORM"
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
        if criteria is None:
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
    def parse(cls, backend_event: "BackendEvent") -> "OpenAppointmentFormEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data") or {}
        doctor = data.get("doctor") if isinstance(data.get("doctor"), dict) else {}
        appointment = data.get("appointment") if isinstance(data.get("appointment"), dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            date=data.get("date") or appointment.get("date"),
            doctor_name=data.get("doctorName") or doctor.get("name") or appointment.get("doctorName"),
            speciality=data.get("specialty") or doctor.get("specialty") or appointment.get("specialty"),
            time=data.get("time") or appointment.get("time"),
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
        data = data.get("data") or {}
        appointment = data.get("appointment") if isinstance(data.get("appointment"), dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            date=data.get("date") or appointment.get("date"),
            doctor_name=data.get("doctorName") or appointment.get("doctorName"),
            speciality=data.get("specialty") or appointment.get("specialty"),
            emergency_contact=data.get("emergencyContact"),
            emergency_phone=data.get("emergencyPhone"),
            insurance_number=data.get("insuranceNumber"),
            insurance_provider=data.get("insuranceProvider"),
            notes=data.get("notes"),
            patient_name=data.get("patientName"),
            patient_email=data.get("patientEmail"),
            patient_phone=data.get("patientPhone"),
            reason_for_visit=data.get("reasonForVisit"),
            time=data.get("time") or appointment.get("time"),
        )


class RequestAppointmentEvent(Event, BaseEventValidator):
    """Fired when user submits the homepage Request Appointment form (quick appointment hero)."""
    event_name: str = "REQUEST_APPOINTMENT"
    patient_name: str | None = None
    patient_email: str | None = None
    patient_phone: str | None = None
    specialty: str | None = None

    class ValidationCriteria(BaseModel):
        patient_name: str | CriterionValue | None = None
        patient_email: str | CriterionValue | None = None
        patient_phone: str | CriterionValue | None = None
        specialty: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.patient_name, criteria.patient_name),
                self._validate_field(self.patient_email, criteria.patient_email),
                self._validate_field(self.patient_phone, criteria.patient_phone),
                self._validate_field(self.specialty, criteria.specialty),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "RequestAppointmentEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data") if isinstance(data, dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            patient_name=data.get("patientName"),
            patient_email=data.get("patientEmail"),
            patient_phone=data.get("patientPhone"),
            specialty=data.get("specialty"),
        )


class RequestQuickAppointmentEvent(Event, BaseEventValidator):
    """Fired when user submits the homepage quick appointment form (hero); shows 'We will contact you' popup."""
    event_name: str = "REQUEST_QUICK_APPOINTMENT"
    patient_name: str | None = None
    patient_email: str | None = None
    patient_phone: str | None = None
    specialty: str | None = None

    class ValidationCriteria(BaseModel):
        patient_name: str | CriterionValue | None = None
        patient_email: str | CriterionValue | None = None
        patient_phone: str | CriterionValue | None = None
        specialty: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.patient_name, criteria.patient_name),
                self._validate_field(self.patient_email, criteria.patient_email),
                self._validate_field(self.patient_phone, criteria.patient_phone),
                self._validate_field(self.specialty, criteria.specialty),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "RequestQuickAppointmentEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data") if isinstance(data, dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            patient_name=data.get("patientName"),
            patient_email=data.get("patientEmail"),
            patient_phone=data.get("patientPhone"),
            specialty=data.get("specialty"),
        )


class SearchAppointmentEvent(Event, BaseEventValidator):
    """Fired when user clicks Search on the Appointments page (applies doctor/specialty/date filters)."""
    event_name: str = "SEARCH_APPOINTMENT"
    filter_type: str | None = None
    doctor_name: str | None = None
    specialty: str | None = None
    date: str | None = None

    class ValidationCriteria(BaseModel):
        filter_type: str | CriterionValue | None = None
        doctor_name: str | CriterionValue | None = None
        specialty: str | CriterionValue | None = None
        date: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.filter_type, criteria.filter_type),
                self._validate_field(self.doctor_name, criteria.doctor_name),
                self._validate_field(self.specialty, criteria.specialty),
                self._validate_field(self.date, criteria.date),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SearchAppointmentEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data") if isinstance(data, dict) else {}
        data = data or {}
        doctor = data.get("doctor") if isinstance(data.get("doctor"), dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            filter_type=data.get("filterType"),
            doctor_name=data.get("doctorName") or doctor.get("name"),
            specialty=data.get("specialty") or doctor.get("specialty"),
            date=data.get("date"),
        )


class SearchPrescriptionEvent(Event, BaseEventValidator):
    """Fired when user clicks Search on the Prescriptions page (applies medicine/doctor filters)."""
    event_name: str = "SEARCH_PRESCRIPTION"
    medicine_name: str | None = None
    doctor_name: str | None = None

    class ValidationCriteria(BaseModel):
        medicine_name: str | CriterionValue | None = None
        doctor_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.medicine_name, criteria.medicine_name),
                self._validate_field(self.doctor_name, criteria.doctor_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SearchPrescriptionEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data") or {}
        prescription = data.get("prescription") if isinstance(data.get("prescription"), dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            medicine_name=data.get("medicine") or prescription.get("medicineName"),
            doctor_name=data.get("doctor") or prescription.get("doctorName"),
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
        data = data.get("data") or {}
        prescription = data.get("prescription") if isinstance(data.get("prescription"), dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            doctor_name=data.get("doctorName") or prescription.get("doctorName"),
            medicine_name=data.get("medicineName") or prescription.get("medicineName"),
            start_date=data.get("startDate") or prescription.get("startDate"),
            dosage=data.get("dosage") or prescription.get("dosage"),
            category=data.get("category") or prescription.get("category"),
            status=data.get("status") or prescription.get("status"),
        )


class RefillRequestEvent(Event, BaseEventValidator):
    event_name: str = "REFILL_PRESCRIPTION"
    medicine_name: str | None = None

    class ValidationCriteria(BaseModel):
        medicine_name: str | CriterionValue | None = None

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
        data = data.get("data") or {}
        prescription = data.get("prescription") if isinstance(data.get("prescription"), dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            medicine_name=data.get("medicineName") or prescription.get("medicineName"),
        )


class SearchMedicalAnalysisEvent(Event, BaseEventValidator):
    """Fired when user clicks Search on the Medical Records page (applies title/doctor filters)."""
    event_name: str = "SEARCH_MEDICAL_ANALYSIS"
    record_title: str | None = None
    doctor_name: str | None = None
    source: str | None = None
    action: str | None = None

    class ValidationCriteria(BaseModel):
        record_title: str | CriterionValue | None = None
        doctor_name: str | CriterionValue | None = None
        source: str | CriterionValue | None = None
        action: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.record_title, criteria.record_title),
                self._validate_field(self.doctor_name, criteria.doctor_name),
                self._validate_field(self.source, criteria.source),
                self._validate_field(self.action, criteria.action),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SearchMedicalAnalysisEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data") or {}
        record = data.get("record") if isinstance(data.get("record"), dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            record_title=data.get("title") or record.get("title"),
            doctor_name=data.get("doctor") or record.get("doctorName"),
            source=data.get("source"),
            action=data.get("action"),
        )


class ViewMedicalAnalysisEvent(Event, BaseEventValidator):
    """Fired when user clicks View Analysis on a medical analysis card."""
    event_name: str = "VIEW_MEDICAL_ANALYSIS"
    record_title: str | None = None
    record_type: str | None = None
    record_date: str | None = None
    doctor_name: str | None = None

    class ValidationCriteria(BaseModel):
        record_title: str | CriterionValue | None = None
        record_type: str | CriterionValue | None = None
        record_date: str | CriterionValue | None = None
        doctor_name: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if criteria is None:
            return True
        return all(
            [
                self._validate_field(self.record_title, criteria.record_title),
                self._validate_field(self.record_type, criteria.record_type),
                self._validate_field(self.record_date, criteria.record_date),
                self._validate_field(self.doctor_name, criteria.doctor_name),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "ViewMedicalAnalysisEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data") or {}
        record = data.get("record") if isinstance(data.get("record"), dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            record_title=data.get("title") or record.get("title"),
            record_type=data.get("type") or record.get("type"),
            record_date=data.get("date") or record.get("date"),
            doctor_name=data.get("doctorName") or record.get("doctorName"),
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
        data = data.get("data") if isinstance(data, dict) else {}
        data = data or {}
        doctor = data.get("doctor") if isinstance(data.get("doctor"), dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            doctor_name=data.get("doctorName") or doctor.get("name"),
            rating=data.get("rating") if data.get("rating") is not None else doctor.get("rating"),
            speciality=data.get("specialty") or doctor.get("specialty"),
        )


class ViewDoctorEducationEvent(Event, BaseEventValidator):
    """Fired when user opens the Education & Certifications tab on a doctor profile."""
    event_name: str = "VIEW_DOCTOR_EDUCATION"
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
    def parse(cls, backend_event: "BackendEvent") -> "ViewDoctorEducationEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data") if isinstance(data, dict) else {}
        data = data or {}
        doctor = data.get("doctor") if isinstance(data.get("doctor"), dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            doctor_name=data.get("doctorName") or doctor.get("name"),
            speciality=data.get("specialty") or doctor.get("specialty"),
        )


class SearchDoctorsEvent(Event, BaseEventValidator):
    """Fired when user clicks Search on the Doctors page (applies name/specialty filters)."""
    event_name: str = "SEARCH_DOCTORS"
    search_term: str | None = None
    specialty: str | None = None

    class ValidationCriteria(BaseModel):
        search_term: str | CriterionValue | None = None
        specialty: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.search_term, criteria.search_term),
                self._validate_field(self.specialty, criteria.specialty),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "SearchDoctorsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data") if isinstance(data, dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            search_term=data.get("searchTerm"),
            specialty=data.get("specialty"),
        )


class OpenContactDoctorFormEvent(Event, BaseEventValidator):
    """Fired when user clicks Contact Doctor and opens the contact form modal."""
    event_name: str = "OPEN_CONTACT_DOCTOR_FORM"
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
    def parse(cls, backend_event: "BackendEvent") -> "OpenContactDoctorFormEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data") or {}
        doctor = data.get("doctor") if isinstance(data.get("doctor"), dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            doctor_name=data.get("doctorName") or doctor.get("name"),
            rating=data.get("rating") if data.get("rating") is not None else doctor.get("rating"),
            speciality=data.get("specialty") or doctor.get("specialty"),
        )


class ContactDoctorEvent(Event, BaseEventValidator):
    event_name: str = "CONTACT_DOCTOR"
    doctor_name: str | None = None
    speciality: str | None = None
    rating: float | None = None

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
    def parse(cls, backend_event: "BackendEvent") -> "ContactDoctorEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data") or {}
        doctor = data.get("doctor") if isinstance(data.get("doctor"), dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            user_id=base_event.user_id,
            web_agent_id=base_event.web_agent_id,
            doctor_name=data.get("doctorName") or doctor.get("name"),
            rating=data.get("rating") if data.get("rating") is not None else doctor.get("rating"),
            speciality=data.get("specialty") or doctor.get("specialty"),
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


class ViewReviewClickedEvent(Event, BaseEventValidator):
    event_name: str = "VIEW_REVIEWS_CLICKED"
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
    def parse(cls, backend_event: "BackendEvent") -> "ViewReviewClickedEvent":
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


class FilterDoctorReviewsEvent(Event, BaseEventValidator):
    """Fired when user filters or sorts doctor reviews (by star rating and/or sort order)."""
    event_name: str = "FILTER_DOCTOR_REVIEWS"
    doctor_name: str | None = None
    filter_rating: int | None = None
    speciality: str | None = None
    sort_order: str | None = None  # newest, oldest, highest, lowest

    class ValidationCriteria(BaseModel):
        doctor_name: str | CriterionValue | None = None
        filter_rating: int | CriterionValue | None = None
        speciality: str | CriterionValue | None = None
        sort_order: str | CriterionValue | None = None

    def _validate_criteria(self, criteria: ValidationCriteria | None = None) -> bool:
        if not criteria:
            return True
        return all(
            [
                self._validate_field(self.doctor_name, criteria.doctor_name),
                self._validate_field(self.filter_rating, criteria.filter_rating),
                self._validate_field(self.speciality, criteria.speciality),
                self._validate_field(self.sort_order, criteria.sort_order),
            ]
        )

    @classmethod
    def parse(cls, backend_event: "BackendEvent") -> "FilterDoctorReviewsEvent":
        base_event = Event.parse(backend_event)
        data = backend_event.data
        data = data.get("data") or {}
        doctor = data.get("doctor") if isinstance(data.get("doctor"), dict) else {}
        return cls(
            event_name=base_event.event_name,
            timestamp=base_event.timestamp,
            web_agent_id=base_event.web_agent_id,
            user_id=base_event.user_id,
            doctor_name=data.get("doctorName") or doctor.get("name"),
            speciality=data.get("specialty") or doctor.get("specialty"),
            filter_rating=data.get("filterRating"),
            sort_order=data.get("sortOrder"),
        )


EVENTS = [
    BookAppointmentEvent,
    AppointmentBookedSuccessfullyEvent,
    RequestAppointmentEvent,
    RequestQuickAppointmentEvent,
    SearchAppointmentEvent,
    SearchDoctorsEvent,
    SearchPrescriptionEvent,
    ViewPrescriptionEvent,
    RefillRequestEvent,
    SearchMedicalAnalysisEvent,
    ViewMedicalAnalysisEvent,
    ViewDoctorProfileEvent,
    ViewDoctorEducationEvent,
    OpenAppointmentFormEvent,
    OpenContactDoctorFormEvent,
    ContactDoctorEvent,
    DoctorContactedSuccessfullyEvent,
    ViewReviewClickedEvent,
    FilterDoctorReviewsEvent,
]

BACKEND_EVENT_TYPES = {
    "BOOK_APPOINTMENT": BookAppointmentEvent,
    "APPOINTMENT_BOOKED_SUCCESSFULLY": AppointmentBookedSuccessfullyEvent,
    "REQUEST_APPOINTMENT": RequestAppointmentEvent,
    "REQUEST_QUICK_APPOINTMENT": RequestQuickAppointmentEvent,
    "SEARCH_APPOINTMENT": SearchAppointmentEvent,
    "SEARCH_DOCTORS": SearchDoctorsEvent,
    "SEARCH_PRESCRIPTION": SearchPrescriptionEvent,
    "VIEW_PRESCRIPTION": ViewPrescriptionEvent,
    "REFILL_PRESCRIPTION": RefillRequestEvent,
    "SEARCH_MEDICAL_ANALYSIS": SearchMedicalAnalysisEvent,
    "VIEW_MEDICAL_ANALYSIS": ViewMedicalAnalysisEvent,
    "VIEW_DOCTOR_PROFILE": ViewDoctorProfileEvent,
    "VIEW_DOCTOR_EDUCATION": ViewDoctorEducationEvent,
    "OPEN_APPOINTMENT_FORM": OpenAppointmentFormEvent,
    "OPEN_CONTACT_DOCTOR_FORM": OpenContactDoctorFormEvent,
    "CONTACT_DOCTOR": ContactDoctorEvent,
    "DOCTOR_CONTACTED_SUCCESSFULLY": DoctorContactedSuccessfullyEvent,
    "VIEW_REVIEWS_CLICKED": ViewReviewClickedEvent,
    "FILTER_DOCTOR_REVIEWS": FilterDoctorReviewsEvent,
}
