import React from 'react';
import { IUniWithChildrenProps } from '../uni/common';
import useUniEntityList from '../uni/api/hooks/entity-list';
import { IUniUser } from '../uni/api/common';


export interface IAppContext {
    version: string
    page: {
        data: string
        get: () => string
        set: (page: string) => void
    }
    users: {
        data: IUniUser[]
        get: () => IUniUser[]
        get_user_by_id: (id: string) => IUniUser
        reload: () => void
    }
}

export const AppContext = React.createContext<IAppContext>({} as IAppContext);

interface IAppProviderProps extends IUniWithChildrenProps {
}
export function AppProvider(props: IAppProviderProps) {
    const [version, setVersion] = React.useState("")  // TODO: get version from backend
    const [page, setPage] = React.useState<string>("")
    const users = useUniEntityList<IUniUser>("/user", null)

    return (
        <AppContext.Provider value={{
            version,
            page: {
                data: page,
                get: () => page,
                set: (page: string) => {
                    setPage(page)
                }
            },
            users: {
                data: users.data,
                get: () => users.data,
                get_user_by_id: (id: string) => {
                    return users.data.find((u) => u.id === id) as IUniUser
                },
                reload: users.reload
            }
        }}>
            {props.children}
        </AppContext.Provider>
    )
}

export function useUniUsers(): {data: IUniUser[], get: () => IUniUser[], get_user_by_id: (id: string) => IUniUser, reload: () => void} {
    const context = React.useContext(AppContext)
    return context.users
}