# CRM Functionality Guide

This guide covers the comprehensive CRM (Customer Relationship Management) functionality available in the MCP-Odoo connector, specifically designed for Universidad ISEP's requirements.

## Overview

The CRM module provides complete management capabilities for:
- **Leads and Opportunities**: Full lifecycle management from initial contact to conversion
- **Partners/Contacts**: Customer and supplier management
- **Academic Programs**: University-specific program management (ISEP)
- **Sales Teams and Stages**: Workflow and team management
- **Dashboard Analytics**: Performance metrics and statistics

## Key Features

### 🎯 Lead/Opportunity Management
- Create, update, and convert leads to opportunities
- Track progress with customizable stages
- Manage academic program associations (ISEP specific)
- Handle contact channels and communication tracking
- Support for Google Analytics integration

### 👥 Partner/Contact Management  
- Comprehensive contact and company management
- Customer and supplier classification
- Address and contact information management
- Category and industry classification

### 📊 University ISEP Specific Features
- Academic program tracking (`x_studio_programa_academico`)
- Contact channel management (`x_studio_canal_de_contacto`)
- Program of interest tracking (`x_studio_programa_de_inters`)
- Progress monitoring with percentage completion
- Mautic CRM integration support
- Contract duration tracking (`x_studio_duracin_de_convenio`)

## Available Tools

### Lead/Opportunity Tools

#### `list_leads`
List and filter leads/opportunities with comprehensive filtering options.

**Parameters:**
- `partner_id`: Filter by customer ID
- `team_id`: Filter by sales team ID
- `user_id`: Filter by salesperson ID
- `stage_id`: Filter by stage ID
- `type`: Filter by type ('lead' or 'opportunity')
- `priority`: Filter by priority ('0'-'3')
- `date_from/date_to`: Date range filtering
- `program_id`: Filter by academic program (ISEP)
- `canal_contacto`: Filter by contact channel (ISEP)
- `limit`: Maximum records to return

**Example usage:**
```json
{
  "tool": "list_leads",
  "parameters": {
    "type": "opportunity",
    "stage_id": 3,
    "program_id": 15,
    "limit": 50
  }
}
```

#### `get_lead_details`
Get comprehensive information about a specific lead/opportunity.

**Parameters:**
- `lead_id`: ID of the lead to retrieve (required)

#### `create_lead`
Create a new lead in the CRM system.

**Parameters:**
- `name`: Lead name (required)
- `contact_name`: Contact person name
- `email_from`: Email address
- `phone`: Phone number
- `partner_name`: Company name
- `description`: Notes/description
- `team_id`: Sales team ID
- `user_id`: Salesperson ID
- `expected_revenue`: Expected revenue amount
- `program_id`: Academic program ID (ISEP)
- `canal_contacto`: Contact channel (ISEP)
- `programa_interes`: Program of interest (ISEP)

**Example usage:**
```json
{
  "tool": "create_lead",
  "parameters": {
    "name": "Interés en Maestría en Administración",
    "contact_name": "María García",
    "email_from": "maria.garcia@email.com",
    "phone": "+34 612 345 678",
    "program_id": 15,
    "canal_contacto": "Web",
    "expected_revenue": 8500.00
  }
}
```

#### `update_lead`
Update an existing lead/opportunity.

**Parameters:**
- `lead_id`: ID of the lead to update (required)
- All other parameters are optional and same as create_lead
- `progress`: Progress percentage (ISEP specific)

#### `convert_lead_to_opportunity`
Convert a lead to opportunity status.

**Parameters:**
- `lead_id`: Lead ID to convert (required)
- `partner_id`: Partner ID to associate
- `user_id`: Salesperson ID to assign
- `team_id`: Sales team ID to assign

### Partner/Contact Tools

#### `list_partners`
List and filter partners/contacts.

**Parameters:**
- `name`: Filter by name (partial match)
- `email`: Filter by email (partial match)
- `phone`: Filter by phone (partial match)
- `is_company`: Filter companies (True) or individuals (False)
- `customer_rank`: Filter customers (>0 for customers)
- `supplier_rank`: Filter suppliers (>0 for suppliers)
- `category_id`: Filter by category ID
- `country_id`: Filter by country ID
- `limit`: Maximum records to return

#### `get_partner_details`
Get detailed information about a specific partner.

**Parameters:**
- `partner_id`: Partner ID to retrieve (required)

