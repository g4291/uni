import React from 'react';

import UniButton from '../primitives/button';
import { useUniTranslator } from '../../translator';
import UniIcons from '../../icons';
import UniTooltip from '../primitives/tooltip';
import { IUniError } from '../../api/common';
import UniModalDialog from '../primitives/modal-dialog';
import useUniDeleteEntity from '../../api/hooks/delete-entity';
import { IUniWithChildrenProps, IUniWithColorProps, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps } from '../../common';
import useUniTouaster from '../../hooks/toaster';
import { SxProps } from '@mui/joy/styles/types';


export const UNI_DELETE_ENTITY_WITH_CONFIRM_BUTTON_CONFIG = {
    defaultButtonProps: {
        error: true,
        sx: { }
    }
} as {
    defaultButtonProps: {
        small: boolean,
        error: boolean,
        sx: SxProps
    }
}

export interface IUniDeleteEntityWithConfirmButton extends IUniWithSXProps, IUniWithColorProps, IUniWithSizeProps, IUniWithVariantProps, IUniWithChildrenProps {
    id: string
    endpoint: string
    name: string
    disabled?: boolean
    title?: string
    onSuccess?: () => void
    onError?: (e: IUniError) => void
}
/**
 * DeleteEntityWithConfirmButton component renders a button that, when clicked, 
 * opens a confirmation dialog to delete an entity. It uses the `useUniDeleteEntity` 
 * hook to handle the deletion process and provides success and error callbacks.
 *
 * @param {IUniDeleteEntityWithConfirmButton} props - The properties for the component.
 * @param {string} props.id - The ID of the entity to be deleted.
 * @param {string} props.endpoint - The API endpoint for the delete request.
 * @param {string} props.name - The name of the entity to be deleted.
 * @param {boolean} [props.disabled] - Whether the button is disabled.
 * @param {string} [props.title] - The tooltip title for the button.
 * @param {Function} [props.onSuccess] - Callback function to be called on successful deletion.
 * @param {Function} [props.onError] - Callback function to be called on deletion error.
 * @param {object} [props.sx] - The style object for the button.
 * @param {React.ReactNode} [props.children] - The children elements to be rendered inside the button.
 * @param {object} [props.rest] - Additional properties to be passed to the button.
 *
 * @returns {JSX.Element} The rendered DeleteEntityWithConfirmButton component.
 */
export default function UniDeleteEntityWithConfirmButton(props: IUniDeleteEntityWithConfirmButton): JSX.Element {

    const { id, endpoint, name, disabled, title, onSuccess, onError, children, ...rest } = props

    const t = useUniTranslator()
    const toast = useUniTouaster()
    const [showDialog, setShowDialog] = React.useState<boolean>(false)
    const deleteConversation = useUniDeleteEntity(props.endpoint)

    const confirm = () => {
        deleteConversation(props.id, () => {
            setShowDialog(false)
            if (props.onSuccess) props.onSuccess()
            else toast("success", t("deleted", false), "success")
        }, (e) => {
            setShowDialog(false)
            if (props.onError) props.onError(e)
            else toast("error", e.detail, "error")
        })
    }

    return (<>
        <UniTooltip title={title || t("delete")}>
            <div style={{width: "fit-content"}}>
                <UniButton
                    {...UNI_DELETE_ENTITY_WITH_CONFIRM_BUTTON_CONFIG.defaultButtonProps}
                    disabled={props.disabled}
                    onClick={() => { setShowDialog(true) }}
                    {...rest}
                >
                    {
                        children ? children : <UniIcons.Delete />
                    }
                </UniButton>
            </div>
        </UniTooltip>
        <UniModalDialog
            open={showDialog}
            onClose={() => setShowDialog(false)}
            error
            outlined
            title={t("delete") + " - " + t(props.name, false)} 
            actions={
                <>
                    <UniButton neutral onClick={() => setShowDialog(false)}>{t("cancel")}</UniButton>
                    <UniButton warning onClick={confirm}>{t("delete")}</UniButton>
                </>
            }
        >
            {t("are you sure?")}
        </UniModalDialog>
    </>)
}