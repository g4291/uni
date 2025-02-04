import { useRef } from "react";
import { useEffect } from "react";

/**
 * Custom hook that delays the execution of a callback function.
 * 
 * @param callback - The callback function to be executed after the delay.
 * @param dependencies - The dependencies that trigger the callback when changed.
 * @param delayMs - The delay in milliseconds before executing the callback.
 * @param init - Optional parameter to control whether the callback should be executed on initial render. Defaults to true.
 */
export function useUniDelay(callback: () => any, dependencies: any[], delayMs: number, init: boolean = true): void {
    const firstUpdate = useRef(true);

    useEffect(() => {
        // first update?
        if (firstUpdate.current) {
            firstUpdate.current = false;
            if (!init) return () => { }
        }

        // set timeout to run callback
        const delayFn = setTimeout(callback, delayMs);

        return () => {
            clearTimeout(delayFn);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, dependencies);
}

export default useUniDelay;