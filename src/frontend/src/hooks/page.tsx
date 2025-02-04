import React from 'react';
import { AppContext } from '../context/app';

/**
 * Custom hook to get and set the current page in the application context.
 *
 * @returns {[string, (page: string) => void]} - A tuple containing the current page and a function to set the page.
 */
export function usePage(): [string, (page: string) => void] {

    const app = React.useContext(AppContext)

    const setPage = React.useCallback(
        (page: string) => {
            app.page.set(page)
        }, [app.page]
    )

    return [app.page.data, setPage]
}