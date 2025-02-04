import React, { useEffect, useState } from "react";


export function useUniStateTimeout<T>(duration: number): [T | undefined, React.Dispatch<T | undefined>] {

    const [inState, setInState] = useState<T>()
    const [outState, setOutState] = useState<T>()

    // use effect on inState change
    useEffect(() => {
        if (inState) {
            // set output
            setOutState(inState)
    
            // start timer
            const timer = setTimeout(() => {
                setOutState(undefined);
                setInState(undefined);
            }, duration)
    
            // clear timer
            return () => {
                clearInterval(timer)
            }
    
        } else {
            setOutState(undefined)
        }

        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [inState])

    return [outState, setInState];
}

export default useUniStateTimeout;