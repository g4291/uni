import useUniApi from './api';
import useUniTouaster from '../../hooks/toaster';
import { IUniError } from '../common';


/**
 * Custom hook for getting an entity from the API.
 * 
 * @param endpoint - The API endpoint for getting the entity.
 * @param notifyError - Optional flag to indicate whether to notify errors. Default is true.
 * @returns A function that takes an entity ID and optional success and error callbacks.
 */
export default function useUniGetEntity<T>(endpoint: string, notifyError: boolean = true): (id: string, onSuccess?: (entity: T) => void, onError?: (e: IUniError) => void) => void {
    const api = useUniApi()
    const toast = useUniTouaster()

    return (id: string, onSuccess?: (entity: T) => void, onError?: (e: IUniError) => void) => {
        api.post(`${endpoint}/get?entity_id=${id}`, {}, (r: T) => {
            if (onSuccess) onSuccess(r)
        }, (e) => {
            if(notifyError) toast("error", e.detail, "error")
            if (onError) onError(e)
        })
    }
}
