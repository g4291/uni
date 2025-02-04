import React from "react";

export function useUniPrevious<T>(value: T): T | undefined {
    const ref = React.useRef<T>();

    React.useEffect(() => {
        ref.current = value;
    }, [value])

    return ref.current;
}

export default useUniPrevious;