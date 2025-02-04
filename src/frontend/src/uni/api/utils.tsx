import { timeDuration } from '../../utils';
import { IUniError, IUniStreamChunk, IUniToken } from './common';

interface IError {
    status: number;
    statusText: string;
    json(): Promise<any>;
    detail?: string;
    text?: string;
}

const uniEndpoints = {
    auth: "/auth",
    googleOAuth: "/google_oauth",
    authWithRoot: "/auth_with_root",
    user: {
        get_self: "/user/get_self",
    }
}

/**
 * Performs a GET request to the specified URL.
 * 
 * @param url - The URL to send the GET request to.
 * @param token - Optional token object to include in the request headers.
 * @param headers - Optional headers object to include in the request.
 * @returns A Promise that resolves to the response of the GET request.
 */
function _get(url: string, token?: IUniToken, headers?: Headers) {
    // headers, token
    if (!headers) headers = new Headers()
    if (token) headers.set("token", token.token)

    return fetch(url, {
        headers: headers,
        method: "GET"
    })
}

/**
 * send request to UNI-B,
 * returns response as promise
 * 
 * @param {string} endpoint server endpoint
 * @param {string} token 
 * @param {object} params get parameters
 * @param {function} progress_start process start callback
 * @param {function} progress_end process end callback
 * @returns result
 */
export function get(endpoint: string, token?: IUniToken, params?: any) {
    // handle params
    var _params = "";
    if (params) {
        _params += "?";
        var first = false;
        for (let p in params) {
            if (!first) _params += "&";

            _params += p + "=" + params[p]
        }
    }

    return _get(endpoint + encodeURI(_params), token)
        .then(
            (r) => {
                if (!r.ok) throw r
                return r.json()
            }
        )
}


/**
 * private, send HTTP request
 * 
 * @param {string} url endpoint url
 * @param {object} body request body
 * @param {string} token 
 * @param {object} headers headers
 * @returns 
 */
export async function post_stream(url: string, body: any, token?: IUniToken, headers?: Headers, onData?: (data: string) => void, onDone?: (data: string, duration: string) => void, onError?: (error: any) => void, onChunk?: (chunk: IUniStreamChunk) => boolean) {
    // headers, token
    if (!headers) headers = new Headers()
    if (token) headers.set("token", token.token)
    headers.set("Content-type", "application/json")

    try {
        const startTime = new Date();
        const response = await fetch(url, {
            headers: headers,
            method: "POST",
            body: JSON.stringify(body),
            mode: "cors"
        })

        if (!response.ok) {
            if (onError) onError(response)
            else console.error(response)
            return
        }

        const reader = response.body?.getReader()
        if (!reader) {
            if (onError) onError(response)
            else console.error(response)
            return
        }

        const decoder = new TextDecoder()
        let result = ''
        let done = false
        let rest = ""
        while (!done) {
            const chunk = await reader.read()
            done = chunk.done
            if (chunk.value) {
                // fix json stream, chunks are not separated by comma, add [] to make it valid json
                const raw = rest + decoder.decode(chunk.value, { stream: true }).replace(/\}\{/g, "}, {")
                rest = ""
                const splitted = raw.split("}, {")
                
                const last = splitted[splitted.length - 1]
                if (!last.endsWith("}")) {
                    rest += last
                    splitted.pop()
                }

                // parse json stream
                const toEncode = splitted.join("}, {")
                const streamChunk: IUniStreamChunk[] = JSON.parse("["+toEncode+"]")

                for (let c of streamChunk) {
                    // handle error
                    if (c.error) {
                        if (onError) onError(c.error)
                        return
                    }

                    // on data
                    result += c.data
                    if (onData) onData(result)

                    // on chunk
                    if(onChunk) {
                        const stop = onChunk(c)
                        if (stop) {
                            return
                        }
                    }
                }
            }
        }
        if (onDone) onDone(result, timeDuration(startTime, new Date()))
    } catch (error) {
        console.error("catched", error)
        if (onError) onError(error)
    }
}

export async function get_stream(url: string, token?: IUniToken, headers?: Headers, onData?: (data: any) => void, onDone?: (data: string) => void, onError?: (error: any) => void) {
    if (!headers) headers = new Headers()
    if (token) headers.set("token", token.token)

    try {
        const response = await fetch(url, {
            headers: headers,
            method: "GET"
        })

        if (!response.ok) {
            if (onError) onError(response)
            else console.error(response)
            return
        }

        const reader = response.body?.getReader()
        if (!reader) {
            if (onError) onError(response)
            else console.error(response)
            return
        }

        const decoder = new TextDecoder()
        let result = ''
        let done = false
        while (!done) {
            const chunk = await reader.read()
            done = chunk.done
            if (chunk.value) {
                const decoded = decoder.decode(chunk.value, { stream: true })
                result += decoded
                if (onData) onData(decoded)
            }
        }
        if (onDone) onDone(result)
    } catch (error) {
        if (onError) onError(error)
    }
}

