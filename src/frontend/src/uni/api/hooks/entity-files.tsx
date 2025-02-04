import React from "react";

import useUniApi from "./api";
import { useUniLoading } from "../../hooks/loading";
import useUniTouaster from "../../hooks/toaster";
import { UniFile } from "../../datamodel";
import { queryFindByArray } from "../../utils";
import { UniFindQuery } from "./entity-list";


export default function useUniEntityFiles(entity: any, field: string): UniFile[] {

    const api = useUniApi()
    const loading = useUniLoading()
    const toast = useUniTouaster()

    const [data, setData] = React.useState<UniFile[]>([])
    const [query, setQuery] = React.useState<UniFindQuery | null>(null)

    const onErrorClear = React.useCallback(
        () => {
            setData([])
            loading.off()
        }, [loading]
    )

    const load = React.useCallback(
        () => {
            loading.on()
            if (!query) {
                setData([])
                return
            }
            api.post("/file/find", {...query}, 
                (r: UniFile[]) => {
                    setData(r)
                    loading.off()
                },
                (e: any) => {
                    toast("error", e.detail, "error")
                    onErrorClear()
                }
            )
        }, [query, onErrorClear, api, toast, loading]
    )

    React.useEffect(() => {
        if (!entity || !entity[field]) {
            setQuery(null)
            return
        }
        
        const q = queryFindByArray(entity[field])
        if (q.length === 0) {
            setQuery(null)
            return
        }
        setQuery({
            filters: q
        })

    }, [entity, field])

    React.useEffect(() => {
        load()

        // eslint-disable-next-line
    }, [query])

    return data
}