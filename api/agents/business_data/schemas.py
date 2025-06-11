"""Database schemas and table definitions for the data retrieval agent."""

from typing import Dict, List, Any


# User Table Schema
USER_TABLE_SCHEMA = [
    {"name": "customer_tags", "mode": "REPEATED", "type": "RECORD", "description": "The tags associated with the customer"},
    {"name": "customer_tags.value", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "distinct_id", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "email_marketing_consent_opt_in_level", "mode": "NULLABLE", "type": "STRING", "description": "Shows the consent opt in level of users"},
    {"name": "email_marketing_consent_state", "mode": "NULLABLE", "type": "STRING", "description": "Whether user is subscribed or not to our email marketing"},
    {"name": "first_order_date", "mode": "NULLABLE", "type": "TIMESTAMP", "description": "The date of the first paid order of the customers"},
    {"name": "first_seen", "mode": "NULLABLE", "type": "TIMESTAMP", "description": "When the user was first seen. This data is stored in the users browser on their first visit."},
    {"name": "gclid", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "last_order_date", "mode": "NULLABLE", "type": "TIMESTAMP", "description": "The date of the last paid order of the customer"},
    {"name": "marketing_state", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_city", "mode": "NULLABLE", "type": "STRING", "description": "The City"},
    {"name": "mp_reserved_country_code", "mode": "NULLABLE", "type": "STRING", "description": "The country of the order"},
    {"name": "mp_reserved_created", "mode": "NULLABLE", "type": "TIMESTAMP", "description": ""},
    {"name": "mp_reserved_email", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_first_name", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_initial_utm_campaign", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_initial_utm_content", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_initial_utm_medium", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_initial_utm_source", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_initial_utm_term", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_last_name", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_last_seen", "mode": "NULLABLE", "type": "TIMESTAMP", "description": ""},
    {"name": "mp_reserved_phone", "mode": "NULLABLE", "type": "STRING", "description": "The phone number"},
    {"name": "mp_reserved_region", "mode": "NULLABLE", "type": "STRING", "description": "The state (Australia) / region (US)"},
    {"name": "mp_reserved_timezone", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_user_id", "mode": "NULLABLE", "type": "STRING", "description": "The client-side ID of the customer, provided by Shopify"},
    {"name": "msclkid", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "order_count", "mode": "NULLABLE", "type": "NUMERIC", "description": "Number of orders that the customer have placed"},
    {"name": "shopify_customer_id", "mode": "NULLABLE", "type": "STRING", "description": "Shopify Customer ID"},
    {"name": "shopify_customer_notes", "mode": "NULLABLE", "type": "STRING", "description": "Admin entered customer notes"},
    {"name": "state", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "tax_exempt", "mode": "NULLABLE", "type": "BOOLEAN", "description": "Whether customer is exempt from tax or not"},
    {"name": "total_spent", "mode": "NULLABLE", "type": "STRING", "description": "Total amount spent by customer"},
    {"name": "utm_campaign", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "utm_content", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "utm_medium", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "utm_source", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "utm_term", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "verified_email", "mode": "NULLABLE", "type": "BOOLEAN", "description": "Whether the customers emails verified or not"},
    {"name": "shipping_address", "mode": "REPEATED", "type": "RECORD", "description": "Latest shipping address of the customer"},
]

# Event Table Schema
EVENT_TABLE_SCHEMA = [
    {"name": "abandoned_checkout_url", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "account_id", "mode": "NULLABLE", "type": "STRING", "description": "Advertising account ID"},
    {"name": "account_name", "mode": "NULLABLE", "type": "STRING", "description": "Advertising Account name"},
    {"name": "ad_id", "mode": "NULLABLE", "type": "STRING", "description": "Advertising Ad ID"},
    {"name": "adgroup_id", "mode": "NULLABLE", "type": "STRING", "description": "Advertising Ad Group ID - only valid for Google Ads"},
    {"name": "adgroup_name", "mode": "NULLABLE", "type": "STRING", "description": "Advertising Ad Group Name - only valid for Google Ads"},
    {"name": "amount", "mode": "NULLABLE", "type": "STRING", "description": "Used for the monetary amount of the object (Product Added To Cart, Cart Viewed) !!! This is coming as null."},
    {"name": "app_id", "mode": "NULLABLE", "type": "STRING", "description": "The Shopify APP ID that the order is placed from."},
    {"name": "billing_address", "mode": "NULLABLE", "type": "STRING", "description": "The billing address where the order will be billed to (Order Received)"},
    {"name": "campaign_id", "mode": "NULLABLE", "type": "STRING", "description": "Advertising Campaign ID - All ad platforms have this"},
    {"name": "campaign_name", "mode": "NULLABLE", "type": "STRING", "description": "Advertising Campaign ID - All ad platforms have this"},
    {"name": "cart_subtotal_amount", "mode": "NULLABLE", "type": "STRING", "description": "The price at checkout before duties, shipping, and taxes (Order Received, Checkout Completed)"},
    {"name": "cart_total_amount", "mode": "NULLABLE", "type": "STRING", "description": "The sum of all the items in the checkout, including duties, taxes, and discounts (Order Received, Checkout Completed). USE THIS FOR REVENUE RELATED QUESTIONS"},
    {"name": "checkout_attributes", "mode": "NULLABLE", "type": "STRING", "description": "A list of attributes accumulated throughout the checkout process (Checkout Completed)"},
    {"name": "checkout_id", "mode": "NULLABLE", "type": "STRING", "description": "The unique checkout ID of the checkout"},
    {"name": "checkout_token", "mode": "NULLABLE", "type": "STRING", "description": "A unique identifier for a particular checkout (Checkout Completed)"},
    {"name": "collection_id", "mode": "NULLABLE", "type": "STRING", "description": "the product category ID - one product may belong to multiple categories"},
    {"name": "collection_title", "mode": "NULLABLE", "type": "STRING", "description": "the product category name - one product may belong to multiple categories"},
    {"name": "confirmed", "mode": "NULLABLE", "type": "STRING", "description": "Status or the orders if it was confirmed or not (Products Purchased)"},
    {"name": "conversions", "mode": "NULLABLE", "type": "STRING", "description": "The conversions reported from ad platforms"},
    {"name": "cost_reporting", "mode": "NULLABLE", "type": "STRING", "description": "The advertising cost in the reporting currency AUD"},
    {"name": "cost_source", "mode": "NULLABLE", "type": "STRING", "description": "The advertising cost in the source currency - variable"},
    {"name": "currency", "mode": "NULLABLE", "type": "STRING", "description": "The three-letter code that represents the currency (Order Received, , etc.)"},
    {"name": "currency_reporting", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "currency_source", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "custom_order_attributes", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "delivery_date", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "delivery_speed", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "delivery_speed_weekdays", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "device_category", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "discount", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "email", "mode": "NULLABLE", "type": "STRING", "description": "The email attached to this checkout (Order Received, , Checkout Completed)"},
    {"name": "event", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "fbclid", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "fulfillment_speed", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "fulfillment_speed_weekdays", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "fulfillment_status", "mode": "NULLABLE", "type": "STRING", "description": "The payment state of an order ()"},
    {"name": "gclid", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "job_id", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "language", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "landing_page", "mode": "NULLABLE", "type": "STRING", "description": "The first page a user visits when arriving on a website or app ()"},
    # ... continuing with all mp_reserved fields
    {"name": "mp_reserved_ad_clicks", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_ad_cost", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_ad_impressions", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_ad_platform", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_browser", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_browser_version", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_country", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_country_code", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_current_url", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_device", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_device_id", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_email", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_import", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_initial_utm_campaign", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_initial_utm_content", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_initial_utm_medium", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_initial_utm_source", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_initial_utm_term", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_lib_version", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_marketing_state", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_mp_replay_id", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_mp_replay_retention_period", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_os", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_phone", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_region", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_screen_height", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_screen_width", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_source", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_timezone", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_user_agent", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_user_id", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "mp_reserved_zip", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "note", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "order_id", "mode": "NULLABLE", "type": "STRING", "description": "The order ID is assigned by Shopify. This is the displayed order ID that shows in the store admin (Order Received, , Checkout Completed)"},
    {"name": "order_tags", "mode": "NULLABLE", "type": "STRING", "description": "The tags associated with orders ()"},
    {"name": "page_title", "mode": "NULLABLE", "type": "STRING", "description": "The title of the page (Page Viewed, Product Viewed, etc.)"},
    {"name": "path_name", "mode": "NULLABLE", "type": "STRING", "description": "The path of the URL (Page Viewed, Product Viewed, etc.)"},
    {"name": "payment_gateway", "mode": "NULLABLE", "type": "STRING", "description": "What user use to pay for the order ()"},
    {"name": "phone", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "publisher_platform", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "replay_env", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "replay_length_ms", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "replay_region", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "replay_start_time", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "replay_start_url", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "search_query", "mode": "NULLABLE", "type": "STRING", "description": "The search query of in the website (Search Submitted)"},
    {"name": "seq_no", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "shipping_amount", "mode": "NULLABLE", "type": "STRING", "description": "Total shipping cost (Order Received)"},
    {"name": "shipping_address", "mode": "NULLABLE", "type": "STRING", "description": "The shipping address to where the line items will be shipped (Order Received, Checkout Completed)"},
    {"name": "source_name", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "state", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "tax_amount", "mode": "NULLABLE", "type": "STRING", "description": "Tax Amount (Order Received)"},
    {"name": "test", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "time", "mode": "NULLABLE", "type": "TIMESTAMP", "description": ""},
    {"name": "tracking_number", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "total_discounts", "mode": "NULLABLE", "type": "STRING", "description": "The total amount of all discounts applied to the order (Order Received)"},
    {"name": "total_spent", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "utm_campaign", "mode": "NULLABLE", "type": "STRING", "description": "The last seen attributed campaign value (Page Viewed, Product Viewed, etc.)"},
    {"name": "utm_content", "mode": "NULLABLE", "type": "STRING", "description": "The last seen attributed content value (Page Viewed, Product Viewed, etc.)"},
    {"name": "utm_creative_format", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "utm_id", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "utm_medium", "mode": "NULLABLE", "type": "STRING", "description": "The last seen attributed medium value (Page Viewed, Product Viewed, etc.)"},
    {"name": "utm_marketing_tactic", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "utm_source", "mode": "NULLABLE", "type": "STRING", "description": "The last seen attributed source value (Page Viewed, Product Viewed, etc.)"},
    {"name": "utm_source_platform", "mode": "NULLABLE", "type": "STRING", "description": ""},
    {"name": "utm_term", "mode": "NULLABLE", "type": "STRING", "description": "The last seen attributed term value (Page Viewed, Product Viewed, etc.)"},
]



# Event Names and Descriptions
EVENT_NAMES = {
    "Page Viewed": "The page_viewed event logs an instance where a buyer visited a page. This event is available on the online store, checkout, and order status pages.",
    "Product Viewed": "The product_viewed event logs an instance where a buyer visited a product details page. This event is available on the product page.",
    "Collection Viewed": "The collection_viewed event logs an instance where a buyer visited a product collection index page. This event is available on the online store page",
    "$mp_session_record": "Session recording event batch sent from client. This is a Mixpanel system event. Use this event if the user wants to see the session replay URLs. The event property name is replay_start_url",
    "Order Received": "The order_received event is sent when a new order is created at Shopify. This order could be received from the online store or other sources. A received order does not mean an order is paid. An order may have multiple financial statuses. Use financial_status event property to see the orders' status. USE THIS FOR Revenue, order calculations.",
    "Checkout Completed": "The checkout_completed event logs when a visitor completes a purchase. This event is available on the order status and checkout pages.",
    "Checkout Shipping Info Submitted": "The checkout_shipping_info_submitted event logs an instance where the buyer chooses a shipping rate. This event is only available in checkouts where checkout extensibility for customizations is enabled",
    "Checkout Started": "The checkout_started event logs an instance of a buyer starting the checkout process. This event is available on the checkout page",
    "Checkout Address Info Submitted": "The checkout_address_info_submitted event logs an instance of a buyer submitting their mailing address. This event is only available in checkouts where checkout extensibility for customizations is enabled",
    "Payment Info Submitted": "The payment_info_submitted event logs an instance of a buyer submitting their payment information. This event is available on the checkout page",
    "Product Added To Cart": "The product_added_to_cart event logs an instance where a buyer added a product to the cart. This event is available on the product page.",
    "Search Submitted": "The search_submitted event logs an instance where a buyer performed a search on the storefront. This event is available on the online store page.",
    "Cart Abandoned": "The cart_abandoned event logs an instance where a abandons their cart",
    "Order Fulfilled": "The order_fulfilled event logs when the shop owner has processed and shipped the order",
    "Order Delivered": "The order_delivered event is sent when an order is delivered, based on the shipment status of the order.",
    "Ad Data": "Contains advertising data imported from platforms such as Google, Meta, and TikTok. This event includes all UTM parameters (utm_source, utm_medium, utm_campaign, etc.) and is used for analyses involving campaign attribution, cost, conversions, and other ad performance metrics. **This event can be used for ad spend or advertising spend calculations using the `cost_reporting` or `cost_source` event properties.**",
    "Ad Geo Data": "Contains advertising data imported from platforms such as Google, Meta, and TikTok, focused on geographic breakdowns (e.g., by country or region) and is used for analyses involving campaign attribution, cost, conversions, and other ad performance metrics. This event does **not** include UTM parameters and should be used when the analysis requires location-based ad performance rather than campaign attribution. **This event can also be used for ad spend or advertising spend calculations using the `cost_reporting` or `cost_source` event properties.**",
    "Cart Viewed": "The cart_viewed event logs an instance where a customer visited the cart page.",
    "Product Removed From Cart": "The product_removed_from_cart event logs an instance where a customer removes a product from their cart",
    "Checkout Contact Info Submitted": "The checkout_contact_info_submitted event logs an instance where a buyer submits a checkout form. This event is only available in checkouts where checkout extensibility for customizations is enabled",
    "Order Partially Refunded": "The order_partially_refunded event logs when the order is edited to only refund part of the order"
}

# Ad Data Event Properties
AD_DATA_PROPERTIES = [
    {"name": "$source", "display_name": "Source", "description": "Name of the source where the data syncs. This will be Vendo data."},
    {"name": "account_id", "display_name": "Advertising Account ID", "description": "ID of the ad account"},
    {"name": "account_name", "display_name": "Advertising Account Name", "description": "Name of the ad account, as displayed via API"},
    {"name": "ad_id", "display_name": "Ad ID", "description": "ID of the ad set by the advertising platform."},
    {"name": "campaign_id", "display_name": "Campaign ID", "description": "ID of the campaign set by the advertising platform."},
    {"name": "campaign_name", "display_name": "Campaign Name", "description": "Name of the campaign as it appears in the advertising platform."},
    {"name": "conversion_value", "display_name": "Conversion Value", "description": "The value associated with the conversion"},
    {"name": "conversions", "display_name": "Conversions", "description": "Number of conversions"},
    {"name": "cost_reporting", "display_name": "Cost Reporting", "description": "The advertising cost converted to the reporting currency in Mixpanel"},
    {"name": "cost_source", "display_name": "Cost Source", "description": "The advertising cost in the source currency of the advertising platform."},
    {"name": "currency_reporting", "display_name": "Currency Reporting", "description": "The reporting currency in Mixpanel."},
]

# Order Received Event Properties
ORDER_RECEIVED_PROPERTIES = [
    {"name": "$source", "display_name": "Source", "description": "The source of where the data is coming from"},
    {"name": "app_id", "display_name": "App ID", "description": "The ID of the app that created the order"},
    {"name": "app_name", "display_name": "App Name", "description": "The name of the app that created the order"},
    {"name": "billing_address", "display_name": "Billing Address", "description": "The billing address where the order will be billed to"},
    {"name": "cart_subtotal_amount", "display_name": "Cart Subtotal Amount", "description": "The price at checkout before duties, shipping, and taxes"},
    {"name": "cart_total_amount", "display_name": "Cart Total Amount", "description": "The sum of all the items in the checkout, including duties, taxes, and discounts"},
    {"name": "confirmed", "display_name": "Confirmed", "description": "Status or the orders if it was confirmed or not"},
    {"name": "currency", "display_name": "Currency", "description": "The three-letter code that represents the currency, for example, USD. Supported codes include standard ISO 4217 codes, legacy codes, and non-standard codes"},
    {"name": "custom_order_attributes", "display_name": "Custom Order Attributes", "description": "A list of details that have been added to the order."},
    {"name": "discount", "display_name": "Discount Codes", "description": "Discount codes for the order"},
    {"name": "email", "display_name": "Email", "description": "The email attached to this checkout"},
    {"name": "financial_status", "display_name": "Financial Status", "description": "The payment state of an order"},
    {"name": "landing_page", "display_name": "Landing Page", "description": "The first page a user visits when arriving on a website or app"},
    {"name": "note", "display_name": "Order Note", "description": "Order note"},
    {"name": "order_id", "display_name": "Order ID", "description": "The order ID is assigned by Shopify. This is the displayed order ID that shows in the store admin"},
    {"name": "order_status_url", "display_name": "Order Status URL", "description": "The URL of the page when order was confirmed"},
    {"name": "order_tags", "display_name": "Order Tags", "description": "The tags associated with orders"},
    {"name": "payment_gateway", "display_name": "Payment Gateway", "description": "What user use to pay for the order"},
    {"name": "products", "display_name": "Products", "description": "A list of line item objects, each one containing information about an item in the checkout"},
    {"name": "shipping_address", "display_name": "Shipping Address", "description": "The shipping address to where the line items will be shipped"},
    {"name": "shipping_amount", "display_name": "Shipping Amount", "description": "Total shipping cost"},
    {"name": "shopify_order_id", "display_name": "Shopify Order ID", "description": "The Shopify Order ID is a global order ID set by Shopify"},
    {"name": "source_name", "display_name": "Source Name", "description": "The name of the source where the order originated"},
    {"name": "tax_amount", "display_name": "Tax Amount", "description": "Tax Amount"},
    {"name": "test", "display_name": "Test", "description": "Shows whether this order is a test order or not"},
    {"name": "total_discounts", "display_name": "Total Discounts", "description": "The total amount of all discounts applied to the order"},
    {"name": "vendo_tracking_version", "display_name": "Vendo Tracking Version", "description": "Vendo tracking version"},
]

# Products Object Schema (for product-related events)
PRODUCTS_OBJECT_SCHEMA = [
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
    {"name": "vendor", "type": "STRING", "example": "Piri Red", "description": "Vendor or brand name"},
]

# Events that contain the products object
PRODUCT_EVENTS = [
    "Product Viewed",
    "Collection Viewed", 
    "Product Added To Cart",
    "Checkout Started",
    "Checkout Shipping Info Submitted",
    "Payment Info Submitted",
    "Product Removed From Cart",
    "Checkout Completed",
    "Order Fulfilled"
]


def get_user_table_schema() -> List[Dict[str, Any]]:
    """
    Get the user table schema.
    
    Returns:
        List[Dict[str, Any]]: User table schema definitions
    """
    return USER_TABLE_SCHEMA.copy()


def get_event_table_schema() -> List[Dict[str, Any]]:
    """
    Get the event table schema.
    
    Returns:
        List[Dict[str, Any]]: Event table schema definitions
    """
    return EVENT_TABLE_SCHEMA.copy()


def get_event_names() -> Dict[str, str]:
    """
    Get the event names and their descriptions.
    
    Returns:
        Dict[str, str]: Event names mapped to descriptions
    """
    return EVENT_NAMES.copy()


def get_ad_data_properties() -> List[Dict[str, str]]:
    """
    Get the Ad Data event properties.
    
    Returns:
        List[Dict[str, str]]: Ad Data event property definitions
    """
    return AD_DATA_PROPERTIES.copy()


def get_order_received_properties() -> List[Dict[str, str]]:
    """
    Get the Order Received event properties.
    
    Returns:
        List[Dict[str, str]]: Order Received event property definitions
    """
    return ORDER_RECEIVED_PROPERTIES.copy()


def get_products_object_schema() -> List[Dict[str, str]]:
    """
    Get the products object schema for product-related events.
    
    Returns:
        List[Dict[str, str]]: Products object schema definitions
    """
    return PRODUCTS_OBJECT_SCHEMA.copy()


def get_product_events() -> List[str]:
    """
    Get the list of events that contain the products object.
    
    Returns:
        List[str]: List of event names that contain products
    """
    return PRODUCT_EVENTS.copy()


def format_user_table_schema_for_prompt(user_table: str) -> str:
    """
    Format the user table schema for inclusion in prompts.
    
    Args:
        user_table (str): The user table name
        
    Returns:
        str: Formatted schema string for prompts
    """
    schema_text = f"### User Table: `{user_table}`\n\n"
    schema_text += "| Name | Mode | Type | Description |\n"
    schema_text += "|------|------|------|-------------|\n"
    
    for field in USER_TABLE_SCHEMA:
        schema_text += f"| {field['name']} | {field['mode']} | {field['type']} | {field['description']} |\n"
    
    return schema_text


def format_event_table_schema_for_prompt(event_table: str) -> str:
    """
    Format the event table schema for inclusion in prompts.
    
    Args:
        event_table (str): The event table name
        
    Returns:
        str: Formatted schema string for prompts
    """
    schema_text = f"### Event Table: `{event_table}`\n\n"
    schema_text += "| Name | Mode | Type | Description |\n"
    schema_text += "|------|------|------|-------------|\n"
    
    for field in EVENT_TABLE_SCHEMA:
        schema_text += f"| {field['name']} | {field['mode']} | {field['type']} | {field['description']} |\n"
    
    return schema_text


def format_event_names_for_prompt() -> str:
    """
    Format the event names for inclusion in prompts.
    
    Returns:
        str: Formatted event names string for prompts
    """
    schema_text = "### Event Names (export table)\n"
    
    for event_name, description in EVENT_NAMES.items():
        schema_text += f"- {event_name}: {description}\n"
    
    return schema_text


def format_all_schemas_for_prompt(user_table: str, event_table: str) -> str:
    """
    Format all schemas for inclusion in prompts.
    
    Args:
        user_table (str): The user table name
        event_table (str): The event table name
        
    Returns:
        str: Complete formatted schemas string for prompts
    """
    schemas_text = "## Schemas\n\n"
    schemas_text += format_user_table_schema_for_prompt(user_table) + "\n\n"
    schemas_text += format_event_table_schema_for_prompt(event_table) + "\n\n"
    schemas_text += format_event_names_for_prompt() + "\n\n"
    
    # Add event property definitions
    schemas_text += "### Event Property Definitions - `Ad Data`\n\n"
    schemas_text += "Ad Data events contain advertising data imported from platforms like Google, Meta, TikTok, etc. These properties are used to calculate advertising cost, impressions, and other ad metrics. Ad data can be joined to user or event data using UTM properties for attribution and analysis.\n\n"
    schemas_text += "| Name | Display Name | Description |\n"
    schemas_text += "|------|--------------|-------------|\n"
    
    for prop in AD_DATA_PROPERTIES:
        schemas_text += f"| {prop['name']} | {prop['display_name']} | {prop['description']} |\n"
    
    schemas_text += "\n\n### Event Property Definitions - `Order Received`\n\n"
    schemas_text += "The following table lists key event properties available for the 'Order Received' event. These fields are used for order, revenue, and checkout analyses.\n\n"
    schemas_text += "| Name | Display Name | Description |\n"
    schemas_text += "|------|--------------|-------------|\n"
    
    for prop in ORDER_RECEIVED_PROPERTIES:
        schemas_text += f"| {prop['name']} | {prop['display_name']} | {prop['description']} |\n"
    
    schemas_text += "\n\n### Event Property Definitions - `products` event property object (for product-related events)\n\n"
    schemas_text += f"The `products` field is a repeated RECORD (array of objects) present in the following events:\n"
    for event in PRODUCT_EVENTS:
        schemas_text += f"- {event}\n"
    
    schemas_text += "\n| Name | Type | Example Value | Description |\n"
    schemas_text += "|------|------|---------------|-------------|\n"
    
    for field in PRODUCTS_OBJECT_SCHEMA:
        schemas_text += f"| {field['name']} | {field['type']} | {field['example']} | {field['description']} |\n"
    
    return schemas_text 