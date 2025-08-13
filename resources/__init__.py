"""
Resources for the MCP-Odoo connector.

All resources should be imported here to ensure they are registered
with the MCP instance.
"""

# Partner resources
from .partners import partners_resource, partner_detail

# Accounting resources
from .accounting import (
    list_vendor_bills, 
    list_customer_invoices,
    list_payments,
    get_invoice_details,
    reconcile_invoices_and_payments,
    list_accounting_entries,
    list_suppliers,
    list_customers
)

# CRM resources
from .crm import (
    list_leads,
    get_lead_details,
    create_lead,
    update_lead,
    convert_lead_to_opportunity,
    list_partners,
    get_partner_details,
    create_partner,
    update_partner,
    list_crm_stages,
    list_crm_teams,
    get_lead_activities,
    get_academic_programs,
    get_crm_dashboard_stats
)

__all__ = [
    # Partners
    "partners_resource", 
    "partner_detail",
    
    # Accounting
    "list_vendor_bills",
    "list_customer_invoices",
    "list_payments",
    "get_invoice_details",
    "reconcile_invoices_and_payments",
    "list_accounting_entries",
    "list_suppliers",
    "list_customers",
    
    # CRM
    "list_leads",
    "get_lead_details",
    "create_lead",
    "update_lead",
    "convert_lead_to_opportunity",
    "list_partners",
    "get_partner_details",
    "create_partner",
    "update_partner",
    "list_crm_stages",
    "list_crm_teams",
    "get_lead_activities",
    "get_academic_programs",
    "get_crm_dashboard_stats"
] 