import React from "react"
import { useTheme } from "@mui/joy"
import { UniBreakPoint } from "../common"


/**
 * Custom hook that returns the current breakpoint based on the window width.
 * @returns The current breakpoint as a string.
 */
export function useUniBreakPoint(): UniBreakPoint {
    const theme = useTheme()
    const values = theme.breakpoints.values
    const [bp, setBp] = React.useState<UniBreakPoint>("xl")
    
    const handleResize = () => {
        const width = window.innerWidth
        if (width > values.xl) return setBp("xl")
        if (width > values.lg) return setBp("lg")
        if (width > values.md) return setBp("md")
        if (width > values.sm) return setBp("sm")
        setBp("xs")
    }

    // Fix for ResizeObserver loop completed with undelivered notifications
    React.useEffect(() => {
        function hideError(e: any) {
            if (e.message === 'ResizeObserver loop completed with undelivered notifications.') {
                const resizeObserverErrDiv = document.getElementById(
                    'webpack-dev-server-client-overlay-div'
                );
                const resizeObserverErr = document.getElementById(
                    'webpack-dev-server-client-overlay'
                );
                if (resizeObserverErr) {
                    resizeObserverErr.setAttribute('style', 'display: none');
                }
                if (resizeObserverErrDiv) {
                    resizeObserverErrDiv.setAttribute('style', 'display: none');
                }
            }
        }
    
        window.addEventListener('error', hideError)
        return () => {
            window.addEventListener('error', hideError)
        }
    }, [])

    React.useEffect(() => {
        handleResize()
        window.addEventListener("resize", handleResize)
        return () => window.removeEventListener("resize", handleResize)

        // eslint-disable-next-line
    }, [])

    return bp
}

export default useUniBreakPoint