import React from "react";

import useUniApi from "./api";
import { useUniLoading } from "../../hooks/loading";
import useUniTouaster from "../../hooks/toaster";
import { uniEndpoints } from "../utils";
import { IKVStoreEntity } from "../../datamodel";


/**
 * Custom hook for interacting with a key-value store.
 *
 * @param key - The key to access the value in the store.
 * @param defaultValue - The default value to use if the key does not exist in the store.
 * @returns An array containing the current value, a function to set the value, and a function to delete the value.
 */
export function useKVStore<T>(key: string, defaultValue: T | null): [T | null, (value: T | null) => void, () => void] {
    const api = useUniApi()
    const toast = useUniTouaster()

    const [value, setValue] = React.useState(defaultValue)

    React.useEffect(() => {
        handleGet()

        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    const handleGet = () => {
        api.post(
            uniEndpoints.kvStore.get + `?key=${key}`,
            {},
            (r: IKVStoreEntity<T>) => {
                setValue(r.value)
            },
            (e) => {
                toast("error", "Failed to get value from KV store", "error")
            })
    }

    const handleSet = (value: any) => {
        api.post(
            uniEndpoints.kvStore.set,
            { key: key, value: value },
            (r: T | null) => {
                setValue(value)
            },
            (e) => {
                toast("error", "Failed to set value in KV store", "error")
            })
    }

    const handleDelete = () => {        
        api.post(
            uniEndpoints.kvStore.delete + `?key=${key}`,
            {},
            (r: any) => {
                setValue(null)
            },
            (e) => {
                toast("error", "Failed to delete value from KV store", "error")
            })
    }


    return [value, handleSet, handleDelete]
}

export default useKVStore;