/**
 * private, send HTTP request
 * 
 * @param {string} url endpoint url
 * @param {object} body request body
 * @param {string} token 
 * @param {object} headers headers
 * @returns 
 */
function _post(url: string, body: any, token?: IUniToken, headers?: Headers) {
    // headers, token
    if (!headers) headers = new Headers()
    if (token) headers.set("token", token.token)
    headers.set("Content-type", "application/json")


    return fetch(url, {
        headers: headers,
        method: "POST",
        body: JSON.stringify(body),
        mode: "cors"
    })
}

/**
 * 
 * @param {string} endpoint server endpoint
 * @param {string} token 
 * @param {object} body request body
 * @param {function} progress_start process start callback
 * @param {function} progress_end process end callback
 */
function post(endpoint: string, body: any, token?: IUniToken, headers?: Headers, blob?: boolean) {

    return _post(endpoint, body, token, headers)
        .then(
            (r) => {
                if (!r.ok) throw r
                if (blob) return r.blob()
                return r.json()
            }
        )
}

/**
 * private, send HTTP request
 * 
 * @param {string} url endpoint url
 * @param {object} body request body
 * @param {string} token 
 * @param {object} headers headers
 */
function _post_file(url: string, file: File, token?: IUniToken, headers?: Headers) {
    // headers, token
    if (!headers) headers = new Headers()
    if (token) headers.set("token", token.token)
    headers.set("Accept", "application/json")
    const data = new FormData()
    data.append("f", file)


    return fetch(url, {
        headers: headers,
        method: "POST",
        body: data,
        mode: "cors"
    })
}

/**
 * 
 * @param {string} endpoint server endpoint
 * @param {string} token 
 * @param {object} file request body
 * @param {function} progress_start process start callback
 * @param {function} progress_end process end callback
 * @returns 
 */
function post_file(endpoint: string, file: File, token?: IUniToken) {
    return _post_file(endpoint, file, token)
        .then(
            (r) => {
                if (!r.ok) throw r
                return r.json()
            }
        )
}

/**
 * get authentication token
 * 
 * @param {string} username 
 * @param {string} password 
 * @returns user token
 */
function auth(serverUrl: string, username: string, password: string) {
    const headers: Headers = new Headers();
    headers.set('Authorization', 'Basic ' + btoa(username + ":" + password));

    return _get(serverUrl + uniEndpoints.auth, undefined, headers).then(
        (r) => {
            if (!r.ok) throw r  // on error
            return r.json()  // on success
        }
    );
}

/**
 * get authentication token with google
 * 
 * @param googleToken google token
 * @returns user token
 */
function googleOAuth(serverUrl: string, googleToken: string) {
    return post(serverUrl + uniEndpoints.googleOAuth, { token: googleToken })
}

/**
 * get authentication token with root user
 * 
 * @param userId userId
 * @returns user token
 */
function authWithRoot(serverUrl: string, userId: string) {
    return post(serverUrl + uniEndpoints.authWithRoot, { user_id: userId })
}

/**
 * 
 * @param {object} token auth token
 * @returns logged user
 */
function get_user(serverUrl: string, token?: IUniToken) {

    return _get(serverUrl + uniEndpoints.user.get_self, token)
        .then(
            (r) => {
                if (!r.ok) throw r  // on error
                return r.json()  // on success
            }
        )
}

/**
 * http error handler,
 * lifts error with callback
 * 
 * @param {any} error http error
 * @param {function} callback error callback
 */
function uniErrorHandler(error: IError, callback: (error: IUniError) => any) {
    try {
        if (error?.detail)
        {
            callback(
                {
                    status: error.status,
                    text: error.text || error.statusText,
                    detail: error.detail
                }
            )
            return
        }

        error.json().then(
            (e) => {
                callback(
                    {
                        status: error.status,
                        text: error.statusText,
                        detail: e.detail
                    }
                )
            }
        )
        // server error, cors, ...
    } catch (_error) {
        callback(
            {
                status: 500,
                text: "error",
                detail: "unknown server error"
            }
        )
    }
}


export const UniApiUtils = {
    get: get,
    post: post,
    post_file: post_file,
    auth: auth,
    googleOAuth: googleOAuth,
    authWithRoot: authWithRoot,
    get_user: get_user,
    uniErrorHandler: uniErrorHandler
}