import useUniLocalStorage from "../hooks/local-storage";
import { IUniToast, UniAlertSeverity } from "../common";
import { UNI_TOASTER_CONFIG } from "../components/toaster";

/**
 * Custom hook for displaying toast messages.
 * @returns A function that can be used to display a toast message.
 * @param title - The title of the toast message.
 * @param message - The content of the toast message.
 * @param severity - (Optional) The severity level of the toast message.
 */
export default function useUniTouaster() {
    const [, setMessage] = useUniLocalStorage<IUniToast | null>(UNI_TOASTER_CONFIG.toasterStorageKey, null)

    return (title: string, message: any, severity?: UniAlertSeverity) => {
        if (typeof message === "string") {
            setMessage({ title, message: message as string, severity: severity })
            return
        }

        try {
            const _msg = JSON.stringify(message)
            setMessage({ title, message: _msg, severity: severity })
        } catch (error) {
            const _msg = "Error: Could not stringify message."
            setMessage({ title: "Error", message: _msg, severity: "error" })            
        }

    }
}