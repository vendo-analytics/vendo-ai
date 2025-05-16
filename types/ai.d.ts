declare module 'ai' {
  export function OpenAIStream(response: any): ReadableStream;
}

declare module 'ai/edge' {
  export class StreamingTextResponse extends Response {
    constructor(stream: ReadableStream);
  }
} 