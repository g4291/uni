import React from 'react';
import { UniApiContext } from '../api';


/**
 * Custom hook for logging out of the Uni API.
 * @returns A function that can be called to initiate the logout process.
 */
export function useUniLogout(): () => void {
    const ctx = React.useContext(UniApiContext)

    return () => {
        ctx.logout()
    }
}

export default useUniLogout;