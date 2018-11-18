# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
{
    "name": "Hospital Management",
    "version": "1.0",
    "summary": "Hospital Management",
    "category": "Industries",
    "description": """
BrowseInfo developed a new odoo/OpenERP module apps.
This module is used to manage Hospital Mangement.
    Also use for manage the healthcare management, Clinic management, Medical Management.Doctor's Clinic. Clinic software, oehealth.

""",
    "depends": ["base", "sale", "stock", "account", "salon_management", "web_notify", "base_ext", "document", "mrp"],
    "data": [
        "wizard/unlock_client.xml",
        "wizard/map_quotation.xml",
        "wizard/admission_reactivate.xml",
        "wizard/create_appointment.xml",

        "views/patient_extra_actions.xml",
        "views/main_menu_file.xml",
        "views/appointments_invoice_wizard.xml",
        "views/appointment_wizard_view.xml",
        "views/lab_req_view.xml",
        "views/medical_family_code_view.xml",
        "views/medical_patients_view.xml",
        "views/seq1_view.xml",
        "views/sequence_view.xml",

        "views/imaging_test_seq_view.xml",
        "security/healthcare_security.xml",
        "security/ir.model.access.csv",
        "views/medical_appointment_sequence.xml",
        "views/medical_patient_seq.xml",
        "views/result_seq.xml",
        "views/medical_health_service_sequence.xml",

        "views/medical_inpatient_evaluation_view.xml",

        "views/lab_configration_menus.xml",
        "views/laboratory_menu_views.xml",
        "views/medical_psc_view.xml",

        "views/lab_test_results.xml",
        "views/medical_rcri_view.xml",
        "views/medical_appointment_view.xml",
        "views/medical_health_centres_bed_view.xml",
        "views/health_center_view.xml",

        "views/medical_patient_disease_view.xml",
        "views/medical_inpatient_registration_view.xml",
        "views/inpatient_administration_sequence.xml",
        "views/prescription_view.xml",

        "views/medical_vaccination_view.xml",
        "views/medical_newborn_view.xml",
        "views/medical_psc_view.xml",
        "views/medical_newborn_view.xml",

        "views/medical_procedure_code_view.xml",
        "views/medical_nursing_procedures_view.xml",
        "views/medical_surgey_view.xml",

        "views/medical_genetic_risk_view.xml",
        "views/medical_speciality_view.xml",
        "views/medical_occupation_view.xml",
        "views/medical_ethnicity_view.xml",
        "views/medical_drugs_recreational_view.xml",
        "views/medical_operational_area_view.xml",
        "views/medical_operational_sector_view.xml",

        "views/insurance_view.xml",

        "views/medical_health_centers_building_view.xml",

        "views/medical_health_centers_units_view.xml",
        "views/medical_health_centers_ward_view.xml",
        "views/disease_category_structure_view.xml",

        "views/disease_view.xml",
        "views/medical_medicament_view.xml",
        "views/inv_menu_view_actions.xml",

        "views/medical_physician_view.xml",
        "views/medical_physician_schedules_available_view.xml",
        "views/medical_medicament_view.xml",

        "views/medical_medicament_dosage_unit_view.xml",

        "views/report_view.xml",
        "views/appointment_recipts_report_template.xml",
        "views/medical_view_report_document_lab.xml",
        "views/medical_view_report_lab_result_demo_report.xml",
        "views/patient_card_report.xml",
        "views/patient_diseases_document_report.xml",

        "views/patient_medications_document_report.xml",
        "views/newborn_card_report.xml",
        "views/patient_vaccinations_document_report.xml",
        "views/prescription_demo_report.xml",

        "views/appointment_evalution_per_doctor_wizard_view.xml",
        "views/appointment_find_doctor_wizard_view.xml",
        "views/appointment_evalution_per_speciality_wizard_view.xml",
        "views/appointment_evalution_per_prescription_wizard_view.xml",
        "views/appointment_evalution_per_medical_health_wizard_view.xml",

        "views/medical_inpatient_medication1_view.xml",

        "views/medical_monitoring_report_view.xml",
        "views/medical_monitoring_types_view.xml",

        "views/medical_inpatient_medication_view.xml",
        "views/pet_type_view.xml",
        "views/owner_view.xml",
        "views/salon_management.xml",
        "views/medical_map_view.xml",
        "views/medical_next_steps_view.xml",
        "views/medical_sequence.xml",
        "views/report_map_surgey.xml",
        "views/report_map_label.xml",
        "views/report_map_monitoring_report.xml",
        "views/product.xml",
        "views/hospital_config.xml",
        "views/ir_cron.xml",
        "views/office_template.xml",
        "views/report_office_template.xml",
        "views/report_template_type_letter.xml",
        "views/report_medical_exam_website.xml",
        "views/res_company_view.xml",
        "views/res_partner_view.xml",
        "views/website_medical_exam.xml",
    ],
    "author": "BrowseInfo",
    "sequence": 150,
    "website": "http://www.browseinfo.in",
    "price": 129,
    "currency": "EUR",
    "installable": True,
    "application": True,
    "images": ["static/description/Banner.png"],

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
