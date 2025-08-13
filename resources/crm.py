"""
CRM resources for MCP-Odoo

This module provides MCP tools and resources for comprehensive CRM management,
including leads, opportunities, partners, teams, and University ISEP specific fields.
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel
from datetime import datetime, date

from mcp.server.fastmcp import Context
from mcp_instance import mcp
from context_handler import get_odoo_client_from_context

# Models for request/response types
class LeadFilter(BaseModel):
    """Filter parameters for lead/opportunity listing"""
    partner_id: Optional[int] = None
    team_id: Optional[int] = None
    user_id: Optional[int] = None
    stage_id: Optional[int] = None
    type: Optional[str] = None  # 'lead' or 'opportunity'
    priority: Optional[str] = None
    state: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    program_id: Optional[int] = None  # x_studio_programa_academico
    canal_contacto: Optional[str] = None  # x_studio_canal_de_contacto
    limit: Optional[int] = 100

class LeadCreate(BaseModel):
    """Model for creating new leads"""
    name: str
    contact_name: Optional[str] = None
    email_from: Optional[str] = None
    phone: Optional[str] = None
    partner_name: Optional[str] = None
    description: Optional[str] = None
    team_id: Optional[int] = None
    user_id: Optional[int] = None
    stage_id: Optional[int] = None
    expected_revenue: Optional[float] = None
    probability: Optional[float] = None
    program_id: Optional[int] = None
    canal_contacto: Optional[str] = None
    programa_interes: Optional[str] = None

class PartnerFilter(BaseModel):
    """Filter parameters for partner listing"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_company: Optional[bool] = None
    customer_rank: Optional[int] = None
    supplier_rank: Optional[int] = None
    category_id: Optional[int] = None
    country_id: Optional[int] = None
    limit: Optional[int] = 100

# Helper formatting functions
def format_lead(lead: Dict[str, Any]) -> Dict[str, Any]:
    """Format lead data for better presentation"""
    result = {
        "id": lead["id"],
        "name": lead["name"],
        "type": lead.get("type", "lead"),
        "contact_name": lead.get("contact_name", ""),
        "partner_name": lead.get("partner_name", ""),
        "email_from": lead.get("email_from", ""),
        "phone": lead.get("phone", ""),
        "mobile": lead.get("mobile", ""),
        "expected_revenue": lead.get("expected_revenue", 0.0),
        "probability": lead.get("probability", 0.0),
        "priority": lead.get("priority", "0"),
        "create_date": lead.get("create_date", ""),
        "write_date": lead.get("write_date", ""),
        "date_deadline": lead.get("date_deadline", ""),
        "stage": {
            "id": lead["stage_id"][0] if lead.get("stage_id") else None,
            "name": lead["stage_id"][1] if lead.get("stage_id") else None
        } if lead.get("stage_id") else None,
        "team": {
            "id": lead["team_id"][0] if lead.get("team_id") else None,
            "name": lead["team_id"][1] if lead.get("team_id") else None
        } if lead.get("team_id") else None,
        "user": {
            "id": lead["user_id"][0] if lead.get("user_id") else None,
            "name": lead["user_id"][1] if lead.get("user_id") else None
        } if lead.get("user_id") else None,
        "partner": {
            "id": lead["partner_id"][0] if lead.get("partner_id") else None,
            "name": lead["partner_id"][1] if lead.get("partner_id") else None
        } if lead.get("partner_id") else None,
        # University ISEP specific fields
        "programa_academico": {
            "id": lead["x_studio_programa_academico"][0] if lead.get("x_studio_programa_academico") else None,
            "name": lead["x_studio_programa_academico"][1] if lead.get("x_studio_programa_academico") else None
        } if lead.get("x_studio_programa_academico") else None,
        "canal_contacto": lead.get("x_studio_canal_de_contacto", ""),
        "programa_interes": lead.get("x_studio_programa_de_inters", ""),
        "fecha_firma": lead.get("x_studio_fecha_de_firma", ""),
        "progress": lead.get("progress", 0.0),
        "mautic_export": lead.get("mautic_export", False),
        "mautic_id": lead.get("x_studio_id_mautic", ""),
        # Google Analytics fields
        "gr_source": lead.get("gr_source", ""),
        "gr_campaign": lead.get("gr_campaingn", ""),
        "gr_term": lead.get("gr_term", ""),
        "description": lead.get("description", ""),
    }
    
    return result

