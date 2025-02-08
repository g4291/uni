import React from 'react';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { LinearProgress } from '@mui/joy';

import { IUniWithChildrenProps } from '../common';
import useUniLocalStorage from '../hooks/local-storage';
import { IUniBackgroundTaskInfo, IUniToken, IUniUser } from './common';
import useProcessTracker, { IUniProcessTracker } from './hooks/processes';
import UniFade from '../components/animations/fade';
import { UniApiUtils } from './utils';

// config
export const UNI_API_CONFIG = {
    tokenStorageKey: "uni.token",
    defaultRequireAuth: false,
    loaderZIndex: 1000,
    showLoader: true

} as {
    tokenStorageKey: string,
    defaultRequireAuth: boolean,
    loaderZIndex: number,
    showLoader: boolean
}

// Context
export interface IUniApiContext {
    token: {
        get: () => IUniToken | null,
        set: (token: IUniToken | null) => void
    },
    serverUrl: string
    logout: () => void
    user: {
        data: IUniUser | null
        reload: () => void
    }
    googleClientId?: string
    processTracker: IUniProcessTracker
    backgroundTasks: {
        data: IUniBackgroundTaskInfo[]
        reload: () => void
    }

}
export const UniApiContext = React.createContext<IUniApiContext>({} as IUniApiContext);

// Provider
export interface IUniApiProviderProps extends IUniWithChildrenProps {
    serverUrl: string
    noAuthComponent?: React.ReactNode
    googleClientId?: string
}

function UniApiProvider(props: IUniApiProviderProps) {
    const [token, setToken] = useUniLocalStorage<IUniToken | null>(UNI_API_CONFIG.tokenStorageKey, null);
    const [serverUrl] = React.useState(props.serverUrl);
    const [user, setUser] = React.useState<IUniUser | null>(null)
    const processTracker = useProcessTracker()
    const [backgroundTasks, setBackgroundTasks] = React.useState<IUniBackgroundTaskInfo[]>([])

    const logout = () => {
        setToken(null)
        setUser(null)
    }

    const reloadBackgroundTasks = () => {
        if(token) {
            // const processId = processTracker.startProcess()
            UniApiUtils.post(serverUrl+"/background_tasks/get_all", {}, token).then(
                (r: IUniBackgroundTaskInfo[]) => {
                    setBackgroundTasks(r)
                    // processTracker.endProcess(processId)
                },
                (e) => {
                    UniApiUtils.uniErrorHandler(e, (e) => {
                        console.log("bg task error", e)
                    })
                }
            )
            return
        }
        setBackgroundTasks([])
    }

    const reloadUser = () => {
        if (token) {
            const processId = processTracker.startProcess()
            UniApiUtils.get_user(serverUrl, token).then(
                (r: IUniUser) => {
                    setUser(r)
                    processTracker.endProcess(processId)
                },
                (e) => {
                    UniApiUtils.uniErrorHandler(e, (e) => {
                        setToken(null)
                        processTracker.endProcess(processId)
                    })
                }
            )
            return
        }
        setUser(null)
    }

    React.useEffect(() => {
        reloadUser()
        reloadBackgroundTasks()

        // eslint-disable-next-line
    }, [token])


    const showChild = React.useMemo(() => {
        if (!token) return false
        if (!user) return false

        return true
    }, [token, user])


    const element = <>
        <UniFade show={processTracker.isRunning && UNI_API_CONFIG.showLoader}>
            <LinearProgress variant='soft' sx={{ position: "absolute", top: 0, left: 0, zIndex: UNI_API_CONFIG.loaderZIndex, width: "100%" }} />
        </UniFade>
        <UniApiContext.Provider value={{
            token: {
                get: () => token,
                set: setToken
            },
            serverUrl: serverUrl,
            logout: logout,
            user: {
                data: user,
                reload: reloadUser
            },
            googleClientId: props.googleClientId,
            processTracker: processTracker,
            backgroundTasks: {
                data: backgroundTasks,
                reload: reloadBackgroundTasks
            }
        }}>
            {showChild ? props.children : (props.noAuthComponent ? props.noAuthComponent : "unauthorized")}
        </UniApiContext.Provider>
    </>

    if (props.googleClientId)
        return <GoogleOAuthProvider clientId={props.googleClientId}>{element}</GoogleOAuthProvider>

    return element

}

// export module
export const UniApi = {
    config: UNI_API_CONFIG,
    ctx: UniApiContext,
    Provider: UniApiProvider,
}


export default UniApi