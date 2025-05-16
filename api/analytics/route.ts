import { NextResponse } from "next/server";
import { run_analytics_agent } from "../agents/analytics_agent";

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    const lastMessage = messages[messages.length - 1];
    
    if (!lastMessage?.content) {
      return NextResponse.json(
        { error: "No message content provided" },
        { status: 400 }
      );
    }

    const response = await run_analytics_agent(
      lastMessage.content,
      messages.slice(0, -1)
    );

    return NextResponse.json({ response });
  } catch (error) {
    console.error("Error in analytics endpoint:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
} 