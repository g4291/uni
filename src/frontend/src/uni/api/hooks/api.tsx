import React from 'react';
import { IUniError, IUniStreamChunk } from '../common';
import { post_stream, UniApiUtils } from '../utils';
import { UniApiContext } from '../api';


/**
 * Custom hook for accessing the Uni API.
 * @returns An object containing functions for making GET and POST requests to the Uni API, as well as an error handler function.
 */
export function useUniApi() {
    const ctx = React.useContext(UniApiContext)


    const _handleError = (e: any, processId: string | number, onError?: (e: IUniError) => void) => {
        UniApiUtils.uniErrorHandler(e, (e) => {
            if (e.status === 401) ctx.logout()
            if (onError) onError(e)
            ctx.processTracker.endProcess(processId)
        })
    }

    const getWrapper = (endpoint: string, params?: any, onResult?: (r: any) => void, onError?: (e: IUniError) => void) => {
        const processId = ctx.processTracker.startProcess()
        UniApiUtils.get(ctx.serverUrl + endpoint, ctx.token.get() || undefined, params).then(
            (r) => {
                if (onResult) onResult(r)
                ctx.processTracker.endProcess(processId)
            },
            (e) => {
                _handleError(e, processId, onError)
            }
        )
    }

    const postWrapper = (endpoint: string, body: any, onResult?: (r: any) => void, onError?: (e: IUniError) => void, headers?: Headers, blob?: boolean) => {
        const processId = ctx.processTracker.startProcess()
        UniApiUtils.post(ctx.serverUrl + endpoint, body, ctx.token.get() || undefined, headers, blob).then(
            (r) => {
                if (onResult) onResult(r)
                ctx.processTracker.endProcess(processId)
            },
            (e) => {
                _handleError(e, processId, onError)
            },

        )
    }

    const postFileWrapper = (endpoint: string, file: File, onResult?: (r: any) => void, onError?: (e: IUniError) => void) => {
        const processId = ctx.processTracker.startProcess()
        UniApiUtils.post_file(ctx.serverUrl + endpoint, file, ctx.token.get() || undefined).then(
            (r) => {
                if (onResult) onResult(r)
                ctx.processTracker.endProcess(processId)
            },
            (e) => {
                _handleError(e, processId, onError)
            }
        )
    }

    const postStreamWrapper = (endpoint: string, body: any, onData: (data: string) =>void, onDone?: (data: string, duration: string) => void, onError?: (e: IUniError) => void, onChunk?: (chunk: IUniStreamChunk) => boolean) => {
        const processId = ctx.processTracker.startProcess()
        const handler = async () => {
            await post_stream(ctx.serverUrl + endpoint, body, ctx.token.get() || undefined, undefined, onData, (data: string, duration: string) => {
                if (onDone) onDone(data, duration)
                ctx.processTracker.endProcess(processId)
            }, (e: any) => {
                _handleError(e, processId, onError)
            }, (c: IUniStreamChunk) => {
                if (onChunk) {
                    const stop = onChunk(c)
                    if (stop) {
                        ctx.processTracker.endProcess(processId)
                        return true
                    }
                }
                    return false
            })
        }

        handler().then()
    }
    return {
        get: getWrapper,
        post: postWrapper,
        postFile: postFileWrapper,
        postStream: postStreamWrapper,
        errorHandler: UniApiUtils.uniErrorHandler
    }
}

export default useUniApi