import React from 'react';
import { IUniError, } from '../common';
import { IUniLoading, useUniLoading } from '../../hooks/loading';
import useUniTouaster from '../../hooks/toaster';
import { useGoogleLogin } from '@react-oauth/google';
import { UniApiUtils } from '../utils';
import { UniApiContext } from '../api';


/**
 * Custom hook for Uni login.
 * 
 * @returns A tuple containing a login function and a loading state.
 */
export function useUniLogin(notify: boolean = true): [(username: string, password: string, onSuccess?: () => void, onError?: (e: IUniError) => void) => void, IUniLoading] {
    const ctx = React.useContext(UniApiContext)
    const loading = useUniLoading()
    const toast = useUniTouaster()

    const login = (username: string, password: string, onSuccess?: () => void, onError?: (e: IUniError) => void) => {
        loading.on()
        const processId = ctx.processTracker.startProcess()
        UniApiUtils.auth(ctx.serverUrl, username, password).then(
            (t) => {
                ctx.token.set(t)
                if (onSuccess) onSuccess()
                ctx.processTracker.endProcess(processId)
                loading.off()
                if (notify) toast("Success", "login successful", "success")
            }
        ).catch(
            (e) => {
                if (onError) UniApiUtils.uniErrorHandler(e, onError)
                ctx.token.set(null)
                ctx.processTracker.endProcess(processId)
                loading.off()
                if (notify) toast("Error", "login failed", "error")
            }
        )
    }

    return [login, loading]
}

/**
 * Custom hook for performing Google login in the Uni API.
 * 
 * @returns A tuple containing the `googleLogin` function and the `loading` state.
 */
export function useUniGoogleLogin(notify: boolean = true): [(onSuccess?: () => void, onError?: (e: IUniError) => void) => void, IUniLoading] {
    const ctx = React.useContext(UniApiContext)
    const loading = useUniLoading()
    const toast = useUniTouaster()

    if (!ctx.googleClientId) throw new Error("uni error: google client id not set, please provide google client id in UniApiProvider")

    const onSuccessRef = React.useRef<() => void>(() => { })
    const onErrorRef = React.useRef<(e: IUniError) => void>((e) => { })

    // handle google oauth login
    const handleGoogleSuccessLogin = (response: any,) => {
        if (!response.access_token) {
            handleGoogleErrorLogin()
            return
        }

        loading.on();
        const processId = ctx.processTracker.startProcess()
        UniApiUtils.googleOAuth(ctx.serverUrl, response.access_token)
            .then(
                (result) => {
                    ctx.token.set(result)
                    onSuccessRef.current()
                    loading.off()
                    ctx.processTracker.endProcess(processId)
                    if (notify) toast("Success", "google login successful", "success")
                },
                (e) => {
                    UniApiUtils.uniErrorHandler(e, onErrorRef.current)
                    ctx.token.set(null)
                    loading.off()
                    ctx.processTracker.endProcess(processId)
                    if (notify) toast("Error", "google login failed", "error")
                }
            );
    }

    // handle google oauth login error
    const handleGoogleErrorLogin = () => {
        onErrorRef.current({ status: -1, text: "Error", detail: "unable to login with Google" })
        ctx.token.set(null)
        loading.off()
        
        if (notify) toast("Error", "google login failed", "error")
    }


    const googleLogin = useGoogleLogin({
        onSuccess: handleGoogleSuccessLogin,
        onError: handleGoogleErrorLogin
    })

    return [(onSuccess?: () => void, onError?: (e: IUniError) => void) => {
        onSuccessRef.current = onSuccess || (() => { })
        onErrorRef.current = onError || ((e) => { })
        googleLogin()
    }, loading]

}

export const UniLogin = {
    useUniLogin,
    useUniGoogleLogin
}

export default UniLogin