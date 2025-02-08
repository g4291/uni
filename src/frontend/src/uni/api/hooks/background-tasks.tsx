import React from 'react';
import { IUniBackgroundTaskInfo } from '../common';
import { UniApiContext } from '../api';


/**
 * Custom hook to access and manage background tasks in the Uni API context.
 *
 * @returns {[IUniBackgroundTaskInfo[], () => void]} An array containing the list of background tasks and a function to reload the tasks.
 */
export function useUniBackgroundTasks(): [IUniBackgroundTaskInfo[], () => void] {

    const ctx = React.useContext(UniApiContext)

    return [ctx.backgroundTasks.data, ctx.backgroundTasks.reload]
}

export default useUniBackgroundTasks;