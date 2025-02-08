export interface IUniToken {
    token: string;
    expires?: number;
    valid?: boolean;
}

export interface IUniError {
    status: number
    text: string
    detail: any
}

export interface IUniEndpoint {
    create: string;
    update: string;
    update_many: string;
    delete: string;
    get: string;
    count: string;
    count_multiple?: string;
    find: string;
}

export interface IUniFileEndpoint extends IUniEndpoint {
    read: string
}

export interface IUniModelMeta {
    timestamp: number
    user_id: string | null
}

export interface IUniDatabaseModel {
    id: string
    owner?: string | null
    parent?: string | null
    seq?: number
    name?: string
    note?: string
    enabled?: boolean

    created?: IUniModelMeta
    updated?: IUniModelMeta
    accessed?: IUniModelMeta

    joined_collections?: any
}

export interface IUniUser extends IUniDatabaseModel {
    email: string
    first_name: string
    middle_name: string
    last_name: string
    avatar: string
    user_permissions: string[]
    root: boolean
    last_login: number
}

export interface IUniStreamChunk {
    data: string
    timestamp: number
    error: IUniError | null
}

export interface IUniBackgroundTaskInfo {
    id: string
    custom_id: string
    finished: boolean
    exception_type: string
    exception_detail: string
    progress: number
}