import { getId } from "./utils"

interface UniModelMeta {
    user_id: string
    timestamp: number | null
}

interface UniPermission {
    read: boolean
    write: boolean
}

interface UniModelPermissions {
    group: UniPermission
    all: UniPermission
    other: UniPermission
}

export interface UniDatabaseModel {
    id: string
    created: UniModelMeta
    updated: UniModelMeta
    accessed: UniModelMeta
    owner: string | null
    parent: string | null
    seq: number
    note: string
    permissions?: UniModelPermissions
    joined_collections?: any

}

export interface UniSharingMeta {
    write: boolean
    user_email: string
}

export interface UniWithSharing {
    sharing: UniSharingMeta[]
}

export interface UniUpdateModel {
    id: string
    note?: string
}

export interface UniFile extends UniDatabaseModel {
    filename: string
    original_name: string
    public_link: string
    secret: string
    size: number
    content_type: string
}

export function NewUniDatabaseModel() {
    return {
        id: getId(),
        created: {
            user_id: "",
            timestamp: Date.now()
        },
        updated: {
            user_id: "",
            timestamp: null
        },
        accessed: {
            user_id: "",
            timestamp: null
        },
        owner: null,
        parent: null,
        seq: 0,
        note: "",
        permissions: {
            group: {
                read: true,
                write: true
            },
            all: {
                read: true,
                write: true
            },
            other: {
                read: true,
                write: true
            }
        }
    }
}


export interface UniCreateUserModel {
    id: string
    email: string
    password: string
}