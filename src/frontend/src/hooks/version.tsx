import React from 'react';
import { AppContext } from '../context/app';

/**
 * Custom hook to retrieve the current application version from the AppContext.
 *
 * @returns {string} The current version of the application.
 */
export const useAppVersion = () => {
    const app = React.useContext(AppContext)
    return app.version
}