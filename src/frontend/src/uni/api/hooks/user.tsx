import React from 'react';
import { IUniUser } from '../common';
import { UniApiContext } from '../api';

/**
 * Custom hook that provides the current Uni user and a function to reload the user data.
 * @returns A tuple containing the Uni user object and a function to reload the user data.
 * @throws {Error} Throws an error if the user is not authenticated.
 */
export function useUniUser(): [IUniUser, () => void] {
    const ctx = React.useContext(UniApiContext)

    if (!ctx.user.data) throw new Error("uni error: user not authenticated")
    return [ctx.user.data, ctx.user.reload]
}

export default useUniUser;