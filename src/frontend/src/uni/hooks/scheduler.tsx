import React from "react";


/**
 * Custom hook for scheduling a task at a specified interval.
 *
 * @param task - The task to be executed.
 * @param interval - The interval in milliseconds at which the task should be executed. Default is 5000ms.
 * @param suspended - A boolean indicating whether the task should be suspended. Default is false.
 */
export function useUniScheduler(task: () => void, interval: number = 5000, suspended: boolean = false): void {
    // refs
    const intervalRef = React.useRef<any>(null)
    const taskRef = React.useRef<any>();

    // clear interval
    const clear = () => {
        if (intervalRef.current) clearInterval(intervalRef.current);
    }

    // update taskRef on task change
    React.useEffect(() => {
        taskRef.current = task;
    }, [task])

    // on mount
    React.useEffect(() => {
        // try to run task and create interval
        // suspended, clear interval and return
        if (suspended) {
            clear()
            return
        }

        try {
            // interval
            if (interval) {
                intervalRef.current = setInterval(() => {
                    taskRef.current();
                }, interval);
            }
        }
        catch (e) {
            console.error(e);
        }

        // clear interval
        return clear;
        
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [suspended, interval]);
};

export default useUniScheduler;