def format_partner(partner: Dict[str, Any]) -> Dict[str, Any]:
    """Format partner data for better presentation"""
    return {
        "id": partner["id"],
        "name": partner["name"],
        "display_name": partner.get("display_name", ""),
        "email": partner.get("email", ""),
        "phone": partner.get("phone", ""),
        "mobile": partner.get("mobile", ""),
        "website": partner.get("website", ""),
        "is_company": partner.get("is_company", False),
        "customer_rank": partner.get("customer_rank", 0),
        "supplier_rank": partner.get("supplier_rank", 0),
        "vat": partner.get("vat", ""),
        "street": partner.get("street", ""),
        "street2": partner.get("street2", ""),
        "city": partner.get("city", ""),
        "zip": partner.get("zip", ""),
        "country": {
            "id": partner["country_id"][0] if partner.get("country_id") else None,
            "name": partner["country_id"][1] if partner.get("country_id") else None
        } if partner.get("country_id") else None,
        "state": {
            "id": partner["state_id"][0] if partner.get("state_id") else None,
            "name": partner["state_id"][1] if partner.get("state_id") else None
        } if partner.get("state_id") else None,
        "parent": {
            "id": partner["parent_id"][0] if partner.get("parent_id") else None,
            "name": partner["parent_id"][1] if partner.get("parent_id") else None
        } if partner.get("parent_id") else None,
        "categories": [
            {"id": cat[0], "name": cat[1]} for cat in partner.get("category_id", [])
        ] if isinstance(partner.get("category_id"), list) else [],
        "create_date": partner.get("create_date", ""),
        "write_date": partner.get("write_date", ""),
        "active": partner.get("active", True),
    }

# ============================================================================
# LEAD/OPPORTUNITY MANAGEMENT TOOLS
# ============================================================================

