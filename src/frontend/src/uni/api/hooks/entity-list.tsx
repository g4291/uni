import React from "react";

import useUniApi from "./api";
import { useUniLoading } from "../../hooks/loading";
import useUniTouaster from "../../hooks/toaster";


export interface UniSort {
    key: string
    order: 0 | 1
}

export interface UniFindQuery {
    sort_key?: string
    sort_order?: 0 | 1
    limit_from?: number
    limit_to?: number
    filters?: any[]
    join?: string[][]
    fetch_dict?: boolean
}

export interface IUniFindResult<T> {
    count: number
    data: T[]
    loading: boolean
    reload: () => any
}

/**
 * Custom hook to fetch and manage a list of entities from a given endpoint.
 *
 * @template T - The type of the entities in the list.
 * @param {string} endpoint - The API endpoint to fetch the entities from.
 * @param {UniFindQuery | null} query - The query parameters for fetching the entities.
 * @param {boolean} [noEmptyQuery=false] - If true, prevents fetching data if the query has no filters.
 * @param {boolean} [init=true] - If false, prevents the initial fetch on mount.
 * @returns {IUniFindResult<T>} An object containing the fetched data, count, loading state, and a reload function.
 */
export default function useUniEntityList<T>(endpoint: string, query: UniFindQuery | null, noEmptyQuery: boolean = false, init: boolean = true): IUniFindResult<T> {

    const api = useUniApi()
    const loading = useUniLoading()
    const toast = useUniTouaster()

    const [data, setData] = React.useState<T[]>([])
    const [count, setCount] = React.useState(0)
    const initRef = React.useRef<boolean>(false)


    const onErrorClear = React.useCallback(
        () => {
            setData([])
            setCount(0)
            loading.off()
        }, [loading]
    )

    const getData = React.useCallback(
        () => {
            loading.on()
            api.post(endpoint+"/find", {...query}, 
                (r: T[]) => {
                    setData(r)
                    loading.off()
                },
                (e: any) => {
                    toast("error", e.detail, "error")
                    onErrorClear()
                }
            )
        }, [query, onErrorClear, api, toast, loading, endpoint]
    )

    const load = React.useCallback(
        () => {
            loading.on()
            api.post(endpoint+"/count", {...query}, 
                (r: number) => {
                    setCount(r)
                    if (r > 0) {
                        getData()
                    } else {
                        setData([])
                    }
                    loading.off()
                },
                (e: any) => {
                    toast("error", e.detail, "error")
                    onErrorClear()
                }
            )
        }, [query, onErrorClear, api, toast, loading, getData, endpoint]
    )

    React.useEffect(() => {
        if (noEmptyQuery) {
            if (query?.filters && query.filters.length === 0) {
                return
            }
        }
        if (!init && !initRef.current) {
            initRef.current = true
            return
        }
        load()

        // eslint-disable-next-line
    }, [query])

    React.useEffect(() => {
        
        return () => {
            loading.off()
            onErrorClear()
        }

        // eslint-disable-next-line
    }, [])

    return {
        count,
        data,
        loading: loading.loading,
        reload: load, 
    }
}