#### `create_partner`
Create a new partner/contact.

**Parameters:**
- `name`: Partner name (required)
- `email`: Email address
- `phone`: Phone number
- `mobile`: Mobile number
- `is_company`: True for companies, False for individuals
- `website`: Website URL
- `vat`: VAT/Tax ID
- `street`: Street address
- `city`: City
- `zip`: ZIP/Postal code
- `country_id`: Country ID
- `customer_rank`: Customer rank (0=not customer, 1+=customer)
- `supplier_rank`: Supplier rank (0=not supplier, 1+=supplier)
- `category_ids`: List of category IDs

**Example usage:**
```json
{
  "tool": "create_partner",
  "parameters": {
    "name": "Universidad Ejemplo S.A.",
    "email": "contacto@universidad-ejemplo.com",
    "phone": "+34 91 123 4567",
    "is_company": true,
    "website": "https://www.universidad-ejemplo.com",
    "street": "Calle Principal 123",
    "city": "Madrid",
    "zip": "28001",
    "country_id": 69,
    "customer_rank": 1
  }
}
```

#### `update_partner`
Update an existing partner/contact.

**Parameters:**
- `partner_id`: Partner ID to update (required)
- All other parameters are optional and same as create_partner

### Auxiliary Tools

#### `list_crm_stages`
Get available CRM stages for leads/opportunities.

**Parameters:**
- `team_id`: Filter stages by team ID (optional)

#### `list_crm_teams`
Get available sales teams.

#### `get_lead_activities`
Get activities related to a lead/opportunity.

**Parameters:**
- `lead_id`: Lead/Opportunity ID (required)

#### `get_academic_programs`
Get available academic programs (ISEP specific).

**Parameters:**
- `active_only`: Return only active programs (default: True)

#### `get_crm_dashboard_stats`
Get CRM performance statistics and metrics.

**Parameters:**
- `team_id`: Filter by team ID
- `user_id`: Filter by user ID  
- `date_from/date_to`: Date range for statistics

**Returns:**
- Leads and opportunities counts
- Win/loss rates
- Revenue statistics
- Active pipeline metrics

## Universidad ISEP Custom Fields

The CRM module includes specific fields for Universidad ISEP:

### Lead/Opportunity Fields
- **`x_studio_programa_academico`**: Academic program association
- **`x_studio_canal_de_contacto`**: Contact channel (Web, Phone, Email, etc.)
- **`x_studio_programa_de_inters`**: Program of interest
- **`x_studio_fecha_de_firma`**: Contract signature date
- **`x_studio_duracin_de_convenio`**: Contract duration
- **`progress`**: Lead progress percentage
- **`mautic_export`**: Mautic export flag
- **`x_studio_id_mautic`**: Mautic ID for integration
- **Google Analytics fields**: Source, campaign, term tracking

### Data Flow Examples

#### Complete Lead Lifecycle
1. **Create Lead**: Student shows interest in a program
2. **Update Progress**: Track engagement and follow-up activities
3. **Associate Program**: Link to specific academic program
4. **Convert to Opportunity**: When serious purchase intent is shown
5. **Track to Closure**: Monitor through stages to enrollment

#### Partner Management
1. **Create Partner**: Add new educational institution or corporate client
2. **Categorize**: Assign appropriate categories (University, Corporate, etc.)
3. **Link to Opportunities**: Associate with relevant leads/opportunities
4. **Update Information**: Maintain current contact and business data

## Best Practices

1. **Use Consistent Naming**: Follow naming conventions for leads and partners
2. **Track Progress**: Regularly update progress percentages for leads
3. **Proper Categorization**: Use appropriate categories and contact channels
4. **Stage Management**: Move leads through stages systematically
5. **Activity Logging**: Use activities to track communications and follow-ups
6. **Data Quality**: Keep contact information current and validated

## Integration Notes

- **Mautic Integration**: The system supports Mautic CRM synchronization
- **Google Analytics**: Track lead sources and campaign effectiveness  
- **Academic Programs**: Integrated with product catalog for program management
- **Multi-team Support**: Handles multiple sales teams and territories
- **Reporting Ready**: All data structured for analytics and reporting

This CRM module provides comprehensive functionality for managing the complete student recruitment and enrollment process specific to Universidad ISEP's needs while maintaining compatibility with standard Odoo CRM features.
