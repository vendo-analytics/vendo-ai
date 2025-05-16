import { useChat as useVercelChat } from 'ai/react';
import { Message, CreateMessage, ChatRequestOptions } from 'ai';

export function useChat({
  api,
  onResponse,
}: {
  api: string;
  onResponse?: (response: Response) => void;
}) {
  const {
    messages,
    input,
    handleInputChange,
    handleSubmit: vercelHandleSubmit,
    isLoading,
    stop,
  } = useVercelChat({
    api,
    onResponse,
  });

  const handleSubmit = (
    event?: { preventDefault?: () => void },
    chatRequestOptions?: ChatRequestOptions
  ) => {
    if (event?.preventDefault) {
      event.preventDefault();
    }
    return vercelHandleSubmit(event, chatRequestOptions);
  };

  return {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    stop,
  };
} 