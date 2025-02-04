import React from 'react';

export interface IUniLoading {
    loading: boolean;
    on: () => void;
    off: () => void;

}
export function useUniLoading(initState: boolean = false): IUniLoading {

    const [isLoading, setLoading] = React.useState(initState);

    return {
        loading: isLoading, 
        on: () => {setLoading(true)}, 
        off: () => {setLoading(false)}
    };
}

