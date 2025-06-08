"""Database schemas and table definitions for the data retrieval agent."""

from typing import Dict, List, Any
import json


# User Table Schema
USER_TABLE_SCHEMA = [
    {
        "name": "shipping_address",
        "type": "object",
        "description": "Most recent shipping address for the customer.",
        "sample_value": "{\"address1\": \"123 Main St\", \"address2\": \"Apt 4B\", \"city\": \"New York\", \"company\": \"Acme Corp\", \"country\": \"US\", \"last_name\": \"Doe\", \"latitude\": \"40.7128\", \"longitude\": \"-74.0060\", \"name\": \"John Doe\", \"phone\": \"+1234567890\", \"province\": \"NY\", \"zip\": \"10001\", \"first_name\": \"John\"}",
        "properties": [
            {"name": "address1", "type": "string", "description": "Street address, line 1", "example": "123 Main St"},
            {"name": "address2", "type": "string", "description": "Street address, line 2", "example": "Apt 4B"},
            {"name": "city", "type": "string", "description": "City name", "example": "New York"},
            {"name": "company", "type": "string", "description": "Company name", "example": "Acme Corp"},
            {"name": "country", "type": "string", "description": "Country code (ISO)", "example": "US"},
            {"name": "last_name", "type": "string", "description": "Last name", "example": "Doe"},
            {"name": "latitude", "type": "string", "description": "Latitude", "example": "40.7128"},
            {"name": "longitude", "type": "string", "description": "Longitude", "example": "-74.0060"},
            {"name": "name", "type": "string", "description": "Full name", "example": "John Doe"},
            {"name": "phone", "type": "string", "description": "Phone number", "example": "+1234567890"},
            {"name": "province", "type": "string", "description": "State/Province", "example": "NY"},
            {"name": "zip", "type": "string", "description": "Postal code", "example": "10001"},
            {"name": "first_name", "type": "string", "description": "First name", "example": "John"}
        ],
        "database_value": [{"name": "", "type": ""}]
    }, {
        "name": "customer_tags",
        "type": "array",
        "description": "Tags assigned to the customer for segmentation or workflow automation.",
        "sample_value": "[\"vip\", \"repeat-buyer\"]",
        "database_value": [{"name": "properties_customer_tags", "type": "STRING"}]
    }, {
        "name": "first_order_date",
        "type": "string",
        "description": "Date of the customer's first paid order (ISO 8601 format).",
        "sample_value": "2023-08-31T20:19:00Z",
        "database_value": [{"name": "properties_first_order_date", "type": "TIMESTAMP"}]
    }, {
        "name": "first_seen",
        "type": "string",
        "description": "Timestamp of the customer's first website visit (ISO 8601 format).",
        "sample_value": "2023-08-31T20:19:00Z",
        "database_value": [{"name": "properties_first_seen", "type": "TIMESTAMP"}]
    }, {
        "name": "last_order_date",
        "type": "string",
        "description": "Date of the customer's most recent paid order (ISO 8601 format).",
        "sample_value": "2024-05-01T15:00:00Z",
        "database_value": [{"name": "properties_last_order_date", "type": "TIMESTAMP"}]
    }, {
        "name": "user_id",
        "type": "string",
        "description": "Client-side unique ID for the customer, provided by Shopify.",
        "sample_value": "5816460574766",
        "database_value": [{"name": "properties_user_id", "type": "STRING"}]
    }, {
        "name": "shopify_customer_id",
        "type": "string",
        "description": "Shopify-assigned customer ID.",
        "sample_value": "6359703453860",
        "database_value": [{"name": "properties_shopify_customer_id", "type": "INTEGER"}]
    }, {
        "name": "shopify_customer_notes",
        "type": "string",
        "description": "Admin notes about the customer.",
        "sample_value": "This customer is awesome",
        "database_value": [{"name": "properties_shopify_customer_notes", "type": "STRING"}]
    }, {
        "name": "tax_exempt",
        "type": "boolean",
        "description": "Whether the customer is exempt from tax.",
        "sample_value": False,
        "database_value": [{"name": "properties_tax_exempt", "type": "STRING"}]
    }, {
        "name": "verified_email",
        "type": "boolean",
        "description": "Whether the customer's email is verified.",
        "sample_value": True,
        "database_value": [{"name": "properties_verified_email", "type": "STRING"}]
    }, {
        "name": "initial_utm_medium",
        "type": "string",
        "description": "UTM medium from the first visit (e.g., 'organic', 'cpc').",
        "sample_value": "organic",
        "database_value": [{"name": "properties_initial_utm_medium", "type": "STRING"}]
    }, {
        "name": "utm_medium",
        "type": "string",
        "description": "Most recent UTM medium value.",
        "sample_value": "cpc",
        "database_value": [{"name": "properties_utm_medium", "type": "STRING"}]
    }, {
        "name": "event_type",
        "type": "string",
        "description": "Indicates whether the event is standard or custom.",
        "sample_value": "standard",
        "database_value": [{"name": "", "type": ""}]
    }, {
        "name": "marketing_state",
        "type": "string",
        "description": "Current email marketing state for the customer.",
        "sample_value": "enabled",
        "database_value": [{"name": "properties_marketing_state", "type": "STRING"}]
    }, {
        "name": "initial_utm_source",
        "type": "string",
        "description": "UTM source from the first visit (e.g., 'google', 'facebook').",
        "sample_value": "google",
        "database_value": [{"name": "properties_initial_utm_source", "type": "STRING"}]
    }, {
        "name": "utm_source",
        "type": "string",
        "description": "Most recent UTM source value.",
        "sample_value": "facebook",
        "database_value": [{"name": "properties_utm_source", "type": "STRING"}]
    }, {
        "name": "initial_utm_campaign",
        "type": "string",
        "description": "UTM campaign from the first visit.",
        "sample_value": "summer-sale",
        "database_value": [{"name": "properties_initial_utm_campaign", "type": "STRING"}]
    }, {
        "name": "utm_campaign",
        "type": "string",
        "description": "Most recent UTM campaign value.",
        "sample_value": "new-product-release",
        "database_value": [{"name": "properties_utm_campaign", "type": "STRING"}]
    }, {
        "name": "initial_utm_content",
        "type": "string",
        "description": "UTM content from the first visit.",
        "sample_value": "banner",
        "database_value": [{"name": "properties_initial_utm_content", "type": "STRING"}]
    }, {
        "name": "utm_content",
        "type": "string",
        "description": "Most recent UTM content value.",
        "sample_value": "video_ad",
        "database_value": [{"name": "properties_utm_content", "type": "STRING"}]
    }, {
        "name": "email_marketing_consent_opt_in_level",
        "type": "string",
        "description": "Email marketing consent opt-in level.",
        "sample_value": "single_opt_in",
        "database_value": [{"name": "properties_email_marketing_consent_opt_in_level", "type": "STRING"}]
    }, {
        "name": "email_marketing_consent_state",
        "type": "string",
        "description": "Whether the user is subscribed to email marketing.",
        "sample_value": "subscribed",
        "database_value": [{"name": "properties_email_marketing_consent_state", "type": "STRING"}]
    }, {
        "name": "initial_utm_term",
        "type": "string",
        "description": "UTM term from the first visit (e.g., paid keyword).",
        "sample_value": "sunscreen",
        "database_value": [{"name": "properties_initial_utm_term", "type": "STRING"}]
    }, {
        "name": "utm_term",
        "type": "string",
        "description": "Most recent UTM term value.",
        "sample_value": "vegan-shampoo",
        "database_value": [{"name": "properties_utm_term", "type": "STRING"}]
    }, {
        "name": "order_count",
        "type": "number",
        "description": "Total number of orders placed by the customer.",
        "sample_value": 10,
        "database_value": [{"name": "properties_order_count", "type": "FLOAT"}]
    }, {
        "name": "total_spent",
        "type": "number",
        "description": "Total amount spent by the customer (in their currency).",
        "sample_value": 199.95,
        "database_value": [{"name": "properties_total_spent", "type": "FLOAT"}]
    }, {
        "name": "$ignore_time",
        "type": "boolean",
        "description": "If true, ignore the event timestamp for analytics.",
        "sample_value": False,
        "database_value": [{"name": "", "type": ""}]
    }]



