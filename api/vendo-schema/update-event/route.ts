import { type NextRequest, NextResponse } from "next/server"

export async function PUT(request: NextRequest) {
  try {
    const { connection_id, event_name, description } = await request.json()

    // Here you would update your database with the new event description
    // For now, we'll just log it and return success
    console.log("Updating event description:", {
      connection_id,
      event_name,
      description,
    })

    // Example: Update your database
    // await db.events.update({
    //   where: {
    //     connectionId: connection_id,
    //     eventName: event_name
    //   },
    //   data: {
    //     description
    //   }
    // })

    return NextResponse.json({
      success: true,
      message: "Event description updated successfully",
    })
  } catch (error) {
    console.error("Error updating event description:", error)
    return NextResponse.json({ error: "Failed to update event description" }, { status: 500 })
  }
}