@mcp.tool()
async def list_leads(ctx: Context, 
                    partner_id: Optional[int] = None,
                    team_id: Optional[int] = None,
                    user_id: Optional[int] = None,
                    stage_id: Optional[int] = None,
                    type: Optional[str] = None,
                    priority: Optional[str] = None,
                    date_from: Optional[str] = None,
                    date_to: Optional[str] = None,
                    program_id: Optional[int] = None,
                    canal_contacto: Optional[str] = None,
                    limit: Optional[int] = 100) -> List[Dict[str, Any]]:
    """
    List leads/opportunities with comprehensive filtering options.
    
    Args:
        partner_id: Filter by partner/customer ID
        team_id: Filter by sales team ID
        user_id: Filter by salesperson ID
        stage_id: Filter by stage ID
        type: Filter by type ('lead' or 'opportunity')
        priority: Filter by priority ('0', '1', '2', '3')
        date_from: Filter from this date (YYYY-MM-DD)
        date_to: Filter until this date (YYYY-MM-DD)
        program_id: Filter by academic program ID (ISEP specific)
        canal_contacto: Filter by contact channel (ISEP specific)
        limit: Maximum number of records to return
        
    Returns:
        List of leads with detailed information including ISEP custom fields
    """
    try:
        # Get Odoo client
        odoo_client = await get_odoo_client_from_context(ctx)
        
        # Build domain filter
        domain = []
        
        if partner_id:
            domain.append(("partner_id", "=", partner_id))
        if team_id:
            domain.append(("team_id", "=", team_id))
        if user_id:
            domain.append(("user_id", "=", user_id))
        if stage_id:
            domain.append(("stage_id", "=", stage_id))
        if type:
            domain.append(("type", "=", type))
        if priority:
            domain.append(("priority", "=", priority))
        if date_from:
            domain.append(("create_date", ">=", date_from))
        if date_to:
            domain.append(("create_date", "<=", date_to))
        if program_id:
            domain.append(("x_studio_programa_academico", "=", program_id))
        if canal_contacto:
            domain.append(("x_studio_canal_de_contacto", "ilike", canal_contacto))
        
        await ctx.info(f"Fetching leads with domain: {domain}")
        
        # Fields to retrieve
        fields = [
            "id", "name", "type", "contact_name", "partner_name", "email_from",
            "phone", "mobile", "expected_revenue", "probability", "priority",
            "create_date", "write_date", "date_deadline", "stage_id", "team_id",
            "user_id", "partner_id", "description",
            # ISEP specific fields
            "x_studio_programa_academico", "x_studio_canal_de_contacto",
            "x_studio_programa_de_inters", "x_studio_fecha_de_firma",
            "progress", "mautic_export", "x_studio_id_mautic",
            # Google Analytics fields
            "gr_source", "gr_campaingn", "gr_term"
        ]
        
        # Query Odoo
        leads = await odoo_client.search_read(
            "crm.lead", domain, fields, limit=limit, order="create_date desc"
        )
        
        # Format response
        return [format_lead(lead) for lead in leads]
        
    except Exception as e:
        await ctx.error(f"Error fetching leads: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def get_lead_details(ctx: Context, lead_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific lead/opportunity.
    
    Args:
        lead_id: ID of the lead to retrieve
        
    Returns:
        Detailed lead information including all custom fields
    """
    try:
        odoo_client = await get_odoo_client_from_context(ctx)
        
        # Get all available fields for the lead
        lead_data = await odoo_client.execute_kw(
            "crm.lead", "read", [lead_id], {}
        )
        
        if not lead_data:
            return {"error": f"Lead with ID {lead_id} not found"}
        
        lead = lead_data[0]
        result = format_lead(lead)
        
        # Add additional detailed fields
        result.update({
            "website": lead.get("website", ""),
            "function": lead.get("function", ""),
            "street": lead.get("street", ""),
            "street2": lead.get("street2", ""),
            "city": lead.get("city", ""),
            "zip": lead.get("zip", ""),
            "date_open": lead.get("date_open", ""),
            "date_closed": lead.get("date_closed", ""),
            "date_last_stage_update": lead.get("date_last_stage_update", ""),
            "won_status": lead.get("won_status", ""),
            "active": lead.get("active", True),
            "color": lead.get("color", 0),
            # Additional ISEP fields
            "duracion_convenio": lead.get("x_studio_duracin_de_convenio", ""),
            "correo_existe": lead.get("x_studio_correo_existe", False),
            "correo_revisado": lead.get("x_studio_correo_revisado", False),
            "bool_interes": lead.get("x_studio_bool_interes", False),
        })
        
        return result
        
    except Exception as e:
        await ctx.error(f"Error fetching lead details: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def create_lead(ctx: Context, 
                     name: str,
                     contact_name: Optional[str] = None,
                     email_from: Optional[str] = None,
                     phone: Optional[str] = None,
                     partner_name: Optional[str] = None,
                     description: Optional[str] = None,
                     team_id: Optional[int] = None,
                     user_id: Optional[int] = None,
                     stage_id: Optional[int] = None,
                     expected_revenue: Optional[float] = None,
                     probability: Optional[float] = None,
                     program_id: Optional[int] = None,
                     canal_contacto: Optional[str] = None,
                     programa_interes: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new lead/opportunity in the CRM.
    
    Args:
        name: Lead/Opportunity name (required)
        contact_name: Contact person name
        email_from: Email address
        phone: Phone number
        partner_name: Company name
        description: Description/notes
        team_id: Sales team ID
        user_id: Salesperson ID
        stage_id: Stage ID
        expected_revenue: Expected revenue
        probability: Probability (0-100)
        program_id: Academic program ID (ISEP specific)
        canal_contacto: Contact channel (ISEP specific)
        programa_interes: Program of interest (ISEP specific)
        
    Returns:
        Created lead information
    """
    try:
        odoo_client = await get_odoo_client_from_context(ctx)
        
        # Prepare lead data
        lead_data = {
            "name": name,
            "type": "lead"  # Default to lead, can be converted later
        }
        
        # Add optional fields
        if contact_name:
            lead_data["contact_name"] = contact_name
        if email_from:
            lead_data["email_from"] = email_from
        if phone:
            lead_data["phone"] = phone
        if partner_name:
            lead_data["partner_name"] = partner_name
        if description:
            lead_data["description"] = description
        if team_id:
            lead_data["team_id"] = team_id
        if user_id:
            lead_data["user_id"] = user_id
        if stage_id:
            lead_data["stage_id"] = stage_id
        if expected_revenue:
            lead_data["expected_revenue"] = expected_revenue
        if probability:
            lead_data["probability"] = probability
        
        # ISEP specific fields
        if program_id:
            lead_data["x_studio_programa_academico"] = program_id
        if canal_contacto:
            lead_data["x_studio_canal_de_contacto"] = canal_contacto
        if programa_interes:
            lead_data["x_studio_programa_de_inters"] = programa_interes
        
        await ctx.info(f"Creating lead with data: {lead_data}")
        
        # Create the lead
        lead_id = await odoo_client.execute_kw(
            "crm.lead", "create", [lead_data]
        )
        
        # Get the created lead details
        created_lead = await get_lead_details(ctx, lead_id)
        
        await ctx.info(f"Successfully created lead with ID: {lead_id}")
        return created_lead
        
    except Exception as e:
        await ctx.error(f"Error creating lead: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def update_lead(ctx: Context, 
                     lead_id: int,
                     name: Optional[str] = None,
                     contact_name: Optional[str] = None,
                     email_from: Optional[str] = None,
                     phone: Optional[str] = None,
                     description: Optional[str] = None,
                     stage_id: Optional[int] = None,
                     user_id: Optional[int] = None,
                     team_id: Optional[int] = None,
                     expected_revenue: Optional[float] = None,
                     probability: Optional[float] = None,
                     priority: Optional[str] = None,
                     program_id: Optional[int] = None,
                     canal_contacto: Optional[str] = None,
                     programa_interes: Optional[str] = None,
                     progress: Optional[float] = None) -> Dict[str, Any]:
    """
    Update an existing lead/opportunity.
    
    Args:
        lead_id: ID of the lead to update (required)
        name: Lead/Opportunity name
        contact_name: Contact person name
        email_from: Email address
        phone: Phone number
        description: Description/notes
        stage_id: Stage ID
        user_id: Salesperson ID
        team_id: Sales team ID
        expected_revenue: Expected revenue
        probability: Probability (0-100)
        priority: Priority ('0', '1', '2', '3')
        program_id: Academic program ID (ISEP specific)
        canal_contacto: Contact channel (ISEP specific)
        programa_interes: Program of interest (ISEP specific)
        progress: Progress percentage (ISEP specific)
        
    Returns:
        Updated lead information
    """
    try:
        odoo_client = await get_odoo_client_from_context(ctx)
        
        # Prepare update data
        update_data = {}
        
        # Add fields to update if provided
        if name is not None:
            update_data["name"] = name
        if contact_name is not None:
            update_data["contact_name"] = contact_name
        if email_from is not None:
            update_data["email_from"] = email_from
        if phone is not None:
            update_data["phone"] = phone
        if description is not None:
            update_data["description"] = description
        if stage_id is not None:
            update_data["stage_id"] = stage_id
        if user_id is not None:
            update_data["user_id"] = user_id
        if team_id is not None:
            update_data["team_id"] = team_id
        if expected_revenue is not None:
            update_data["expected_revenue"] = expected_revenue
        if probability is not None:
            update_data["probability"] = probability
        if priority is not None:
            update_data["priority"] = priority
        
        # ISEP specific fields
        if program_id is not None:
            update_data["x_studio_programa_academico"] = program_id
        if canal_contacto is not None:
            update_data["x_studio_canal_de_contacto"] = canal_contacto
        if programa_interes is not None:
            update_data["x_studio_programa_de_inters"] = programa_interes
        if progress is not None:
            update_data["progress"] = progress
        
        if not update_data:
            return {"error": "No fields provided for update"}
        
        await ctx.info(f"Updating lead {lead_id} with data: {update_data}")
        
        # Update the lead
        await odoo_client.execute_kw(
            "crm.lead", "write", [[lead_id], update_data]
        )
        
        # Get updated lead details
        updated_lead = await get_lead_details(ctx, lead_id)
        
        await ctx.info(f"Successfully updated lead {lead_id}")
        return updated_lead
        
    except Exception as e:
        await ctx.error(f"Error updating lead: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def convert_lead_to_opportunity(ctx: Context, 
                                    lead_id: int,
                                    partner_id: Optional[int] = None,
                                    user_id: Optional[int] = None,
                                    team_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Convert a lead to opportunity.
    
    Args:
        lead_id: ID of the lead to convert
        partner_id: Partner ID to associate with opportunity
        user_id: Salesperson ID to assign
        team_id: Sales team ID to assign
        
    Returns:
        Updated opportunity information
    """
    try:
        odoo_client = await get_odoo_client_from_context(ctx)
        
        # Update lead to opportunity type
        update_data = {"type": "opportunity"}
        
        if partner_id:
            update_data["partner_id"] = partner_id
        if user_id:
            update_data["user_id"] = user_id
        if team_id:
            update_data["team_id"] = team_id
        
        await ctx.info(f"Converting lead {lead_id} to opportunity")
        
        await odoo_client.execute_kw(
            "crm.lead", "write", [[lead_id], update_data]
        )
        
        # Get updated opportunity details
        opportunity = await get_lead_details(ctx, lead_id)
        
        await ctx.info(f"Successfully converted lead {lead_id} to opportunity")
        return opportunity
        
    except Exception as e:
        await ctx.error(f"Error converting lead to opportunity: {str(e)}")
        return {"error": str(e)}

# ============================================================================
# PARTNER MANAGEMENT TOOLS
# ============================================================================

@mcp.tool()
async def list_partners(ctx: Context,
                       name: Optional[str] = None,
                       email: Optional[str] = None,
                       phone: Optional[str] = None,
                       is_company: Optional[bool] = None,
                       customer_rank: Optional[int] = None,
                       supplier_rank: Optional[int] = None,
                       category_id: Optional[int] = None,
                       country_id: Optional[int] = None,
                       limit: Optional[int] = 100) -> List[Dict[str, Any]]:
    """
    List partners/contacts with filtering options.
    
    Args:
        name: Filter by name (partial match)
        email: Filter by email (partial match)
        phone: Filter by phone (partial match)
        is_company: Filter companies (True) or individuals (False)
        customer_rank: Filter by customer rank (> 0 for customers)
        supplier_rank: Filter by supplier rank (> 0 for suppliers)
        category_id: Filter by category ID
        country_id: Filter by country ID
        limit: Maximum number of records to return
        
    Returns:
        List of partners with detailed information
    """
    try:
        odoo_client = await get_odoo_client_from_context(ctx)
        
        # Build domain filter
        domain = []
        
        if name:
            domain.append(("name", "ilike", name))
        if email:
            domain.append(("email", "ilike", email))
        if phone:
            domain.append(("phone", "ilike", phone))
        if is_company is not None:
            domain.append(("is_company", "=", is_company))
        if customer_rank is not None:
            domain.append(("customer_rank", ">=", customer_rank))
        if supplier_rank is not None:
            domain.append(("supplier_rank", ">=", supplier_rank))
        if category_id:
            domain.append(("category_id", "in", [category_id]))
        if country_id:
            domain.append(("country_id", "=", country_id))
        
        await ctx.info(f"Fetching partners with domain: {domain}")
        
        # Fields to retrieve
        fields = [
            "id", "name", "display_name", "email", "phone", "mobile", "website",
            "is_company", "customer_rank", "supplier_rank", "vat", "street",
            "street2", "city", "zip", "country_id", "state_id", "parent_id",
            "category_id", "create_date", "write_date", "active"
        ]
        
        # Query Odoo
        partners = await odoo_client.search_read(
            "res.partner", domain, fields, limit=limit, order="name asc"
        )
        
        # Format response
        return [format_partner(partner) for partner in partners]
        
    except Exception as e:
        await ctx.error(f"Error fetching partners: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def get_partner_details(ctx: Context, partner_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific partner.
    
    Args:
        partner_id: ID of the partner to retrieve
        
    Returns:
        Detailed partner information
    """
    try:
        odoo_client = await get_odoo_client_from_context(ctx)
        
        partner_data = await odoo_client.execute_kw(
            "res.partner", "read", [partner_id], {}
        )
        
        if not partner_data:
            return {"error": f"Partner with ID {partner_id} not found"}
        
        partner = partner_data[0]
        result = format_partner(partner)
        
        # Add additional detailed fields
        result.update({
            "function": partner.get("function", ""),
            "title": {
                "id": partner["title"][0] if partner.get("title") else None,
                "name": partner["title"][1] if partner.get("title") else None
            } if partner.get("title") else None,
            "lang": partner.get("lang", ""),
            "tz": partner.get("tz", ""),
            "comment": partner.get("comment", ""),
            "ref": partner.get("ref", ""),
            "industry": {
                "id": partner["industry_id"][0] if partner.get("industry_id") else None,
                "name": partner["industry_id"][1] if partner.get("industry_id") else None
            } if partner.get("industry_id") else None,
            "company": {
                "id": partner["company_id"][0] if partner.get("company_id") else None,
                "name": partner["company_id"][1] if partner.get("company_id") else None
            } if partner.get("company_id") else None,
        })
        
        return result
        
    except Exception as e:
        await ctx.error(f"Error fetching partner details: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def create_partner(ctx: Context,
                        name: str,
                        email: Optional[str] = None,
                        phone: Optional[str] = None,
                        mobile: Optional[str] = None,
                        is_company: Optional[bool] = False,
                        website: Optional[str] = None,
                        vat: Optional[str] = None,
                        street: Optional[str] = None,
                        street2: Optional[str] = None,
                        city: Optional[str] = None,
                        zip: Optional[str] = None,
                        country_id: Optional[int] = None,
                        state_id: Optional[int] = None,
                        parent_id: Optional[int] = None,
                        customer_rank: Optional[int] = 0,
                        supplier_rank: Optional[int] = 0,
                        category_ids: Optional[List[int]] = None) -> Dict[str, Any]:
    """
    Create a new partner/contact.
    
    Args:
        name: Partner name (required)
        email: Email address
        phone: Phone number
        mobile: Mobile number
        is_company: True for companies, False for individuals
        website: Website URL
        vat: VAT/Tax ID
        street: Street address
        street2: Street address line 2
        city: City
        zip: ZIP/Postal code
        country_id: Country ID
        state_id: State ID
        parent_id: Parent company ID
        customer_rank: Customer rank (0=not customer, 1+=customer)
        supplier_rank: Supplier rank (0=not supplier, 1+=supplier)
        category_ids: List of category IDs
        
    Returns:
        Created partner information
    """
    try:
        odoo_client = await get_odoo_client_from_context(ctx)
        
        # Prepare partner data
        partner_data = {
            "name": name,
            "is_company": is_company or False
        }
        
        # Add optional fields
        if email:
            partner_data["email"] = email
        if phone:
            partner_data["phone"] = phone
        if mobile:
            partner_data["mobile"] = mobile
        if website:
            partner_data["website"] = website
        if vat:
            partner_data["vat"] = vat
        if street:
            partner_data["street"] = street
        if street2:
            partner_data["street2"] = street2
        if city:
            partner_data["city"] = city
        if zip:
            partner_data["zip"] = zip
        if country_id:
            partner_data["country_id"] = country_id
        if state_id:
            partner_data["state_id"] = state_id
        if parent_id:
            partner_data["parent_id"] = parent_id
        if customer_rank is not None:
            partner_data["customer_rank"] = customer_rank
        if supplier_rank is not None:
            partner_data["supplier_rank"] = supplier_rank
        if category_ids:
            partner_data["category_id"] = [(6, 0, category_ids)]
        
        await ctx.info(f"Creating partner with data: {partner_data}")
        
        # Create the partner
        partner_id = await odoo_client.execute_kw(
            "res.partner", "create", [partner_data]
        )
        
        # Get the created partner details
        created_partner = await get_partner_details(ctx, partner_id)
        
        await ctx.info(f"Successfully created partner with ID: {partner_id}")
        return created_partner
        
    except Exception as e:
        await ctx.error(f"Error creating partner: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def update_partner(ctx: Context,
                        partner_id: int,
                        name: Optional[str] = None,
                        email: Optional[str] = None,
                        phone: Optional[str] = None,
                        mobile: Optional[str] = None,
                        website: Optional[str] = None,
                        vat: Optional[str] = None,
                        street: Optional[str] = None,
                        street2: Optional[str] = None,
                        city: Optional[str] = None,
                        zip: Optional[str] = None,
                        country_id: Optional[int] = None,
                        state_id: Optional[int] = None,
                        customer_rank: Optional[int] = None,
                        supplier_rank: Optional[int] = None,
                        active: Optional[bool] = None) -> Dict[str, Any]:
    """
    Update an existing partner/contact.
    
    Args:
        partner_id: ID of the partner to update (required)
        name: Partner name
        email: Email address
        phone: Phone number
        mobile: Mobile number
        website: Website URL
        vat: VAT/Tax ID
        street: Street address
        street2: Street address line 2
        city: City
        zip: ZIP/Postal code
        country_id: Country ID
        state_id: State ID
        customer_rank: Customer rank
        supplier_rank: Supplier rank
        active: Active status
        
    Returns:
        Updated partner information
    """
    try:
        odoo_client = await get_odoo_client_from_context(ctx)
        
        # Prepare update data
        update_data = {}
        
        # Add fields to update if provided
        if name is not None:
            update_data["name"] = name
        if email is not None:
            update_data["email"] = email
        if phone is not None:
            update_data["phone"] = phone
        if mobile is not None:
            update_data["mobile"] = mobile
        if website is not None:
            update_data["website"] = website
        if vat is not None:
            update_data["vat"] = vat
        if street is not None:
            update_data["street"] = street
        if street2 is not None:
            update_data["street2"] = street2
        if city is not None:
            update_data["city"] = city
        if zip is not None:
            update_data["zip"] = zip
        if country_id is not None:
            update_data["country_id"] = country_id
        if state_id is not None:
            update_data["state_id"] = state_id
        if customer_rank is not None:
            update_data["customer_rank"] = customer_rank
        if supplier_rank is not None:
            update_data["supplier_rank"] = supplier_rank
        if active is not None:
            update_data["active"] = active
        
        if not update_data:
            return {"error": "No fields provided for update"}
        
        await ctx.info(f"Updating partner {partner_id} with data: {update_data}")
        
        # Update the partner
        await odoo_client.execute_kw(
            "res.partner", "write", [[partner_id], update_data]
        )
        
        # Get updated partner details
        updated_partner = await get_partner_details(ctx, partner_id)
        
        await ctx.info(f"Successfully updated partner {partner_id}")
        return updated_partner
        
    except Exception as e:
        await ctx.error(f"Error updating partner: {str(e)}")
        return {"error": str(e)}

# ============================================================================
# CRM AUXILIARY TOOLS
# ============================================================================

@mcp.tool()
async def list_crm_stages(ctx: Context, team_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    List CRM stages for leads/opportunities.
    
    Args:
        team_id: Filter stages by team ID
        
    Returns:
        List of CRM stages
    """
    try:
        odoo_client = await get_odoo_client_from_context(ctx)
        
        domain = []
        if team_id:
            domain.append(("team_id", "=", team_id))
        
        stages = await odoo_client.search_read(
            "crm.stage", domain,
            ["id", "name", "sequence", "fold", "team_id", "probability"],
            order="sequence asc"
        )
        
        return [{
            "id": stage["id"],
            "name": stage["name"],
            "sequence": stage.get("sequence", 0),
            "fold": stage.get("fold", False),
            "probability": stage.get("probability", 0.0),
            "team": {
                "id": stage["team_id"][0] if stage.get("team_id") else None,
                "name": stage["team_id"][1] if stage.get("team_id") else None
            } if stage.get("team_id") else None
        } for stage in stages]
        
    except Exception as e:
        await ctx.error(f"Error fetching CRM stages: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def list_crm_teams(ctx: Context) -> List[Dict[str, Any]]:
    """
    List CRM sales teams.
    
    Returns:
        List of CRM teams
    """
    try:
        odoo_client = await get_odoo_client_from_context(ctx)
        
        teams = await odoo_client.search_read(
            "crm.team", [],
            ["id", "name", "user_id", "member_ids", "active"],
            order="name asc"
        )
        
        return [{
            "id": team["id"],
            "name": team["name"],
            "active": team.get("active", True),
            "leader": {
                "id": team["user_id"][0] if team.get("user_id") else None,
                "name": team["user_id"][1] if team.get("user_id") else None
            } if team.get("user_id") else None,
            "member_count": len(team.get("member_ids", []))
        } for team in teams]
        
    except Exception as e:
        await ctx.error(f"Error fetching CRM teams: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def get_lead_activities(ctx: Context, lead_id: int) -> List[Dict[str, Any]]:
    """
    Get activities related to a lead/opportunity.
    
    Args:
        lead_id: Lead/Opportunity ID
        
    Returns:
        List of activities for the lead
    """
    try:
        odoo_client = await get_odoo_client_from_context(ctx)
        
        activities = await odoo_client.search_read(
            "mail.activity", 
            [("res_model", "=", "crm.lead"), ("res_id", "=", lead_id)],
            ["id", "activity_type_id", "summary", "date_deadline", 
             "user_id", "state", "create_date"],
            order="date_deadline desc"
        )
        
        return [{
            "id": activity["id"],
            "type": {
                "id": activity["activity_type_id"][0] if activity.get("activity_type_id") else None,
                "name": activity["activity_type_id"][1] if activity.get("activity_type_id") else None
            } if activity.get("activity_type_id") else None,
            "summary": activity.get("summary", ""),
            "date_deadline": activity.get("date_deadline", ""),
            "state": activity.get("state", ""),
            "user": {
                "id": activity["user_id"][0] if activity.get("user_id") else None,
                "name": activity["user_id"][1] if activity.get("user_id") else None
            } if activity.get("user_id") else None,
            "create_date": activity.get("create_date", "")
        } for activity in activities]
        
    except Exception as e:
        await ctx.error(f"Error fetching lead activities: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def get_academic_programs(ctx: Context, active_only: bool = True) -> List[Dict[str, Any]]:
    """
    Get academic programs available in the system (ISEP specific).
    
    Args:
        active_only: Return only active programs
        
    Returns:
        List of academic programs
    """
    try:
        odoo_client = await get_odoo_client_from_context(ctx)
        
        domain = []
        if active_only:
            domain.append(("active", "=", True))
        
        # Academic programs are stored as products in Odoo
        programs = await odoo_client.search_read(
            "product.template", domain,
            ["id", "name", "active", "list_price", "categ_id"],
            order="name asc"
        )
        
        return [{
            "id": program["id"],
            "name": program["name"],
            "active": program.get("active", True),
            "price": program.get("list_price", 0.0),
            "category": {
                "id": program["categ_id"][0] if program.get("categ_id") else None,
                "name": program["categ_id"][1] if program.get("categ_id") else None
            } if program.get("categ_id") else None
        } for program in programs]
        
    except Exception as e:
        await ctx.error(f"Error fetching academic programs: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
async def get_crm_dashboard_stats(ctx: Context, 
                                 team_id: Optional[int] = None,
                                 user_id: Optional[int] = None,
                                 date_from: Optional[str] = None,
                                 date_to: Optional[str] = None) -> Dict[str, Any]:
    """
    Get CRM dashboard statistics.
    
    Args:
        team_id: Filter by team ID
        user_id: Filter by user ID
        date_from: Start date for statistics
        date_to: End date for statistics
        
    Returns:
        CRM dashboard statistics
    """
    try:
        odoo_client = await get_odoo_client_from_context(ctx)
        
        # Build base domain
        domain = []
        if team_id:
            domain.append(("team_id", "=", team_id))
        if user_id:
            domain.append(("user_id", "=", user_id))
        if date_from:
            domain.append(("create_date", ">=", date_from))
        if date_to:
            domain.append(("create_date", "<=", date_to))
        
        # Get leads count
        leads_domain = domain + [("type", "=", "lead")]
        leads_count = await odoo_client.execute_kw(
            "crm.lead", "search_count", [leads_domain]
        )
        
        # Get opportunities count
        opps_domain = domain + [("type", "=", "opportunity")]
        opportunities_count = await odoo_client.execute_kw(
            "crm.lead", "search_count", [opps_domain]
        )
        
        # Get won opportunities
        won_domain = domain + [("type", "=", "opportunity"), ("probability", "=", 100)]
        won_count = await odoo_client.execute_kw(
            "crm.lead", "search_count", [won_domain]
        )
        
        # Get lost opportunities  
        lost_domain = domain + [("type", "=", "opportunity"), ("probability", "=", 0), ("active", "=", False)]
        lost_count = await odoo_client.execute_kw(
            "crm.lead", "search_count", [lost_domain]
        )
        
        # Get revenue data
        revenue_opps = await odoo_client.search_read(
            "crm.lead", 
            domain + [("type", "=", "opportunity"), ("expected_revenue", ">", 0)],
            ["expected_revenue", "probability"]
        )
        
        total_expected = sum(opp.get("expected_revenue", 0) for opp in revenue_opps)
        weighted_revenue = sum(
            opp.get("expected_revenue", 0) * (opp.get("probability", 0) / 100)
            for opp in revenue_opps
        )
        
        return {
            "leads_count": leads_count,
            "opportunities_count": opportunities_count,
            "won_count": won_count,
            "lost_count": lost_count,
            "win_rate": round((won_count / max(opportunities_count, 1)) * 100, 2),
            "total_expected_revenue": round(total_expected, 2),
            "weighted_revenue": round(weighted_revenue, 2),
            "active_pipeline": opportunities_count - won_count - lost_count
        }
        
    except Exception as e:
        await ctx.error(f"Error getting CRM dashboard stats: {str(e)}")
        return {"error": str(e)}