EVENT_TABLE_SCHEMA = [
    {
        "event_name": "Cart Abandoned",
        "use_case": "Used to track when a customer abandons their cart. Supports retargeting, abandonment recovery, and funnel analysis.",
        "description": "The cart_abandoned event logs an instance where a abandons their cart",
        "source": "[Server-side, Vendo]",
        "status": "Healthy",
        "first_seen": "2024-03-14",
        "last_seen": "2025-05-16",
        "count": "1",
        "change": "-1.0",
        "properties": [{
            "name": "billing_address",
            "type": "object",
            "description": "The billing address where the order will be billed to",
            "sample_value": "{\"address1\": \"123 Main St\", \"address2\": \"Apt 4B\", \"city\": \"New York\", \"company\": \"Acme Corp\", \"country\": \"US\", \"last_name\": \"Doe\", \"latitude\": \"40.7128\", \"longitude\": \"-74.0060\", \"name\": \"John Doe\", \"phone\": \"+1234567890\", \"province\": \"NY\", \"zip\": \"10001\", \"first_name\": \"John\"}",
            "properties": [
                {"name": "address1", "type": "string", "description": "Street address, line 1", "example": "123 Main St"},
                {"name": "address2", "type": "string", "description": "Street address, line 2", "example": "Apt 4B"},
                {"name": "city", "type": "string", "description": "City name", "example": "New York"},
                {"name": "company", "type": "string", "description": "Company name", "example": "Acme Corp"},
                {"name": "country", "type": "string", "description": "Country code (ISO)", "example": "US"},
                {"name": "last_name", "type": "string", "description": "Last name", "example": "Doe"},
                {"name": "latitude", "type": "string", "description": "Latitude", "example": "40.7128"},
                {"name": "longitude", "type": "string", "description": "Longitude", "example": "-74.0060"},
                {"name": "name", "type": "string", "description": "Full name", "example": "John Doe"},
                {"name": "phone", "type": "string", "description": "Phone number", "example": "+1234567890"},
                {"name": "province", "type": "string", "description": "State/Province", "example": "NY"},
                {"name": "zip", "type": "string", "description": "Postal code", "example": "10001"},
                {"name": "first_name", "type": "string", "description": "First name", "example": "John"}
            ],
            "database_value": [{"name": "", "type": ""}]
        }
        ,

        {
            "name": "shipping_address",
            "type": "object",
            "description": "The shipping address to where the line items will be shipped",
            "sample_value": "{\"address1\": \"123 Main St\", \"address2\": \"Apt 4B\", \"city\": \"New York\", \"company\": \"Acme Corp\", \"country\": \"US\", \"last_name\": \"Doe\", \"latitude\": \"40.7128\", \"longitude\": \"-74.0060\", \"name\": \"John Doe\", \"phone\": \"+1234567890\", \"province\": \"NY\", \"zip\": \"10001\", \"first_name\": \"John\"}",
            "properties": [
                {"name": "address1", "type": "string", "description": "Street address, line 1", "example": "123 Main St"},
                {"name": "address2", "type": "string", "description": "Street address, line 2", "example": "Apt 4B"},
                {"name": "city", "type": "string", "description": "City name", "example": "New York"},
                {"name": "company", "type": "string", "description": "Company name", "example": "Acme Corp"},
                {"name": "country", "type": "string", "description": "Country code (ISO)", "example": "US"},
                {"name": "last_name", "type": "string", "description": "Last name", "example": "Doe"},
                {"name": "latitude", "type": "string", "description": "Latitude", "example": "40.7128"},
                {"name": "longitude", "type": "string", "description": "Longitude", "example": "-74.0060"},
                {"name": "name", "type": "string", "description": "Full name", "example": "John Doe"},
                {"name": "phone", "type": "string", "description": "Phone number", "example": "+1234567890"},
                {"name": "province", "type": "string", "description": "State/Province", "example": "NY"},
                {"name": "zip", "type": "string", "description": "Postal code", "example": "10001"},
                {"name": "first_name", "type": "string", "description": "First name", "example": "John"}
            ],
            "database_value": [{"name": "", "type": ""}]
        }, {
            "name": "products",
            "type": "array",
            "description": "A list of line item objects, each one containing information about an item in the checkout",
            "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
            "properties": [
                {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
                {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
                {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
                {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
                {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
                {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
                {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
                {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
                {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
                {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
                {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
                {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
            ],
            "database_value": [{"name": "", "type": ""}]
        }, {
            "name": "checkout_attributes",
            "type": "array",
            "description": "A list of attributes accumulated throughout the checkout process",
            "sample_value": "[\"value: /}\", \"value: 123-abc}]\", \"[{name: landing_page\", \"{name: cart_token\"]"
        }, {
            "name": "custom_order_attributes",
            "type": "string",
            "description": "A list of details that have been added to the order.",
            "sample_value": "[\"value: google}\", \"value: google}\", \"value: new}]\", \"[{key: utm_source\", \"{key: customer_type\", \"{key: utm_campaign\"]"
        }, {
            "name": "vendo_tracking_version",
            "type": "string",
            "description": "Vendo tracking version",
            "sample_value": "[1.2.1]"
        }, {
            "name": "checkout_id",
            "type": "string",
            "description": "The unique id of the checkout process",
            "sample_value": "[29563359395886]"
        }, {
            "name": "$insert_id",
            "type": "string",
            "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
            "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
        }, {
            "name": "$ignore_time",
            "type": "boolean",
            "description": "Ignore Time",
            "sample_value": "[True]"
        }, {
            "name": "$import",
            "type": "boolean",
            "description": "To determine if this a server side event or not",
            "sample_value": "[True]"
        }, {
            "name": "buyer_accepts_marketing",
            "type": "boolean",
            "description": "Buyer has consented to receiving marketing email",
            "sample_value": "[True]"
        }, {
            "name": "currency",
            "type": "string",
            "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes",
            "sample_value": "[USD]"
        }, {
            "name": "$source",
            "type": "string",
            "description": "The source of where the data is coming from",
            "sample_value": "[Vendo - Shopify Data Intelligence]"
        }, {
            "name": "utm_medium",
            "type": "string",
            "description": "The last seen attributed medium value",
            "sample_value": "[blog, organic, social]"
        }, {
            "name": "event_type",
            "type": "string",
            "description": "Indicates whether an event is a standard or a custom event",
            "sample_value": "[custom, standard]"
        }, {
            "name": "checkout_token",
            "type": "string",
            "description": "A unique identifier for a particular checkout",
            "sample_value": "[f2497b88ed60f51f6f3698bf7bccd74f]"
        }, {
            "name": "utm_source",
            "type": "string",
            "description": "The last seen attributed source value",
            "sample_value": "[facebook, google, linkedin]"
        }, {
            "name": "abandoned_checkout_url",
            "type": "string",
            "description": "Link to the cart that was abandoned",
            "sample_value": "[https://www.my-shop.com/checkout-url]"
        }, {
            "name": "utm_campaign",
            "type": "string",
            "description": "The last seen attributed campaign value",
            "sample_value": "[new-product-release, summer-sale]"
        }, {
            "name": "utm_content",
            "type": "string",
            "description": "The last seen attributed content value",
            "sample_value": "[pricing, sales]"
        }, {
            "name": "utm_term",
            "type": "string",
            "description": "The last seen attributed term value",
            "sample_value": "[sunscreen, vegan-shampoo]"
        }, {
            "name": "email",
            "type": "string",
            "description": "The email attached to this checkout",
            "sample_value": "[test.user@email.com]"
        }, {
            "name": "source_name",
            "type": "string",
            "description": "The source of the abandonment",
            "sample_value": "[web]"
        }, {
            "name": "cart_subtotal_amount",
            "type": "number",
            "description": "The price at checkout before duties, shipping, and taxes",
            "sample_value": "[100.25]"
        }, {
            "name": "cart_total_amount",
            "type": "number",
            "description": "The sum of all the items in the checkout, including duties, taxes, and discounts",
            "sample_value": "[100.25]"
        }, {
            "name": "tax_amount",
            "type": "number",
            "description": "The sum of all the taxes applied to the line items and shipping lines in the checkout",
            "sample_value": "[100.25]"
        }, {
            "name": "total_discounts",
            "type": "number",
            "description": "The total amount of all discounts applied to the order",
            "sample_value": "[100.25]"
        }, {
            "name": "time",
            "type": "number",
            "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
            "sample_value": 1748189059
        }]
    }, 

    {
    "event_name": "Cart Viewed",
    "use_case": "Used to analyze cart engagement and conversion rates. Helps identify drop-off points in the purchase funnel.",
    "description": "The cart_viewed event logs an instance where a customer visited the cart page",
    "source": "[Client-Side, Vendo]",
    "status": "Healthy",
    "first_seen": "2024-04-02",
    "last_seen": "2024-10-15",
    "count": "0",
    "change": None,
    "properties": [{
        "name": "products",
        "type": "array",
        "description": "A list of line item objects, each one containing information about an item in the checkout",
        "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
        "properties": [
            {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
            {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
            {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
            {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
            {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
            {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
            {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
            {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
            {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
            {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
            {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
            {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
        ]
    }, {
        "name": "path_name",
        "type": "string",
        "description": "The path of the URL",
        "sample_value": "[/collections/all]"
    }, {
        "name": "$insert_id",
        "type": "string",
        "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
        "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
    }, {
        "name": "page_title",
        "type": "string",
        "description": "The title of the page",
        "sample_value": "[Products – gamanalytics]"
    }, {
        "name": "currency",
        "type": "string",
        "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes",
        "sample_value": "[USD]"
    }, {
        "name": "$source",
        "type": "string",
        "description": "The source of where the data is coming from",
        "sample_value": "[Vendo - Shopify Data Intelligence]"
    }, {
        "name": "utm_medium",
        "type": "string",
        "description": "The last seen attributed medium value",
        "sample_value": "[blog, organic, social]"
    }, {
        "name": "event_type",
        "type": "string",
        "description": "Indicates whether an event is a standard or a custom event",
        "sample_value": "[custom, standard]"
    }, {
        "name": "utm_source",
        "type": "string",
        "description": "The last seen attributed source value",
        "sample_value": "[facebook, google, linkedin]"
    }, {
        "name": "utm_campaign",
        "type": "string",
        "description": "The last seen attributed campaign value",
        "sample_value": "[new-product-release, summer-sale]"
    }, {
        "name": "utm_content",
        "type": "string",
        "description": "The last seen attributed content value",
        "sample_value": "[pricing, sales]"
    }, {
        "name": "utm_term",
        "type": "string",
        "description": "The last seen attributed term value",
        "sample_value": "[sunscreen, vegan-shampoo]"
    }, {
        "name": "amount",
        "type": "number",
        "description": "Used for the monetary amount of the object",
        "sample_value": "[100]"
    }, {
        "name": "quantity",
        "type": "number",
        "description": "Quantity added to cart",
        "sample_value": "[1]"
    }, {
        "name": "time",
        "type": "number",
        "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
        "sample_value": 1748189059
    }]
    }, {
    "event_name": "Checkout Address Info Submitted",
    "use_case": "Used to capture address information during checkout for fulfillment and fraud prevention.",
    "description": "The checkout_address_info_submitted event logs an instance of a buyer submitting their mailing address. This event is only available in checkouts where checkout extensibility for customizations is enabled",
    "source": "[Client-Side, Vendo]",
    "status": "Healthy",
    "first_seen": "2024-04-15",
    "last_seen": "2025-05-21",
    "count": "23",
    "change": "0.0",
    "properties": [{
        "name": "shipping_address",
        "type": "object",
        "description": "The shipping address to where the line items will be shipped",
        "sample_value": "{\"address1\": \"123 Main St\", \"address2\": \"Apt 4B\", \"city\": \"New York\", \"company\": \"Acme Corp\", \"country\": \"US\", \"last_name\": \"Doe\", \"latitude\": \"40.7128\", \"longitude\": \"-74.0060\", \"name\": \"John Doe\", \"phone\": \"+1234567890\", \"province\": \"NY\", \"zip\": \"10001\", \"first_name\": \"John\"}",
        "properties": [
            {"name": "address1", "type": "string", "description": "Street address, line 1", "example": "123 Main St"},
            {"name": "address2", "type": "string", "description": "Street address, line 2", "example": "Apt 4B"},
            {"name": "city", "type": "string", "description": "City name", "example": "New York"},
            {"name": "company", "type": "string", "description": "Company name", "example": "Acme Corp"},
            {"name": "country", "type": "string", "description": "Country code (ISO)", "example": "US"},
            {"name": "last_name", "type": "string", "description": "Last name", "example": "Doe"},
            {"name": "latitude", "type": "string", "description": "Latitude", "example": "40.7128"},
            {"name": "longitude", "type": "string", "description": "Longitude", "example": "-74.0060"},
            {"name": "name", "type": "string", "description": "Full name", "example": "John Doe"},
            {"name": "phone", "type": "string", "description": "Phone number", "example": "+1234567890"},
            {"name": "province", "type": "string", "description": "State/Province", "example": "NY"},
            {"name": "zip", "type": "string", "description": "Postal code", "example": "10001"},
            {"name": "first_name", "type": "string", "description": "First name", "example": "John"}
        ]
    }, {
        "name": "products",
        "type": "array",
        "description": "A list of line item objects, each one containing information about an item in the checkout",
        "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
        "properties": [
            {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
            {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
            {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
            {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
            {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
            {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
            {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
            {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
            {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
            {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
            {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
            {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
        ]
    }, {
        "name": "checkout_attributes",
        "type": "array",
        "description": "A list of attributes accumulated throughout the checkout process",
        "sample_value": "[\"value: /}\", \"value: 123-abc}]\", \"[{name: landing_page\", \"{name: cart_token\"]"
    }, {
        "name": "phone",
        "type": "string",
        "description": "The phone number of the address",
        "sample_value": "[+14253874474]"
    }, {
        "name": "path_name",
        "type": "string",
        "description": "The path of the URL",
        "sample_value": "[/collections/all]"
    }, {
        "name": "$insert_id",
        "type": "string",
        "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
        "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
    }, {
        "name": "order_id",
        "type": "string",
        "description": "The order ID is assigned by Shopify. This is the displayed order ID that shows in the store admin",
        "sample_value": "[5363269]"
    }, {
        "name": "page_title",
        "type": "string",
        "description": "The title of the page",
        "sample_value": "[Products – gamanalytics]"
    }, {
        "name": "currency",
        "type": "string",
        "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes",
        "sample_value": "[USD]"
    }, {
        "name": "$source",
        "type": "string",
        "description": "The source of where the data is coming from",
        "sample_value": "[Vendo - Shopify Data Intelligence]"
    }, {
        "name": "utm_medium",
        "type": "string",
        "description": "The last seen attributed medium value",
        "sample_value": "[blog, organic, social]"
    }, {
        "name": "event_type",
        "type": "string",
        "description": "Indicates whether an event is a standard or a custom event",
        "sample_value": "[custom, standard]"
    }, {
        "name": "checkout_token",
        "type": "string",
        "description": "A unique identifier for a particular checkout",
        "sample_value": "[f2497b88ed60f51f6f3698bf7bccd74f]"
    }, {
        "name": "utm_source",
        "type": "string",
        "description": "The last seen attributed source value",
        "sample_value": "[facebook, google, linkedin]"
    }, {
        "name": "utm_campaign",
        "type": "string",
        "description": "The last seen attributed campaign value",
        "sample_value": "[new-product-release, summer-sale]"
    }, {
        "name": "utm_content",
        "type": "string",
        "description": "The last seen attributed content value",
        "sample_value": "[pricing, sales]"
    }, {
        "name": "utm_term",
        "type": "string",
        "description": "The last seen attributed term value",
        "sample_value": "[sunscreen, vegan-shampoo]"
    }, {
        "name": "email",
        "type": "string",
        "description": "The email attached to this checkout",
        "sample_value": "[test.user@email.com]"
    }, {
        "name": "cart_subtotal_amount",
        "type": "number",
        "description": "The price at checkout before duties, shipping, and taxes",
        "sample_value": "[100.25]"
    }, {
        "name": "cart_total_amount",
        "type": "number",
        "description": "The sum of all the items in the checkout, including duties, taxes, and discounts",
        "sample_value": "[100.25]"
    }, {
        "name": "tax_amount",
        "type": "number",
        "description": "The sum of all the taxes applied to the line items and shipping lines in the checkout",
        "sample_value": "[100.25]"
    }, {
        "name": "shipping_amount",
        "type": "number",
        "description": "Total shipping cost",
        "sample_value": "[6.99]"
    }, {
        "name": "time",
        "type": "number",
        "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
        "sample_value": 1748189059
    }]
    }, 

    {
  "event_name": "Checkout Completed",
  "description": "The checkout_completed event logs when a visitor completes a purchase. This event is available on the order status and checkout pages",
  "source": "[Client-Side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-04-27",
  "last_seen": "2025-05-26",
  "count": "30",
  "change": "0.0",
  "properties": [{
    "name": "shipping_address",
    "type": "object",
    "description": "The shipping address to where the line items will be shipped",
    "sample_value": "{\"address1\": \"123 Main St\", \"address2\": \"Apt 4B\", \"city\": \"New York\", \"company\": \"Acme Corp\", \"country\": \"US\", \"last_name\": \"Doe\", \"latitude\": \"40.7128\", \"longitude\": \"-74.0060\", \"name\": \"John Doe\", \"phone\": \"+1234567890\", \"province\": \"NY\", \"zip\": \"10001\", \"first_name\": \"John\"}",
    "properties": [
        {"name": "address1", "type": "string", "description": "Street address, line 1", "example": "123 Main St"},
        {"name": "address2", "type": "string", "description": "Street address, line 2", "example": "Apt 4B"},
        {"name": "city", "type": "string", "description": "City name", "example": "New York"},
        {"name": "company", "type": "string", "description": "Company name", "example": "Acme Corp"},
        {"name": "country", "type": "string", "description": "Country code (ISO)", "example": "US"},
        {"name": "last_name", "type": "string", "description": "Last name", "example": "Doe"},
        {"name": "latitude", "type": "string", "description": "Latitude", "example": "40.7128"},
        {"name": "longitude", "type": "string", "description": "Longitude", "example": "-74.0060"},
        {"name": "name", "type": "string", "description": "Full name", "example": "John Doe"},
        {"name": "phone", "type": "string", "description": "Phone number", "example": "+1234567890"},
        {"name": "province", "type": "string", "description": "State/Province", "example": "NY"},
        {"name": "zip", "type": "string", "description": "Postal code", "example": "10001"},
        {"name": "first_name", "type": "string", "description": "First name", "example": "John"}
    ]
  }, {
    "name": "products",
    "type": "array",
    "description": "A list of line item objects, each one containing information about an item in the checkout",
    "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
    "properties": [
        {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
        {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
        {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
        {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
        {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
        {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
        {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
        {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
        {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
        {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
        {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
        {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "checkout_attributes",
    "type": "array",
    "description": "A list of attributes accumulated throughout the checkout process",
    "sample_value": "[\"value: /}\", \"value: 123-abc}]\", \"[{name: landing_page\", \"{name: cart_token\"]"
  }, {
    "name": "phone",
    "type": "string",
    "description": "The phone number of the address",
    "sample_value": "[+14253874474]"
  }, {
    "name": "path_name",
    "type": "string",
    "description": "The path of the URL",
    "sample_value": "[/collections/all]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "order_id",
    "type": "string",
    "description": "The order ID is assigned by Shopify. This is the displayed order ID that shows in the store admin",
    "sample_value": "[5363269]"
  }, {
    "name": "checkout_token",
    "type": "string",
    "description": "A unique identifier for a particular checkout",
    "sample_value": "[57a0a97bf029929066b2a01b5eadd9d1]"
  }, {
    "name": "page_title",
    "type": "string",
    "description": "The title of the page",
    "sample_value": "[Products – gamanalytics]"
  }, {
    "name": "currency",
    "type": "string",
    "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes",
    "sample_value": "[USD]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "email",
    "type": "string",
    "description": "The email attached to this checkout",
    "sample_value": "[test.user@email.com]"
  }, {
    "name": "cart_subtotal_amount",
    "type": "number",
    "description": "The price at checkout before duties, shipping, and taxes",
    "sample_value": "[100.25]"
  }, {
    "name": "cart_total_amount",
    "type": "number",
    "description": "The sum of all the items in the checkout, including duties, taxes, and discounts",
    "sample_value": "[100.25]"
  }, {
    "name": "tax_amount",
    "type": "number",
    "description": "The sum of all the taxes applied to the line items and shipping lines in the checkout",
    "sample_value": "[100.25]"
  }, {
    "name": "shipping_amount",
    "type": "number",
    "description": "Total shipping cost",
    "sample_value": "[6.99]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Checkout Contact Info Submitted",
  "use_case": "Used to capture contact information during checkout for communication and order updates.",
  "description": "The checkout_contact_info_submitted event logs an instance where a buyer submits a checkout form. This event is only available in checkouts where checkout extensibility for customizations is enabled",
  "source": "[Client-Side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-04-15",
  "last_seen": "2025-02-23",
  "count": "0",
  "change": None,
  "properties": [{
    "name": "billing_address",
    "type": "object",
    "description": "The billing address where the order will be billed to",
    "sample_value": "{\"address1\": \"123 Main St\", \"address2\": \"Apt 4B\", \"city\": \"New York\", \"company\": \"Acme Corp\", \"country\": \"US\", \"last_name\": \"Doe\", \"latitude\": \"40.7128\", \"longitude\": \"-74.0060\", \"name\": \"John Doe\", \"phone\": \"+1234567890\", \"province\": \"NY\", \"zip\": \"10001\", \"first_name\": \"John\"}",
    "properties": [
        {"name": "address1", "type": "string", "description": "Street address, line 1", "example": "123 Main St"},
        {"name": "address2", "type": "string", "description": "Street address, line 2", "example": "Apt 4B"},
        {"name": "city", "type": "string", "description": "City name", "example": "New York"},
        {"name": "company", "type": "string", "description": "Company name", "example": "Acme Corp"},
        {"name": "country", "type": "string", "description": "Country code (ISO)", "example": "US"},
        {"name": "last_name", "type": "string", "description": "Last name", "example": "Doe"},
        {"name": "latitude", "type": "string", "description": "Latitude", "example": "40.7128"},
        {"name": "longitude", "type": "string", "description": "Longitude", "example": "-74.0060"},
        {"name": "name", "type": "string", "description": "Full name", "example": "John Doe"},
        {"name": "phone", "type": "string", "description": "Phone number", "example": "+1234567890"},
        {"name": "province", "type": "string", "description": "State/Province", "example": "NY"},
        {"name": "zip", "type": "string", "description": "Postal code", "example": "10001"},
        {"name": "first_name", "type": "string", "description": "First name", "example": "John"}
    ]
  }, {
    "name": "shipping_address",
    "type": "object",
    "description": "The shipping address to where the line items will be shipped",
    "sample_value": "{\"address1\": \"123 Main St\", \"address2\": \"Apt 4B\", \"city\": \"New York\", \"company\": \"Acme Corp\", \"country\": \"US\", \"last_name\": \"Doe\", \"latitude\": \"40.7128\", \"longitude\": \"-74.0060\", \"name\": \"John Doe\", \"phone\": \"+1234567890\", \"province\": \"NY\", \"zip\": \"10001\", \"first_name\": \"John\"}",
    "properties": [
        {"name": "address1", "type": "string", "description": "Street address, line 1", "example": "123 Main St"},
        {"name": "address2", "type": "string", "description": "Street address, line 2", "example": "Apt 4B"},
        {"name": "city", "type": "string", "description": "City name", "example": "New York"},
        {"name": "company", "type": "string", "description": "Company name", "example": "Acme Corp"},
        {"name": "country", "type": "string", "description": "Country code (ISO)", "example": "US"},
        {"name": "last_name", "type": "string", "description": "Last name", "example": "Doe"},
        {"name": "latitude", "type": "string", "description": "Latitude", "example": "40.7128"},
        {"name": "longitude", "type": "string", "description": "Longitude", "example": "-74.0060"},
        {"name": "name", "type": "string", "description": "Full name", "example": "John Doe"},
        {"name": "phone", "type": "string", "description": "Phone number", "example": "+1234567890"},
        {"name": "province", "type": "string", "description": "State/Province", "example": "NY"},
        {"name": "zip", "type": "string", "description": "Postal code", "example": "10001"},
        {"name": "first_name", "type": "string", "description": "First name", "example": "John"}
    ]
  }, {
    "name": "products",
    "type": "array",
    "description": "A list of line item objects, each one containing information about an item in the checkout",
    "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
    "properties": [
        {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
        {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
        {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
        {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
        {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
        {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
        {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
        {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
        {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
        {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
        {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
        {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "checkout_attributes",
    "type": "array",
    "description": "A list of attributes accumulated throughout the checkout process",
    "sample_value": "[\"value: /}\", \"value: 123-abc}]\", \"[{name: landing_page\", \"{name: cart_token\"]"
  }, {
    "name": "phone",
    "type": "string",
    "description": "The phone number of the address",
    "sample_value": "[+14253874474]"
  }, {
    "name": "path_name",
    "type": "string",
    "description": "The path of the URL",
    "sample_value": "[/collections/all]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "order_id",
    "type": "string",
    "description": "The order ID is assigned by Shopify. This is the displayed order ID that shows in the store admin",
    "sample_value": "[5363269]"
  }, {
    "name": "checkout_token",
    "type": "string",
    "description": "A unique identifier for a particular checkout",
    "sample_value": "[57a0a97bf029929066b2a01b5eadd9d1]"
  }, {
    "name": "page_title",
    "type": "string",
    "description": "The title of the page",
    "sample_value": "[Products – gamanalytics]"
  }, {
    "name": "currency",
    "type": "string",
    "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes",
    "sample_value": "[USD]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "email",
    "type": "string",
    "description": "The email attached to this checkout",
    "sample_value": "[test.user@email.com]"
  }, {
    "name": "cart_subtotal_amount",
    "type": "number",
    "description": "The price at checkout before duties, shipping, and taxes",
    "sample_value": "[100.25]"
  }, {
    "name": "cart_total_amount",
    "type": "number",
    "description": "The sum of all the items in the checkout, including duties, taxes, and discounts",
    "sample_value": "[100.25]"
  }, {
    "name": "tax_amount",
    "type": "number",
    "description": "The sum of all the taxes applied to the line items and shipping lines in the checkout",
    "sample_value": "[100.25]"
  }, {
    "name": "shipping_amount",
    "type": "number",
    "description": "Total shipping cost",
    "sample_value": "[6.99]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Checkout Shipping Info Submitted",
  "use_case": "Used to track shipping choices and preferences for logistics and delivery optimization.",
  "description": "The checkout_shipping_info_submitted event logs an instance where the buyer chooses a shipping rate. This event is only available in checkouts where checkout extensibility for customizations is enabled",
  "source": "[Client-Side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-04-24",
  "last_seen": "2025-05-29",
  "count": "66",
  "change": "0.0",
  "properties": [{
    "name": "shipping_address",
    "type": "object",
    "description": "The shipping address to where the line items will be shipped",
    "sample_value": "{\"address1\": \"123 Main St\", \"address2\": \"Apt 4B\", \"city\": \"New York\", \"company\": \"Acme Corp\", \"country\": \"US\", \"last_name\": \"Doe\", \"latitude\": \"40.7128\", \"longitude\": \"-74.0060\", \"name\": \"John Doe\", \"phone\": \"+1234567890\", \"province\": \"NY\", \"zip\": \"10001\", \"first_name\": \"John\"}",
    "properties": [
        {"name": "address1", "type": "string", "description": "Street address, line 1", "example": "123 Main St"},
        {"name": "address2", "type": "string", "description": "Street address, line 2", "example": "Apt 4B"},
        {"name": "city", "type": "string", "description": "City name", "example": "New York"},
        {"name": "company", "type": "string", "description": "Company name", "example": "Acme Corp"},
        {"name": "country", "type": "string", "description": "Country code (ISO)", "example": "US"},
        {"name": "last_name", "type": "string", "description": "Last name", "example": "Doe"},
        {"name": "latitude", "type": "string", "description": "Latitude", "example": "40.7128"},
        {"name": "longitude", "type": "string", "description": "Longitude", "example": "-74.0060"},
        {"name": "name", "type": "string", "description": "Full name", "example": "John Doe"},
        {"name": "phone", "type": "string", "description": "Phone number", "example": "+1234567890"},
        {"name": "province", "type": "string", "description": "State/Province", "example": "NY"},
        {"name": "zip", "type": "string", "description": "Postal code", "example": "10001"},
        {"name": "first_name", "type": "string", "description": "First name", "example": "John"}
    ]
  }, {
    "name": "products",
    "type": "array",
    "description": "A list of line item objects, each one containing information about an item in the checkout",
    "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
    "properties": [
        {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
        {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
        {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
        {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
        {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
        {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
        {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
        {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
        {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
        {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
        {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
        {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "checkout_attributes",
    "type": "array",
    "description": "A list of attributes accumulated throughout the checkout process",
    "sample_value": "[\"value: /}\", \"value: 123-abc}]\", \"[{name: landing_page\", \"{name: cart_token\"]"
  }, {
    "name": "phone",
    "type": "string",
    "description": "The phone number of the address",
    "sample_value": "[+14253874474]"
  }, {
    "name": "path_name",
    "type": "string",
    "description": "The path of the URL",
    "sample_value": "[/collections/all]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "order_id",
    "type": "string",
    "description": "The order ID is assigned by Shopify. This is the displayed order ID that shows in the store admin",
    "sample_value": "[5363269]"
  }, {
    "name": "checkout_token",
    "type": "string",
    "description": "A unique identifier for a particular checkout",
    "sample_value": "[57a0a97bf029929066b2a01b5eadd9d1]"
  }, {
    "name": "page_title",
    "type": "string",
    "description": "The title of the page",
    "sample_value": "[Products – gamanalytics]"
  }, {
    "name": "currency",
    "type": "string",
    "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes",
    "sample_value": "[USD]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "shopify_client_id",
    "type": "string",
    "description": "The clientside ID assigned by Shopify",
    "sample_value": "[d606bc45-b9fa-4fa5-b038-488125ab7264]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "email",
    "type": "string",
    "description": "The email attached to this checkout",
    "sample_value": "[test.user@email.com]"
  }, {
    "name": "cart_subtotal_amount",
    "type": "number",
    "description": "The price at checkout before duties, shipping, and taxes",
    "sample_value": "[100.25]"
  }, {
    "name": "cart_total_amount",
    "type": "number",
    "description": "The sum of all the items in the checkout, including duties, taxes, and discounts",
    "sample_value": "[100.25]"
  }, {
    "name": "tax_amount",
    "type": "number",
    "description": "The sum of all the taxes applied to the line items and shipping lines in the checkout",
    "sample_value": "[100.25]"
  }, {
    "name": "shipping_amount",
    "type": "number",
    "description": "Total shipping cost",
    "sample_value": "[6.99]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Checkout Started",
  "use_case": "Used to track the initiation of the checkout process. Supports funnel analysis and checkout optimization.",
  "description": "The checkout_started event logs an instance of a buyer starting the checkout process. This event is available on the checkout page",
  "source": "[Client-Side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-04-14",
  "last_seen": "2025-05-29",
  "count": "53",
  "change": "-1.0",
  "properties": [{
    "name": "shipping_address",
    "type": "object",
    "description": "The shipping address to where the line items will be shipped",
    "sample_value": "{\"address1\": \"123 Main St\", \"address2\": \"Apt 4B\", \"city\": \"New York\", \"company\": \"Acme Corp\", \"country\": \"US\", \"last_name\": \"Doe\", \"latitude\": \"40.7128\", \"longitude\": \"-74.0060\", \"name\": \"John Doe\", \"phone\": \"+1234567890\", \"province\": \"NY\", \"zip\": \"10001\", \"first_name\": \"John\"}",
    "properties": [
        {"name": "address1", "type": "string", "description": "Street address, line 1", "example": "123 Main St"},
        {"name": "address2", "type": "string", "description": "Street address, line 2", "example": "Apt 4B"},
        {"name": "city", "type": "string", "description": "City name", "example": "New York"},
        {"name": "company", "type": "string", "description": "Company name", "example": "Acme Corp"},
        {"name": "country", "type": "string", "description": "Country code (ISO)", "example": "US"},
        {"name": "last_name", "type": "string", "description": "Last name", "example": "Doe"},
        {"name": "latitude", "type": "string", "description": "Latitude", "example": "40.7128"},
        {"name": "longitude", "type": "string", "description": "Longitude", "example": "-74.0060"},
        {"name": "name", "type": "string", "description": "Full name", "example": "John Doe"},
        {"name": "phone", "type": "string", "description": "Phone number", "example": "+1234567890"},
        {"name": "province", "type": "string", "description": "State/Province", "example": "NY"},
        {"name": "zip", "type": "string", "description": "Postal code", "example": "10001"},
        {"name": "first_name", "type": "string", "description": "First name", "example": "John"}
    ]
  }, {
    "name": "products",
    "type": "array",
    "description": "A list of line item objects, each one containing information about an item in the checkout",
    "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
    "properties": [
        {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
        {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
        {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
        {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
        {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
        {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
        {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
        {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
        {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
        {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
        {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
        {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "checkout_attributes",
    "type": "array",
    "description": "A list of attributes accumulated throughout the checkout process",
    "sample_value": "[\"value: /}\", \"value: 123-abc}]\", \"[{name: landing_page\", \"{name: cart_token\"]"
  }, {
    "name": "path_name",
    "type": "string",
    "description": "The path of the URL",
    "sample_value": "[/collections/all]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "order_id",
    "type": "string",
    "description": "The order ID is assigned by Shopify. This is the displayed order ID that shows in the store admin",
    "sample_value": "[5363269]"
  }, {
    "name": "checkout_token",
    "type": "string",
    "description": "A unique identifier for a particular checkout",
    "sample_value": "[57a0a97bf029929066b2a01b5eadd9d1]"
  }, {
    "name": "page_title",
    "type": "string",
    "description": "The title of the page",
    "sample_value": "[Products – gamanalytics]"
  }, {
    "name": "currency",
    "type": "string",
    "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes",
    "sample_value": "[USD]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "cart_subtotal_amount",
    "type": "number",
    "description": "The price at checkout before duties, shipping, and taxes",
    "sample_value": "[100.25]"
  }, {
    "name": "cart_total_amount",
    "type": "number",
    "description": "The sum of all the items in the checkout, including duties, taxes, and discounts",
    "sample_value": "[100.25]"
  }, {
    "name": "tax_amount",
    "type": "number",
    "description": "The sum of all the taxes applied to the line items and shipping lines in the checkout",
    "sample_value": "[100.25]"
  }, {
    "name": "shipping_amount",
    "type": "number",
    "description": "Total shipping cost",
    "sample_value": "[6.99]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Collection Viewed",
  "use_case": "Used to analyze engagement with product collections and merchandising effectiveness.",
  "description": "The collection_viewed event logs an instance where a buyer visited a product collection index page. This event is available on the online store page",
  "source": "[Client-Side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-04-02",
  "last_seen": "2025-05-30",
  "count": "249",
  "change": "0.0",
  "properties": [{
    "name": "products",
    "type": "array",
    "description": "A list of line item objects, each one containing information about an item in the checkout",
    "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
    "properties": [
        {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
        {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
        {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
        {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
        {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
        {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
        {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
        {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
        {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
        {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
        {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
        {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "path_name",
    "type": "string",
    "description": "The path of the URL",
    "sample_value": "[/collections/all]"
  }, {
    "name": "collection_id",
    "type": "string",
    "description": "The ID of the collection",
    "sample_value": "[155050901556]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "page_title",
    "type": "string",
    "description": "The title of the page",
    "sample_value": "[Products – gamanalytics]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "collection_title",
    "type": "string",
    "description": "The title of the collection",
    "sample_value": "[Winter Outfits]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Order Delivered",
  "use_case": "Used to confirm successful delivery of orders. Supports customer satisfaction and delivery analytics.",
  "description": "The order_delivered event is sent when an order is delivered, based on the shipment status of the order.",
  "source": "[Server-side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-05-23",
  "last_seen": "2025-05-23",
  "count": "27",
  "change": "0.0",
  "properties": [{
    "name": "order_tags",
    "type": "array",
    "description": "The tags associated with orders",
    "sample_value": "[\"RAZORPAY\", \"Shopflo]\", \"pg:pay_NX72qSUceyNDRC\", \"[ONLINE\"]"
  }, {
    "name": "billing_address",
    "type": "object",
    "description": "The billing address where the order will be billed to",
    "sample_value": "{\"address1\": \"123 Main St\", \"address2\": \"Apt 4B\", \"city\": \"New York\", \"company\": \"Acme Corp\", \"country\": \"US\", \"last_name\": \"Doe\", \"latitude\": \"40.7128\", \"longitude\": \"-74.0060\", \"name\": \"John Doe\", \"phone\": \"+1234567890\", \"province\": \"NY\", \"zip\": \"10001\", \"first_name\": \"John\"}",
    "properties": [
        {"name": "address1", "type": "string", "description": "Street address, line 1", "example": "123 Main St"},
        {"name": "address2", "type": "string", "description": "Street address, line 2", "example": "Apt 4B"},
        {"name": "city", "type": "string", "description": "City name", "example": "New York"},
        {"name": "company", "type": "string", "description": "Company name", "example": "Acme Corp"},
        {"name": "country", "type": "string", "description": "Country code (ISO)", "example": "US"},
        {"name": "last_name", "type": "string", "description": "Last name", "example": "Doe"},
        {"name": "latitude", "type": "string", "description": "Latitude", "example": "40.7128"},
        {"name": "longitude", "type": "string", "description": "Longitude", "example": "-74.0060"},
        {"name": "name", "type": "string", "description": "Full name", "example": "John Doe"},
        {"name": "phone", "type": "string", "description": "Phone number", "example": "+1234567890"},
        {"name": "province", "type": "string", "description": "State/Province", "example": "NY"},
        {"name": "zip", "type": "string", "description": "Postal code", "example": "10001"},
        {"name": "first_name", "type": "string", "description": "First name", "example": "John"}
    ]
  }, {
    "name": "shipping_address",
    "type": "object",
    "description": "The shipping address to where the line items will be shipped",
    "sample_value": "{\"address1\": \"123 Main St\", \"address2\": \"Apt 4B\", \"city\": \"New York\", \"company\": \"Acme Corp\", \"country\": \"US\", \"last_name\": \"Doe\", \"latitude\": \"40.7128\", \"longitude\": \"-74.0060\", \"name\": \"John Doe\", \"phone\": \"+1234567890\", \"province\": \"NY\", \"zip\": \"10001\", \"first_name\": \"John\"}",
    "properties": [
        {"name": "address1", "type": "string", "description": "Street address, line 1", "example": "123 Main St"},
        {"name": "address2", "type": "string", "description": "Street address, line 2", "example": "Apt 4B"},
        {"name": "city", "type": "string", "description": "City name", "example": "New York"},
        {"name": "company", "type": "string", "description": "Company name", "example": "Acme Corp"},
        {"name": "country", "type": "string", "description": "Country code (ISO)", "example": "US"},
        {"name": "last_name", "type": "string", "description": "Last name", "example": "Doe"},
        {"name": "latitude", "type": "string", "description": "Latitude", "example": "40.7128"},
        {"name": "longitude", "type": "string", "description": "Longitude", "example": "-74.0060"},
        {"name": "name", "type": "string", "description": "Full name", "example": "John Doe"},
        {"name": "phone", "type": "string", "description": "Phone number", "example": "+1234567890"},
        {"name": "province", "type": "string", "description": "State/Province", "example": "NY"},
        {"name": "zip", "type": "string", "description": "Postal code", "example": "10001"},
        {"name": "first_name", "type": "string", "description": "First name", "example": "John"}
    ]
  }, {
    "name": "discount",
    "type": "array",
    "description": "All of the discount applications for the order and its line items",
    "sample_value": "[\"code: LL-4J2TJS6S\", \"type: fixed_amount}]\", \"[{amount: 26.87\"]"
  }, {
    "name": "products",
    "type": "array",
    "description": "A list of line item objects, each one containing information about an item in the checkout",
    "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
    "properties": [
        {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
        {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
        {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
        {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
        {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
        {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
        {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
        {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
        {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
        {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
        {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
        {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "payment_gateway",
    "type": "array",
    "description": "What user use to pay for the order",
    "sample_value": "[\"[Cash on Delivery (COD)]\"]"
  }, {
    "name": "note",
    "type": "string",
    "description": "Order Note",
    "sample_value": "[** Authority to Leave **]"
  }, {
    "name": "vendo_tracking_version",
    "type": "string",
    "description": "Vendo tracking version",
    "sample_value": "[1.2.1]"
  }, {
    "name": "delivery_date",
    "type": "string",
    "description": "The delivery date.",
    "sample_value": "[2023 8:19 PM, Aug 31, Thu]"
  }, {
    "name": "app_id",
    "type": "string",
    "description": "The ID of the app that created the order",
    "sample_value": "[4341497857]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "order_id",
    "type": "string",
    "description": "The order ID is assigned by Shopify. This is the displayed order ID that shows in the store admin",
    "sample_value": "[5363269]"
  }, {
    "name": "shopify_order_id",
    "type": "string",
    "description": "The Shopify Order ID is a global order ID set by Shopify",
    "sample_value": "[5363269534010]"
  }, {
    "name": "currency",
    "type": "string",
    "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes",
    "sample_value": "[AUD, GBP, USD]"
  }, {
    "name": "test",
    "type": "boolean",
    "description": "Shows whether this order is a test order or not",
    "sample_value": "[False]"
  }, {
    "name": "fulfillment_name",
    "type": "string",
    "description": "The name of the fulfillment service.",
    "sample_value": "[GP2534115-F1]"
  }, {
    "name": "client_details_user_agent",
    "type": "string",
    "description": "The user_agent object consists of a User-agent directive, and a value of the name of the user-agent",
    "sample_value": "[Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36]"
  }, {
    "name": "$import",
    "type": "boolean",
    "description": "To determine if this a server side event or not",
    "sample_value": "[True]"
  }, {
    "name": "confirmed",
    "type": "boolean",
    "description": "Status or the orders if it was confirmed or not",
    "sample_value": "[True]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "source_name",
    "type": "string",
    "description": "Name of the app that the data is syncing from",
    "sample_value": "[app, web]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "fulfillment_status",
    "type": "string",
    "description": "The ID of the fulfillment service.",
    "sample_value": "[cancelled, error, failure, open, pending, success]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "order_status_url",
    "type": "string",
    "description": "The URL of the page when order was confirmed",
    "sample_value": "[https://www.my-url.com/orders/123]"
  }, {
    "name": "fulfillment_service",
    "type": "string",
    "description": "The ID of the fulfillment service.",
    "sample_value": "[manual]"
  }, {
    "name": "processing_method",
    "type": "string",
    "description": "Describes which processing method was used to process the order",
    "sample_value": "[manual]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "payment_status",
    "type": "string",
    "description": "The payment status of the order at the time it was placed. These should be mostly paid or pending but could be other values for historical order syncs",
    "sample_value": "[paid, partially_paid, partially_refunded, pending, refunded, voided]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "email",
    "type": "string",
    "description": "The email attached to this checkout",
    "sample_value": "[test.user@email.com]"
  }, {
    "name": "shipping_amount",
    "type": "number",
    "description": "Total shipping cost",
    "sample_value": "[10.25]"
  }, {
    "name": "cart_subtotal_amount",
    "type": "number",
    "description": "The price at checkout before duties, shipping, and taxes",
    "sample_value": "[100.25]"
  }, {
    "name": "cart_total_amount",
    "type": "number",
    "description": "The sum of all the items in the checkout, including duties, taxes, and discounts",
    "sample_value": "[100.25]"
  }, {
    "name": "tax_amount",
    "type": "number",
    "description": "Tax Amount",
    "sample_value": "[100.25]"
  }, {
    "name": "total_discounts",
    "type": "number",
    "description": "The total amount of all discounts applied to the order",
    "sample_value": "[100.25]"
  }, {
    "name": "delivery_speed",
    "type": "number",
    "description": "The number of days it takes for a business to deliver a customers order from the moment it is placed.",
    "sample_value": "[2]"
  }, {
    "name": "delivery_speed_weekdays",
    "type": "number",
    "description": "The number of business days it takes for a business to deliver a customers order from the moment it is placed. It is counted in days and excludes weekends",
    "sample_value": "[2]"
  }, {
    "name": "fulfillment_speed",
    "type": "number",
    "description": "The number of days it takes for a business to process and deliver a customers order from the moment it is placed.",
    "sample_value": "[2]"
  }, {
    "name": "fulfillment_speed_weekdays",
    "type": "number",
    "description": "The number of business days it takes for a business to process and deliver a customers order from the moment it is placed. It is counted in days and excludes weekends",
    "sample_value": "[2]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Order Fulfilled",
  "use_case": "Used to track when an order is shipped. Supports fulfillment analytics and customer notifications.",
  "description": "The order_fulfilled event logs when the shop owner has processed and shipped the order",
  "source": "[Server-side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-03-17",
  "last_seen": "2025-05-27",
  "count": "38",
  "change": "0.0",
  "properties": [{
    "name": "products",
    "type": "array",
    "description": "A list of line item objects, each one containing information about an item in the checkout",
    "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
    "properties": [
        {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
        {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
        {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
        {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
        {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
        {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
        {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
        {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
        {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
        {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
        {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
        {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "vendo_tracking_version",
    "type": "string",
    "description": "Vendo tracking version",
    "sample_value": "[1.2.1]"
  }, {
    "name": "tracking_number",
    "type": "string",
    "description": "Tracking number of the shipping",
    "sample_value": "[123-abc]"
  }, {
    "name": "fulfillment_id",
    "type": "string",
    "description": "The order_payment_confirmed event is sent when the payment for the order is verified. Use this metric for revenue calculations",
    "sample_value": "[4751610282298]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "order_id",
    "type": "string",
    "description": "The order ID is assigned by Shopify. This is the displayed order ID that shows in the store admin",
    "sample_value": "[5363269]"
  }, {
    "name": "shopify_order_id",
    "type": "string",
    "description": "The Shopify Order ID is a global order ID set by Shopify",
    "sample_value": "[5363269534010]"
  }, {
    "name": "fulfillment_name",
    "type": "string",
    "description": "The name of the fulfillment service.",
    "sample_value": "[GP2534115-F1]"
  }, {
    "name": "$ignore_time",
    "type": "boolean",
    "description": "Ignore Time",
    "sample_value": "[True]"
  }, {
    "name": "$import",
    "type": "boolean",
    "description": "To determine if this a server side event or not",
    "sample_value": "[True]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "email",
    "type": "string",
    "description": "The email attached to this checkout",
    "sample_value": "[abc@def.com]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "fulfillment_status",
    "type": "string",
    "description": "The ID of the fulfillment service.",
    "sample_value": "[cancelled, error, failure, open, pending, success]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "fulfillment_service",
    "type": "string",
    "description": "The ID of the fulfillment service.",
    "sample_value": "[manual]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "fulfillment_number",
    "type": "number",
    "description": "The fulfilment number, if an order has 2 types of product with different shipping there will be 2 fulfillment number",
    "sample_value": "[2]"
  }, {
    "name": "fulfillment_speed",
    "type": "number",
    "description": "The nnumber of days it takes for a business to process and deliver a customers order from the moment it is placed.",
    "sample_value": "[2]"
  }, {
    "name": "fulfillment_speed_weekdays",
    "type": "number",
    "description": "The number of business days it takes for a business to process and deliver a customers order from the moment it is placed. It is counted in days and excludes weekends",
    "sample_value": "[2]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Order Partially Refunded",
  "use_case": "Used to track partial refunds for orders. Supports revenue reconciliation and customer support.",
  "description": "The order_partially_refunded event logs when the order is edited to only refund part of the order",
  "source": "[Server-side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-10-21",
  "last_seen": "2025-04-01",
  "count": "0",
  "change": None,
  "properties": [{
    "name": "products",
    "type": "array",
    "description": "A list of line item objects, each one containing information about an item in the checkout",
    "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
    "properties": [
        {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
        {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
        {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
        {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
        {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
        {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
        {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
        {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
        {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
        {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
        {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
        {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "payment_getaway_names",
    "type": "array",
    "description": "The name of payment gateway used",
    "sample_value": "[\"[shopflo]\"]"
  }, {
    "name": "vendo_tracking_version",
    "type": "string",
    "description": "Vendo tracking version",
    "sample_value": "[1.2.1]"
  }, {
    "name": "refund_amount",
    "type": "string",
    "description": "The amount refunded",
    "sample_value": "[20.5]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "order_id",
    "type": "string",
    "description": "The order ID is assigned by Shopify. This is the displayed order ID that shows in the store admin",
    "sample_value": "[5363269]"
  }, {
    "name": "shopify_order_id",
    "type": "string",
    "description": "The Shopify Order ID is a global order ID set by Shopify",
    "sample_value": "[5363269534010]"
  }, {
    "name": "$import",
    "type": "boolean",
    "description": "To determine if this a server side event or not",
    "sample_value": "[True]"
  }, {
    "name": "currency",
    "type": "string",
    "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes",
    "sample_value": "[USD]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "payment_gateway",
    "type": "string",
    "description": "What user use to pay for the order",
    "sample_value": "[manual]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "confirmed",
    "type": "boolean",
    "description": "Status or the orders if it was confirmed or not",
    "sample_value": "[true]"
  }, {
    "name": "cart_subtotal_amount",
    "type": "number",
    "description": "The price at checkout before duties, shipping, and taxes",
    "sample_value": "[100.25]"
  }, {
    "name": "cart_total_amount",
    "type": "number",
    "description": "The sum of all the items in the checkout, including duties, taxes, and discounts",
    "sample_value": "[100.25]"
  }, {
    "name": "tax_amount",
    "type": "number",
    "description": "The sum of all the taxes applied to the line items and shipping lines in the checkout",
    "sample_value": "[100.25]"
  }, {
    "name": "total_discounts",
    "type": "number",
    "description": "The total amount of all discounts applied to the order",
    "sample_value": "[100.25]"
  }, {
    "name": "shipping_amount",
    "type": "number",
    "description": "Total shipping cost",
    "sample_value": "[6.99]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Order Received",
  "use_case": "Used for order analytics, gross profit calculations, revenue reporting, and triggering fulfillment or customer engagement workflows.",
  "description": "Fires when a new order is created in Shopify, regardless of payment status. Includes all order details, customer info, and line items. Use the 'financial_status' property to determine if the order is paid.",
  "source": "[Server-side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-03-08",
  "last_seen": "2025-05-26",
  "count": "31",
  "change": "0.0",
  "properties": [{
    "name": "order_tags",
    "type": "array",
    "description": "Tags assigned to the order in Shopify, such as payment method, channel, or custom tags.",
    "sample_value": "[\"RAZORPAY\", \"Shopflo\", \"pg:pay_NX72qSUceyNDRC\", \"ONLINE\"]"
  }, {
    "name": "billing_address",
    "type": "object",
    "description": "The billing address where the order will be billed to.",
    "sample_value": "{\"address1\": \"123 Main St\", \"address2\": \"Apt 4B\", \"city\": \"New York\", \"company\": \"Acme Corp\", \"country\": \"US\", \"last_name\": \"Doe\", \"latitude\": \"40.7128\", \"longitude\": \"-74.0060\", \"name\": \"John Doe\", \"phone\": \"+1234567890\", \"province\": \"NY\", \"zip\": \"10001\", \"first_name\": \"John\"}",
    "properties": [
      {"name": "address1", "type": "string", "description": "Street address, line 1", "example": "123 Main St"},
      {"name": "address2", "type": "string", "description": "Street address, line 2", "example": "Apt 4B"},
      {"name": "city", "type": "string", "description": "City name", "example": "New York"},
      {"name": "company", "type": "string", "description": "Company name", "example": "Acme Corp"},
      {"name": "country", "type": "string", "description": "Country code (ISO)", "example": "US"},
      {"name": "last_name", "type": "string", "description": "Last name", "example": "Doe"},
      {"name": "latitude", "type": "string", "description": "Latitude", "example": "40.7128"},
      {"name": "longitude", "type": "string", "description": "Longitude", "example": "-74.0060"},
      {"name": "name", "type": "string", "description": "Full name", "example": "John Doe"},
      {"name": "phone", "type": "string", "description": "Phone number", "example": "+1234567890"},
      {"name": "province", "type": "string", "description": "State/Province", "example": "NY"},
      {"name": "zip", "type": "string", "description": "Postal code", "example": "10001"},
      {"name": "first_name", "type": "string", "description": "First name", "example": "John"}
    ]
  }, {
    "name": "shipping_address",
    "type": "object",
    "description": "The shipping address to where the line items will be shipped.",
    "sample_value": "{\"address1\": \"123 Main St\", \"address2\": \"Apt 4B\", \"city\": \"New York\", \"company\": \"Acme Corp\", \"country\": \"US\", \"last_name\": \"Doe\", \"latitude\": \"40.7128\", \"longitude\": \"-74.0060\", \"name\": \"John Doe\", \"phone\": \"+1234567890\", \"province\": \"NY\", \"zip\": \"10001\", \"first_name\": \"John\"}",
    "properties": [
      {"name": "address1", "type": "string", "description": "Street address, line 1", "example": "123 Main St"},
      {"name": "address2", "type": "string", "description": "Street address, line 2", "example": "Apt 4B"},
      {"name": "city", "type": "string", "description": "City name", "example": "New York"},
      {"name": "company", "type": "string", "description": "Company name", "example": "Acme Corp"},
      {"name": "country", "type": "string", "description": "Country code (ISO)", "example": "US"},
      {"name": "last_name", "type": "string", "description": "Last name", "example": "Doe"},
      {"name": "latitude", "type": "string", "description": "Latitude", "example": "40.7128"},
      {"name": "longitude", "type": "string", "description": "Longitude", "example": "-74.0060"},
      {"name": "name", "type": "string", "description": "Full name", "example": "John Doe"},
      {"name": "phone", "type": "string", "description": "Phone number", "example": "+1234567890"},
      {"name": "province", "type": "string", "description": "State/Province", "example": "NY"},
      {"name": "zip", "type": "string", "description": "Postal code", "example": "10001"},
      {"name": "first_name", "type": "string", "description": "First name", "example": "John"}
    ]
  }, {
    "name": "products",
    "type": "array",
    "description": "List of products (line items) included in the order, with details for each item.",
    "sample_value": "[{\"id\":9882896204064,\"price\":50.15,\"product_type\":\"Red Light Panel\",\"quantity\":1,\"sku\":\"AB123\",\"title\":\"Red Light Therapy Panel - Pro60 (New)\",\"variant_id\":50088217215264,\"variant_price\":50.15,\"variant_sku\":\"AB123-2\",\"variant_title\":\"Red Light Therapy Panel - Pro60 (New) - Black\",\"variant_unit_cost\":30.00,\"vendor\":\"Piri Red\"}]",
    "properties": [
      {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
      {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
      {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
      {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
      {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
      {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
      {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
      {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
      {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
      {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
      {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
      {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "custom_order_attributes",
    "type": "array",
    "description": "A list of details that have been added to the order.",
    "sample_value": "[\"value: google}\", \"value: google}\", \"value: new}]\", \"[{key: utm_source\", \"{key: customer_type\", \"{key: utm_campaign\"]"
  }, {
    "name": "payment_gateway",
    "type": "array",
    "description": "What user use to pay for the order",
    "sample_value": "[\"[Cash on Delivery (COD)]\"]"
  }, {
    "name": "note",
    "type": "string",
    "description": "Order note",
    "sample_value": "[** Authority to Leave **]"
  }, {
    "name": "landing_page",
    "type": "string",
    "description": "The first page a user visits when arriving on a website or app",
    "sample_value": "[/products/shorts?utm_source\u003dgoogle\u0026utm_medium\u003dcpc]"
  }, {
    "name": "vendo_tracking_version",
    "type": "string",
    "description": "Vendo tracking version",
    "sample_value": "[1.2.1]"
  }, {
    "name": "app_id",
    "type": "string",
    "description": "The ID of the app that created the order",
    "sample_value": "[4341497857]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "order_id",
    "type": "string",
    "description": "The order ID is assigned by Shopify. This is the displayed order ID that shows in the store admin",
    "sample_value": "[5363269]"
  }, {
    "name": "shopify_order_id",
    "type": "string",
    "description": "The Shopify Order ID is a global order ID set by Shopify",
    "sample_value": "[5363269534010]"
  }, {
    "name": "currency",
    "type": "string",
    "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes",
    "sample_value": "[AUD, GBP, USD]"
  }, {
    "name": "test",
    "type": "boolean",
    "description": "Shows whether this order is a test order or not",
    "sample_value": "[False]"
  }, {
    "name": "$import",
    "type": "boolean",
    "description": "To determine if this a server side event or not",
    "sample_value": "[True]"
  }, {
    "name": "confirmed",
    "type": "boolean",
    "description": "Status or the orders if it was confirmed or not",
    "sample_value": "[True]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "discount",
    "type": "array",
    "description": "Discount codes for the order",
    "sample_value": "[[]]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "order_status_url",
    "type": "string",
    "description": "The URL of the page when order was confirmed",
    "sample_value": "[https://www.my-url.com/orders/123]"
  }, {
    "name": "processing_method",
    "type": "string",
    "description": "Describes which processing method was used to process the order",
    "sample_value": "[manual]"
  }, {
    "name": "source_name",
    "type": "string",
    "description": "The name of the source where the order originated",
    "sample_value": "[mobile_app, pos, shopify_draft_order, web]"
  }, {
    "name": "app_name",
    "type": "string",
    "description": "The name of the app that created the order",
    "sample_value": "[mobile_app, tiktok, website]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "payment_status",
    "type": "string",
    "description": "The payment status of the order at the time it was placed. These should be mostly paid or pending but could be other values for historical order syncs",
    "sample_value": "[paid, partially_paid, partially_refunded, pending, refunded, voided]"
  }, {
    "name": "financial_status",
    "type": "string",
    "description": "The payment state of an order",
    "sample_value": "[paid, partially_refunded, refunded]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "email",
    "type": "string",
    "description": "The email attached to this checkout",
    "sample_value": "[test.user@email.com]"
  }, {
    "name": "shipping_amount",
    "type": "number",
    "description": "Total shipping cost",
    "sample_value": "[10.25]"
  }, {
    "name": "cart_subtotal_amount",
    "type": "number",
    "description": "The price at checkout before duties, shipping, and taxes",
    "sample_value": "[100.25]"
  }, {
    "name": "cart_total_amount",
    "type": "number",
    "description": "The sum of all the items in the checkout, including duties, taxes, and discounts",
    "sample_value": "[100.25]"
  }, {
    "name": "tax_amount",
    "type": "number",
    "description": "Tax Amount",
    "sample_value": "[100.25]"
  }, {
    "name": "total_discounts",
    "type": "number",
    "description": "The total amount of all discounts applied to the order",
    "sample_value": "[100.25]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Order Refunded",
  "description": "The order_refunded event logs when the order was fully refunded",
  "source": "[Server-side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-04-22",
  "last_seen": "2024-04-22",
  "count": "0",
  "change": None,
  "properties": [{
    "name": "products",
    "type": "array",
    "description": "A list of line item objects, each one containing information about an item in the checkout",
    "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
    "properties": [
        {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
        {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
        {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
        {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
        {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
        {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
        {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
        {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
        {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
        {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
        {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
        {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "payment_gateway",
    "type": "array",
    "description": "The list of payment gateways used for the order",
    "sample_value": "[\"[shopflo]\"]"
  }, {
    "name": "vendo_tracking_version",
    "type": "string",
    "description": "Vendo tracking version",
    "sample_value": "[1.2.1]"
  }, {
    "name": "refund_amount",
    "type": "string",
    "description": "The amount refunded",
    "sample_value": "[20.5]"
  }, {
    "name": "cancelled_at",
    "type": "string",
    "description": "A timestamp for when the order was cancelled",
    "sample_value": "[2023 8:19 PM, Aug 31, Thu]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "order_id",
    "type": "string",
    "description": "The order ID is assigned by Shopify. This is the displayed order ID that shows in the store admin",
    "sample_value": "[5363269]"
  }, {
    "name": "shopify_order_id",
    "type": "string",
    "description": "The Shopify Order ID is a global order ID set by Shopify",
    "sample_value": "[5363269534010]"
  }, {
    "name": "customer_id",
    "type": "string",
    "description": "Customer ID",
    "sample_value": "[6304574505006]"
  }, {
    "name": "note",
    "type": "string",
    "description": "A note from the customer attached to the order",
    "sample_value": "[Please handle with care]"
  }, {
    "name": "cancel_reason",
    "type": "string",
    "description": "The reason of cancellation",
    "sample_value": "[Product not right]"
  }, {
    "name": "$import",
    "type": "boolean",
    "description": "To determine if this a server side event or not",
    "sample_value": "[True]"
  }, {
    "name": "currency",
    "type": "string",
    "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes",
    "sample_value": "[USD]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "confirmed",
    "type": "boolean",
    "description": "Status or the orders if it was confirmed or not",
    "sample_value": "[true]"
  }, {
    "name": "cart_subtotal_amount",
    "type": "number",
    "description": "The price at checkout before duties, shipping, and taxes",
    "sample_value": "[100.25]"
  }, {
    "name": "cart_total_amount",
    "type": "number",
    "description": "The sum of all the items in the checkout, including duties, taxes, and discounts",
    "sample_value": "[100.25]"
  }, {
    "name": "tax_amount",
    "type": "number",
    "description": "The sum of all the taxes applied to the line items and shipping lines in the checkout",
    "sample_value": "[100.25]"
  }, {
    "name": "total_discounts",
    "type": "number",
    "description": "The total amount of all discounts applied to the order",
    "sample_value": "[100.25]"
  }, {
    "name": "shipping_amount",
    "type": "number",
    "description": "Total shipping cost",
    "sample_value": "[6.99]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Page Viewed",
  "use_case": "Used to analyze page engagement and user navigation. Supports content optimization and funnel analysis.",
  "description": "The page_viewed event logs an instance where a buyer visited a page. This event is available on the online store, checkout, and order status pages",
  "source": "[Client-Side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-04-02",
  "last_seen": "2025-05-30",
  "count": "2728",
  "change": "0.0",
  "properties": [{
    "name": "path_name",
    "type": "string",
    "description": "The path of the URL",
    "sample_value": "[/collections/all]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "page_title",
    "type": "string",
    "description": "The title of the page",
    "sample_value": "[Products – gamanalytics]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Payment Info Submitted",
  "use_case": "Used to track payment information submission during checkout. Supports payment analytics and fraud prevention.",
  "description": "The payment_info_submitted event logs an instance of a buyer submitting their payment information. This event is available on the checkout page",
  "source": "[Client-Side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-05-23",
  "last_seen": "2025-05-21",
  "count": "57",
  "change": "0.0",
  "properties": [{
    "name": "shipping_address",
    "type": "object",
    "description": "The shipping address to where the line items will be shipped",
    "sample_value": "{\"address1\": \"123 Main St\", \"address2\": \"Apt 4B\", \"city\": \"New York\", \"company\": \"Acme Corp\", \"country\": \"US\", \"last_name\": \"Doe\", \"latitude\": \"40.7128\", \"longitude\": \"-74.0060\", \"name\": \"John Doe\", \"phone\": \"+1234567890\", \"province\": \"NY\", \"zip\": \"10001\", \"first_name\": \"John\"}",
    "properties": [
        {"name": "address1", "type": "string", "description": "Street address, line 1", "example": "123 Main St"},
        {"name": "address2", "type": "string", "description": "Street address, line 2", "example": "Apt 4B"},
        {"name": "city", "type": "string", "description": "City name", "example": "New York"},
        {"name": "company", "type": "string", "description": "Company name", "example": "Acme Corp"},
        {"name": "country", "type": "string", "description": "Country code (ISO)", "example": "US"},
        {"name": "last_name", "type": "string", "description": "Last name", "example": "Doe"},
        {"name": "latitude", "type": "string", "description": "Latitude", "example": "40.7128"},
        {"name": "longitude", "type": "string", "description": "Longitude", "example": "-74.0060"},
        {"name": "name", "type": "string", "description": "Full name", "example": "John Doe"},
        {"name": "phone", "type": "string", "description": "Phone number", "example": "+1234567890"},
        {"name": "province", "type": "string", "description": "State/Province", "example": "NY"},
        {"name": "zip", "type": "string", "description": "Postal code", "example": "10001"},
        {"name": "first_name", "type": "string", "description": "First name", "example": "John"}
    ]
  }, {
    "name": "products",
    "type": "array",
    "description": "A list of line item objects, each one containing information about an item in the checkout",
    "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
    "properties": [
        {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
        {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
        {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
        {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
        {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
        {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
        {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
        {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
        {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
        {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
        {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
        {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "checkout_attributes",
    "type": "array",
    "description": "A list of attributes accumulated throughout the checkout process",
    "sample_value": "[\"value: /}\", \"value: 123-abc}]\", \"[{name: landing_page\", \"{name: cart_token\"]"
  }, {
    "name": "payment_gateway",
    "type": "array",
    "description": "What user use to pay for the order",
    "sample_value": "[\"[shopflo]\"]"
  }, {
    "name": "path_name",
    "type": "string",
    "description": "The path of the URL",
    "sample_value": "[/collections/all]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "order_id",
    "type": "string",
    "description": "The order ID is assigned by Shopify. This is the displayed order ID that shows in the store admin",
    "sample_value": "[5363269]"
  }, {
    "name": "checkout_token",
    "type": "string",
    "description": "A unique identifier for a particular checkout",
    "sample_value": "[57a0a97bf029929066b2a01b5eadd9d1]"
  }, {
    "name": "page_title",
    "type": "string",
    "description": "The title of the page",
    "sample_value": "[Products – gamanalytics]"
  }, {
    "name": "currency",
    "type": "string",
    "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes",
    "sample_value": "[USD]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "processing_method",
    "type": "string",
    "description": "Describes which processing method was used to process the order",
    "sample_value": "[manual]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "email",
    "type": "string",
    "description": "The email attached to this checkout",
    "sample_value": "[test.user@email.com]"
  }, {
    "name": "cart_subtotal_amount",
    "type": "number",
    "description": "The price at checkout before duties, shipping, and taxes",
    "sample_value": "[100.25]"
  }, {
    "name": "cart_total_amount",
    "type": "number",
    "description": "The sum of all the items in the checkout, including duties, taxes, and discounts",
    "sample_value": "[100.25]"
  }, {
    "name": "tax_amount",
    "type": "number",
    "description": "The sum of all the taxes applied to the line items and shipping lines in the checkout",
    "sample_value": "[100.25]"
  }, {
    "name": "shipping_amount",
    "type": "number",
    "description": "Total shipping cost",
    "sample_value": "[6.99]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Product Added To Cart",
  "use_case": "Used to track when a product is added to the cart. Supports merchandising and conversion analysis.",
  "description": "The product_added_to_cart event logs an instance where a buyer added a product to the cart. This event is available on the product page",
  "source": "[Client-Side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-04-14",
  "last_seen": "2025-05-29",
  "count": "62",
  "change": "-1.0",
  "properties": [{
    "name": "products",
    "type": "array",
    "description": "A list of line item objects, each one containing information about an item in the checkout",
    "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
    "properties": [
        {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
        {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
        {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
        {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
        {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
        {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
        {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
        {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
        {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
        {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
        {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
        {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "path_name",
    "type": "string",
    "description": "The path of the URL",
    "sample_value": "[/collections/all]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "page_title",
    "type": "string",
    "description": "The title of the page",
    "sample_value": "[Products – gamanalytics]"
  }, {
    "name": "currency",
    "type": "string",
    "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes",
    "sample_value": "[USD]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "amount",
    "type": "number",
    "description": "Used for the monetary amount of the object",
    "sample_value": "[100]"
  }, {
    "name": "quantity",
    "type": "number",
    "description": "Quantity added to cart",
    "sample_value": "[1]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Product Removed From Cart",
  "use_case": "Used to track when a product is removed from the cart. Supports cart abandonment and product interest analysis.",
  "description": "The product_removed_from_cart event logs an instance where a customer removes a product from their cart",
  "source": "[Client-Side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-04-02",
  "last_seen": "2025-05-05",
  "count": "0",
  "change": "-1.0",
  "properties": [{
    "name": "products",
    "type": "array",
    "description": "A list of line item objects, each one containing information about an item in the checkout",
    "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
    "properties": [
        {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
        {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
        {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
        {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
        {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
        {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
        {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
        {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
        {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
        {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
        {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
        {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "path_name",
    "type": "string",
    "description": "The path of the URL",
    "sample_value": "[/collections/all]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "page_title",
    "type": "string",
    "description": "The title of the page",
    "sample_value": "[Products – gamanalytics]"
  }, {
    "name": "currency",
    "type": "string",
    "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes",
    "sample_value": "[USD]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "amount",
    "type": "number",
    "description": "Used for the monetary amount of the object",
    "sample_value": "[100]"
  }, {
    "name": "quantity",
    "type": "number",
    "description": "Quantity added to cart",
    "sample_value": "[1]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Product Viewed",
  "use_case": "Used to analyze product interest and engagement. Supports merchandising and recommendation systems.",
  "description": "The product_viewed event logs an instance where a buyer visited a product details page. This event is available on the product page",
  "source": "[Client-Side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-04-02",
  "last_seen": "2025-05-30",
  "count": "1669",
  "change": "0.0",
  "properties": [{
    "name": "products",
    "type": "array",
    "description": "A list of line item objects, each one containing information about an item in the checkout",
    "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
    "properties": [
        {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
        {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
        {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
        {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
        {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
        {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
        {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
        {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
        {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
        {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
        {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
        {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "path_name",
    "type": "string",
    "description": "The path of the URL",
    "sample_value": "[/collections/all]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "page_title",
    "type": "string",
    "description": "The title of the page",
    "sample_value": "[Products – gamanalytics]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Products Purchased",
  "use_case": "Used to analyze individual product sales and order composition. Supports inventory and revenue analytics.",
  "description": "The products_purchased event is sent for each line item in a Shopify order. This event provides detailed information about individual products within an order, including variant details, pricing, and product metadata. Each line item in an order generates a separate event, allowing for granular tracking of product purchases. Like order_received, these events are created when an order is placed and the financial status should be checked to confirm payment.",
  "source": "[Server-side, Vendo]",
  "status": "Healthy",
  "first_seen": "2025-02-18",
  "last_seen": "2025-04-18",
  "count": "0",
  "change": "-1.0",
  "properties": [{
    "name": "order_tags",
    "type": "array",
    "description": "The tags associated with orders",
    "sample_value": "[\"RAZORPAY\", \"Shopflo]\", \"pg:pay_NX72qSUceyNDRC\", \"[ONLINE\"]"
  }, {
    "name": "products",
    "type": "array",
    "description": "A list of line item objects, each one containing information about an item in the checkout",
    "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
    "properties": [
        {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
        {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
        {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
        {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
        {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
        {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
        {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
        {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
        {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
        {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
        {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
        {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "custom_order_attributes",
    "type": "array",
    "description": "A list of details that have been added to the order.",
    "sample_value": "[\"value: google}\", \"value: google}\", \"value: new}]\", \"[{key: utm_source\", \"{key: customer_type\", \"{key: utm_campaign\"]"
  }, {
    "name": "payment_gateway",
    "type": "array",
    "description": "What user use to pay for the order",
    "sample_value": "[\"[Cash on Delivery (COD)]\"]"
  }, {
    "name": "landing_page",
    "type": "string",
    "description": "The first page a user visits when arriving on a website or app",
    "sample_value": "[/products/shorts?utm_source\u003dgoogle\u0026utm_medium\u003dcpc]"
  }, {
    "name": "app_id",
    "type": "string",
    "description": "The ID of the app that created the order",
    "sample_value": "[4341497857]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "order_id",
    "type": "string",
    "description": "The order ID is assigned by Shopify. This is the displayed order ID that shows in the store admin",
    "sample_value": "[5363269]"
  }, {
    "name": "shopify_order_id",
    "type": "string",
    "description": "The Shopify Order ID is a global order ID set by Shopify",
    "sample_value": "[5363269534010]"
  }, {
    "name": "currency",
    "type": "string",
    "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes",
    "sample_value": "[AUD, GBP, USD]"
  }, {
    "name": "test",
    "type": "boolean",
    "description": "Shows whether this order is a test order or not",
    "sample_value": "[False]"
  }, {
    "name": "$import",
    "type": "boolean",
    "description": "To determine if this a server side event or not",
    "sample_value": "[True]"
  }, {
    "name": "confirmed",
    "type": "boolean",
    "description": "Status or the orders if it was confirmed or not",
    "sample_value": "[True]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "discount",
    "type": "array",
    "description": "Discount codes for the order",
    "sample_value": "[[]]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "order_status_url",
    "type": "string",
    "description": "The URL of the page when order was confirmed",
    "sample_value": "[https://www.my-url.com/orders/123]"
  }, {
    "name": "processing_method",
    "type": "string",
    "description": "Describes which processing method was used to process the order",
    "sample_value": "[manual]"
  }, {
    "name": "app_name",
    "type": "string",
    "description": "The name of the app that created the order",
    "sample_value": "[mobile_app, tiktok, website]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "financial_status",
    "type": "string",
    "description": "The payment state of an order",
    "sample_value": "[paid, partially_refunded, refunded]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "email",
    "type": "string",
    "description": "The email attached to this checkout",
    "sample_value": "[test.user@email.com]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}, {
  "event_name": "Search Submitted",
  "use_case": "Used to analyze search behavior and optimize product discovery.",
  "description": "The search_submitted event logs an instance where a buyer performed a search on the storefront. This event is available on the online store page",
  "source": "[Client-Side, Vendo]",
  "status": "Healthy",
  "first_seen": "2024-04-16",
  "last_seen": "2025-05-30",
  "count": "31",
  "change": "1.0",
  "properties": [{
    "name": "products",
    "type": "array",
    "description": "A list of line item objects, each one containing information about an item in the checkout",
    "sample_value": "[\"price: 50.15}]\", \"sku: 123-abc\", \"title: product title\", \"[{product_id: 1234\"]",
    "properties": [
        {"name": "id", "type": "INTEGER", "example": "9882896204064", "description": "Unique product ID"},
        {"name": "price", "type": "FLOAT", "example": "407.54", "description": "Product price at the time of event"},
        {"name": "product_type", "type": "STRING", "example": "Red Light Panel", "description": "Type/category of the product"},
        {"name": "quantity", "type": "INTEGER", "example": "1", "description": "Quantity of this product in the event"},
        {"name": "sku", "type": "STRING", "example": "AB123", "description": "Product SKU (Stock Keeping Unit)"},
        {"name": "title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New)", "description": "Product title/name"},
        {"name": "variant_id", "type": "INTEGER", "example": "50088217215264", "description": "Unique ID for the product variant"},
        {"name": "variant_price", "type": "FLOAT", "example": "399", "description": "Price of the specific variant"},
        {"name": "variant_sku", "type": "STRING", "example": "AB123-2", "description": "SKU for the product variant"},
        {"name": "variant_title", "type": "STRING", "example": "Red Light Therapy Panel - Pro60 (New) - Black", "description": "Title/name of the product variant"},
        {"name": "variant_unit_cost", "type": "FLOAT", "example": "250", "description": "Unit cost of the variant (COGS)"},
        {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"}
    ]
  }, {
    "name": "path_name",
    "type": "string",
    "description": "The path of the URL",
    "sample_value": "[/collections/all]"
  }, {
    "name": "$insert_id",
    "type": "string",
    "description": "A unique identifier for the event, used for deduplication. The client-side events values are set by Shopify",
    "sample_value": "[49b71cd2-295b-476a-a345-0eb50bd13b57]"
  }, {
    "name": "page_title",
    "type": "string",
    "description": "The title of the page",
    "sample_value": "[Products – gamanalytics]"
  }, {
    "name": "$source",
    "type": "string",
    "description": "The source of where the data is coming from",
    "sample_value": "[Vendo - Shopify Data Intelligence]"
  }, {
    "name": "utm_medium",
    "type": "string",
    "description": "The last seen attributed medium value",
    "sample_value": "[blog, organic, social]"
  }, {
    "name": "event_type",
    "type": "string",
    "description": "Indicates whether an event is a standard or a custom event",
    "sample_value": "[custom, standard]"
  }, {
    "name": "utm_source",
    "type": "string",
    "description": "The last seen attributed source value",
    "sample_value": "[facebook, google, linkedin]"
  }, {
    "name": "utm_campaign",
    "type": "string",
    "description": "The last seen attributed campaign value",
    "sample_value": "[new-product-release, summer-sale]"
  }, {
    "name": "utm_content",
    "type": "string",
    "description": "The last seen attributed content value",
    "sample_value": "[pricing, sales]"
  }, {
    "name": "search_query",
    "type": "string",
    "description": "The search query of in the website",
    "sample_value": "[snowboards]"
  }, {
    "name": "utm_term",
    "type": "string",
    "description": "The last seen attributed term value",
    "sample_value": "[sunscreen, vegan-shampoo]"
  }, {
    "name": "time",
    "type": "number",
    "description": "Unix timestamp (e.g., 1748189059) for when the event occurred. Usage: TIMESTAMP_SECONDS(time) gives the full timestamp. DATETIME(TIMESTAMP_SECONDS(time)) gives the date and time in local time (no timezone). DATE(TIMESTAMP_SECONDS(time)) gives just the date.",
    "sample_value": 1748189059
  }]
}

]  # Properly close EVENT_TABLE_SCHEMA






def get_data_dictionary() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get both user and event table schemas.
    Returns:
        Dict[str, List[Dict[str, Any]]]: User and event table schema definitions
    """
    return {
        'user': USER_TABLE_SCHEMA.copy(),
        'events': EVENT_TABLE_SCHEMA.copy(),
    }

def print_schemas(schema: str = 'all') -> None:
    """
    Pretty-print the user and/or event schemas.
    Args:
        schema (str): 'user', 'events', or 'all' (default: 'all')
    """
    data = get_data_dictionary()
    if schema == 'user':
        print('USER_TABLE_SCHEMA:')
        print(json.dumps(data['user'], indent=2, ensure_ascii=False))
    elif schema == 'events':
        print('EVENT_TABLE_SCHEMA:')
        print(json.dumps(data['events'], indent=2, ensure_ascii=False))
    else:
        print('USER_TABLE_SCHEMA:')
        print(json.dumps(data['user'], indent=2, ensure_ascii=False))
        print('\nEVENT_TABLE_SCHEMA:')
        print(json.dumps(data['events'], indent=2, ensure_ascii=False))

def get_user_properties() -> list[dict]:
    """
    Return a copy of the user table schema.
    """
    return USER_TABLE_SCHEMA.copy()

def get_events() -> list[dict]:
    """
    Return a copy of the event table schema.
    """
    return EVENT_TABLE_SCHEMA.copy()

