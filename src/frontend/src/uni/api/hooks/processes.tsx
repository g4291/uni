import React from 'react';
import { v4 } from 'uuid';

type ProcessID = string | number;

export interface IUniProcessTracker {
    isRunning: boolean;
    startProcess: () => ProcessID;
    endProcess: (id: ProcessID) => void;
}

export function useUniProcessTracker(): IUniProcessTracker {
    const [processes, setProcesses] = React.useState<Set<ProcessID>>(new Set());

    // Indicates if any processes are running
    const isRunning = processes.size > 0;

    // Starts a process by adding its ID to the set
    const startProcess = React.useCallback(() => {
        const id = v4();
        setProcesses((prevProcesses) => new Set(prevProcesses).add(id));
        return id
    }, []);

    // Ends a process by removing its ID from the set
    const endProcess = React.useCallback((id: ProcessID) => {
        setProcesses((prevProcesses) => {
            const newProcesses = new Set(prevProcesses);
            newProcesses.delete(id);
            return newProcesses;
        });
    }, []);

    return { isRunning, startProcess, endProcess };
}

export default useUniProcessTracker;