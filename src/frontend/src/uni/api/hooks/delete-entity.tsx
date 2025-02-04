import useUniApi from './api';
import useUniTouaster from '../../hooks/toaster';
import { IUniError } from '../common';
import { dispatchUniEvent, UNI_EVENT_ENTITY_DELETED } from '../../events';


/**
 * Custom hook for deleting a entity.
 * 
 * @returns A function that can be used to delete a entity.
 * @param id - The ID of the conversation to be deleted.
 * @param onSuccess - Optional callback function to be executed on successful deletion.
 * @param onError - Optional callback function to be executed on deletion error.
 */
export default function useUniDeleteEntity(endpoint: string, notify: boolean = true): (id: string, onSuccess?: () => void, onError?: (e: IUniError) => void) => void {
    const api = useUniApi()
    const toast = useUniTouaster()

    return (id: string, onSuccess?: () => void, onError?: (e: IUniError) => void) => {
        api.post(`${endpoint}/delete?entity_id=${id}`, {}, (r) => {
            if (notify) toast("deleted", "", "success")
                dispatchUniEvent(UNI_EVENT_ENTITY_DELETED, { endpoint: endpoint, id: id })
            if (onSuccess) onSuccess()
        }, (e) => {
            if(notify) toast("error", e.detail, "error")
            if (onError) onError(e)
        })
    }
}
