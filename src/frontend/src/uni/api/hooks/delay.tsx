import { useRef } from "react";
import { useEffect } from "react";


/**
 * Custom hook that delays the execution of a callback function.
 *
 * @param {() => any} callback - The function to be executed after the delay.
 * @param {any[]} dependencies - The list of dependencies that will trigger the effect.
 * @param {number} delayMs - The delay in milliseconds before executing the callback.
 * @param {boolean} [init=true] - If true, the callback will be executed on the first render.
 *
 * @returns {void}
 */
export function useDelay(callback: () => any, dependencies: any[], delayMs: number, init: boolean = true): void {
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

export default useDelay;