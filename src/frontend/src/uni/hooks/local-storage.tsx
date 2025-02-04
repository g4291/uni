import { useState } from "react";

import useEventListener from "./event-listener";
import { dispatchUniEvent, UniEventTypes } from "../events";


const get = (key: string) => {
    const item = localStorage.getItem(key)
    if(item !== null) return JSON.parse(item);
    return null;
}

const set = (key: string, value: any) => {
    const item = JSON.stringify(value)
    localStorage.setItem(key, item)
}

const del = (key: string) => {
    const item = localStorage.getItem(key)
    if(item !== null) localStorage.removeItem(key); 
    return null;
}

export function useUniLocalStorage<T>(key: string, defaultValue: T|null): [T, (value: T) => void, ()=>void] {
    const getData = () => {
        const d = get(key) 
        if (d !== null) return d;
        return defaultValue;
    }
    const [data, setData] = useState(getData());

    const updateData = (value: T) => {
        // update in local storage
        set(key, value)

        // publish event
        dispatchUniEvent(UniEventTypes.localStorage.update, {key: key, value: value})

    }

    const delData = () => {
        // delete from local storage
        del(key)

        // publish event
        dispatchUniEvent(UniEventTypes.localStorage.delete, {key: key})
    }

    const eventListener = (e: any) => {
        if(e.detail.key === key) {
            if (e.type === UniEventTypes.localStorage.update) setData(e.detail.value);
            else if(e.type === UniEventTypes.localStorage.delete) setData(defaultValue)
        }
    }

    // add event listeners
    useEventListener(UniEventTypes.localStorage.update, eventListener);
    useEventListener(UniEventTypes.localStorage.delete, eventListener);

    return [data, updateData, delData]
}

export default useUniLocalStorage;