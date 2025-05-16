import { OpenAIStream, StreamingTextResponse } from 'ai';
import OpenAI from 'openai';

declare module 'ai' {
  export function OpenAIStream(response: any): ReadableStream;
}

declare module 'ai/edge' {
  export class StreamingTextResponse extends Response {
    constructor(stream: ReadableStream);
  }
}

export const runtime = 'edge';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(req: Request) {
  const { messages } = await req.json();

  const response = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    stream: true,
    messages: [
      {
        role: 'system',
        content: 'You are an analytics AI assistant. Analyze questions and provide insights based on the conversation history.',
      },
      ...messages.map((message: any) => ({
        content: message.content,
        role: message.role,
      })),
    ],
  });

  const stream = OpenAIStream(response);
  return new StreamingTextResponse(stream);
} 