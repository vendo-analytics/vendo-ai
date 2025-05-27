import { useEffect, useRef, type RefObject } from "react";

export function useScrollToBottom<T extends HTMLElement>(): [
  RefObject<T>,
  RefObject<T>,
] {
  const containerRef = useRef<T>(null);
  const endRef = useRef<T>(null);

  useEffect(() => {
    const container = containerRef.current;
    const end = endRef.current;

    if (container && end) {
      const observer = new MutationObserver((mutations) => {
        // Check if any mutations involve significant content changes
        const hasSignificantChange = mutations.some(mutation => {
          if (mutation.type === 'childList') {
            const addedNodes = Array.from(mutation.addedNodes);
            return addedNodes.some(node => {
              // Check for text nodes with content or element nodes
              return (node.nodeType === Node.TEXT_NODE && node.textContent?.trim()) ||
                     (node.nodeType === Node.ELEMENT_NODE);
            });
          }
          // Also trigger on text content changes
          if (mutation.type === 'characterData') {
            return mutation.target.textContent?.trim();
          }
          return false;
        });

        if (hasSignificantChange) {
          // Add a small delay to ensure content is fully rendered
          setTimeout(() => {
            // Scroll to the very bottom with additional offset
            end.scrollIntoView({ behavior: "smooth", block: "start" });
            
            // Additional scroll to ensure we're at the very bottom
            setTimeout(() => {
              if (container) {
                container.scrollTop = container.scrollHeight;
              }
            }, 100);
          }, 50);
        }
      });

      observer.observe(container, {
        childList: true,
        subtree: true,
        attributes: true,
        characterData: true,
      });

      return () => observer.disconnect();
    }
  }, []);

  return [containerRef, endRef];
}
