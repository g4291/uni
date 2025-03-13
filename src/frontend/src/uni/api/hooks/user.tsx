import React from 'react';
import { IUniUser } from '../common';
import { UniApiContext } from '../api';

/**
 * Custom hook that provides the current Uni user and a function to reload the user data.
 * @returns A tuple containing the Uni user object and a function to reload the user data.
 * @throws {Error} Throws an error if the user is not authenticated.
 */
export function useUniUser(): [IUniUser, () => void, (permission: string, write?: boolean) => boolean] {
    const ctx = React.useContext(UniApiContext)

    const getPermission = (permission: string, write: boolean = false) => {
        if (!ctx.user.data) return false
        if (ctx.user.data.root) return true

        const _p = [permission + ".read"]
        if (write) _p.push(permission + ".write")

        return _p.every(p => ctx.user.data?.user_permissions.includes(p))
    }

    if (!ctx.user.data) throw new Error("uni error: user not authenticated")
    return [ctx.user.data, ctx.user.reload, getPermission]
}

/**
 * Custom hook to check if the current user has a specific permission.
 *
 * @param {string} permission - The permission to check for.
 * @param {boolean} [write=false] - Optional flag to check for write permission.
 * @returns {boolean} - Returns true if the user has the specified permission, otherwise false.
 */
export function useUniUserPermission(permission: string, write: boolean = false): boolean {
    const [user, , getPermission] = useUniUser()
    const [hasPerm, setHasPerm] = React.useState(false)

    React.useEffect(() => {
        setHasPerm(getPermission(permission, write))

        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [user])

    return hasPerm
}

export default useUniUser;