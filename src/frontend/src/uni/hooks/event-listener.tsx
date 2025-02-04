import React from 'react';

function useEventListener(
  eventName: string,
  handler: (event: any) => void,
  element: HTMLElement | Document | Window | null = window
): void {
  // Create a ref that stores handler
  const savedHandler = React.useRef<(event: Event) => void>();

  React.useEffect(() => {
    // Update saved handler if handler changes
    savedHandler.current = handler;
  }, [handler]);

  React.useEffect(() => {
    // Make sure element supports addEventListener
    const targetElement = element || window;
    if (!(targetElement && targetElement.addEventListener)) {
      return;
    }

    // Create event listener that calls handler function stored in ref
    const eventListener = (event: Event) => {
      savedHandler.current?.(event);
    };

    targetElement.addEventListener(eventName, eventListener);

    // Remove event listener on cleanup
    return () => {
      targetElement.removeEventListener(eventName, eventListener);
    };
  }, [eventName, element]); // Re-run if eventName or element changes
}

export default useEventListener;