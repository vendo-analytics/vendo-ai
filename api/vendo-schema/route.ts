import { type NextRequest, NextResponse } from "next/server"

// This is a mock implementation - in a real app, you would fetch this from your database
export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const connectionId = searchParams.get("connection_id")

  // In a real implementation, you would use the connectionId to fetch the correct data
  // For now, we'll return the sample data

  const sampleData = {
    summary: {
      total_events: 200,
      date_range: {
        earliest_event: "2024-07-01T07:04:00",
        latest_event: "2025-06-28T20:30:00",
      },
      last_30_days: {
        period_start: "2025-05-10T22:40:22",
        period_end: "2025-06-09T22:40:22",
        total_events: 21,
        events: {
          "Cart Abandoned": {
            last_30_day_count: 2,
            status: "live",
          },
          "Page Viewed": {
            last_30_day_count: 10,
            status: "live",
          },
          "Order Received": {
            last_30_day_count: 4,
            status: "live",
          },
          Signup: {
            last_30_day_count: 5,
            status: "live",
          },
        },
      },
      status_summary: {
        events: {
          new: 0,
          inactive: 0,
          live: 4,
        },
        properties: {
          new: 0,
          inactive: 3,
          live: 19,
        },
      },
    },
    events: {
      "Cart Abandoned": {
        first_seen: "2024-07-01T07:04:00",
        last_seen: "2025-06-28T20:30:00",
        last_30_day_count: 2,
        properties: {
          cart_value: {
            data_type: "integer",
            first_seen: "2024-07-01T07:04:00",
            last_seen: "2025-06-28T20:30:00",
            sample_values: [228, 249, 174],
            status: "live",
            description: "The total value of items in the cart",
          },
          user_email: {
            data_type: "string",
            first_seen: "2024-07-01T07:04:00",
            last_seen: "2025-06-28T20:30:00",
            sample_values: ["user510@example.com", "user886@example.com", "user574@example.com"],
            status: "live",
            description: "Email of the user who abandoned the cart",
          },
          exit_page: {
            data_type: "string",
            first_seen: "2024-07-01T07:04:00",
            last_seen: "2025-02-17T02:42:00",
            sample_values: ["/checkout", "/shipping"],
            status: "inactive",
            description: "The last page viewed before abandoning",
          },
          abandoned_products: {
            data_type: "array",
            first_seen: "2024-07-11T09:51:00",
            last_seen: "2025-05-02T09:42:00",
            sample_values: ["product_103", "product_345", "product_876"],
            status: "inactive",
            description: "List of product IDs in the abandoned cart",
          },
          time_in_cart: {
            data_type: "integer",
            first_seen: "2024-08-10T18:32:00",
            last_seen: "2025-06-23T14:21:00",
            sample_values: [69, 77, 112],
            status: "live",
            description: "Time in seconds items were in cart before abandonment",
          },
        },
        status: "live",
        description: "Tracks when users add items to cart but leave without completing purchase",
      },
      "Page Viewed": {
        first_seen: "2024-07-01T09:01:00",
        last_seen: "2025-06-19T16:25:00",
        last_30_day_count: 10,
        properties: {
          current_URL: {
            data_type: "string",
            first_seen: "2024-07-01T09:01:00",
            last_seen: "2025-06-19T16:25:00",
            sample_values: [
              "https://example.com/support",
              "https://example.com/pricing",
              "https://example.com/category/clothing",
            ],
            status: "live",
            description: "Full URL of the viewed page",
          },
          page_path: {
            data_type: "string",
            first_seen: "2024-07-01T09:01:00",
            last_seen: "2025-06-19T16:25:00",
            sample_values: ["/support", "/pricing", "/category/clothing"],
            status: "live",
            description: "Path component of the URL",
          },
          utm_source: {
            data_type: "string",
            first_seen: "2024-07-01T09:01:00",
            last_seen: "2025-06-19T16:25:00",
            sample_values: ["linkedin", "twitter", "email"],
            status: "live",
            description: "Marketing source that directed to this page",
          },
          device_type: {
            data_type: "string",
            first_seen: "2024-07-01T09:01:00",
            last_seen: "2025-05-18T14:05:00",
            sample_values: ["desktop", "tablet", "mobile"],
            status: "live",
            description: "Type of device used to view the page",
          },
          utm_campaign: {
            data_type: "string",
            first_seen: "2024-07-21T10:44:00",
            last_seen: "2025-06-02T07:12:00",
            sample_values: ["back_to_school", "new_year", "valentine"],
            status: "live",
            description: "Marketing campaign associated with the visit",
          },
          referrer: {
            data_type: "string",
            first_seen: "2024-07-26T20:58:00",
            last_seen: "2025-06-19T16:25:00",
            sample_values: ["https://facebook.com", "https://linkedin.com", "https://twitter.com"],
            status: "live",
            description: "URL that referred the user to this page",
          },
          one_time_property: {
            data_type: "string",
            first_seen: "2024-07-26T23:58:00",
            last_seen: "2025-05-20T22:34:00",
            sample_values: ["yes"],
            status: "live",
            description: "Special property for one-time events",
          },
        },
        status: "live",
        description: "Tracks when users view any page on the website",
      },
      "Order Received": {
        first_seen: "2024-07-09T10:09:00",
        last_seen: "2025-06-15T09:13:00",
        last_30_day_count: 4,
        properties: {
          cart_value: {
            data_type: "integer",
            first_seen: "2024-07-09T10:09:00",
            last_seen: "2025-06-15T09:13:00",
            sample_values: [180, 481, 69],
            status: "live",
            description: "Total value of the order in cents",
          },
          products: {
            data_type: "array",
            first_seen: "2024-07-09T10:09:00",
            last_seen: "2025-06-15T09:13:00",
            sample_values: [
              {
                product_id: "567",
                quantity: 4,
              },
              {
                product_id: "789",
                quantity: 5,
              },
              {
                product_id: "012",
                quantity: 5,
              },
            ],
            status: "live",
            description: "List of products in the order with quantities",
          },
          payment_method: {
            data_type: "string",
            first_seen: "2024-07-09T10:09:00",
            last_seen: "2025-06-15T09:13:00",
            sample_values: ["bank_transfer", "apple_pay", "paypal"],
            status: "live",
            description: "Method used to pay for the order",
          },
          shipping_method: {
            data_type: "string",
            first_seen: "2024-08-03T16:07:00",
            last_seen: "2025-05-30T13:44:00",
            sample_values: ["overnight", "express", "standard"],
            status: "live",
            description: "Shipping method selected for the order",
          },
          discount_code: {
            data_type: "string",
            first_seen: "2024-08-12T08:27:00",
            last_seen: "2025-05-29T06:21:00",
            sample_values: ["HOLIDAY", "FIRST20", "SAVE10"],
            status: "live",
            description: "Discount code applied to the order",
          },
        },
        status: "live",
        description: "Tracks when an order is successfully placed",
      },
      Signup: {
        first_seen: "2024-07-15T02:44:00",
        last_seen: "2025-06-25T16:22:00",
        last_30_day_count: 5,
        properties: {
          signup_method: {
            data_type: "string",
            first_seen: "2024-07-15T02:44:00",
            last_seen: "2025-06-25T16:22:00",
            sample_values: ["google", "github", "facebook"],
            status: "live",
            description: "The authentication method used for registration",
          },
          referrer: {
            data_type: "string",
            first_seen: "2024-07-15T02:44:00",
            last_seen: "2025-06-25T16:22:00",
            sample_values: ["https://youtube.com", "https://twitter.com", "https://google.com"],
            status: "live",
            description: "The source that brought the user to the signup page",
          },
          newsletter_opt_in: {
            data_type: "boolean",
            first_seen: "2024-07-15T02:44:00",
            last_seen: "2025-05-17T23:51:00",
            sample_values: [false, true],
            status: "live",
            description: "Whether the user opted in to receive marketing emails during signup",
          },
          promo_code_used: {
            data_type: "string",
            first_seen: "2024-08-02T00:59:00",
            last_seen: "2025-04-29T18:48:00",
            sample_values: ["SOCIAL15", "WELCOME10"],
            status: "inactive",
            description: "Promotional code used during signup if any",
          },
          age_group: {
            data_type: "string",
            first_seen: "2024-10-05T15:18:00",
            last_seen: "2025-06-22T17:59:00",
            sample_values: ["55+", "25-34", "35-44"],
            status: "live",
            description: "Age range of the user",
          },
        },
        status: "live",
        description:
          "Captures user registration events across different signup methods. Essential for tracking user acquisition, conversion rates, and optimizing the onboarding funnel.",
      },
    },
  }

  return NextResponse.json(sampleData)
}
