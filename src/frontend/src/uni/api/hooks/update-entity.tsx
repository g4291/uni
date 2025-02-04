import useUniApi from './api';
import useUniTouaster from '../../hooks/toaster';
import { IUniError } from '../common';


/**
 * Custom hook for updating an entity.
 * 
 * @template T - The type of the entity.
 * @param {string} endpoint - The endpoint for the update request.
 * @param {boolean} [notifyError=true] - Flag indicating whether to notify errors.
 * @returns {(entity: T, onSuccess?: () => void, onError?: (e: IUniError) => void) => void} - The update function.
 */
export default function useUniUpdateEntity<T>(endpoint: string, notifyError: boolean = true): (entity: T, onSuccess?: () => void, onError?: (e: IUniError) => void) => void {
    const api = useUniApi()
    const toast = useUniTouaster()

    return (entity: T, onSuccess?: () => void, onError?: (e: IUniError) => void) => {
        api.post(`${endpoint}/update`, {...entity}, () => {
            if (onSuccess) onSuccess()
        }, (e) => {
            if(notifyError) toast("error", e.detail, "error")
            if (onError) onError(e)
        })
    }
}
