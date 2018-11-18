# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Medical Website - Patients",
    "summary": "Adds patient listing and editing to website portal.",
    "version": "10.0.1.0.0",
    "category": "Medical",
    "website": "https://laslabs.com",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_portal_medical",
    ],
    "data": [
        "views/website_medical_template.xml",
        "views/patients_template.xml",
        "views/assets.xml",
        "data/ir_model_data.xml",
        "security/ir.model.access.csv",
        "security/ir_sequence_security.xml",
        "security/medical_patient_security.xml",
    ],
    "demo": [
        "demo/medical_patient_demo.xml",
    ],
}
