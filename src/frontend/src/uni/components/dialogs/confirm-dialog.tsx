import React from 'react';

import UniButton from '../primitives/button';
import { useUniTranslator } from '../../translator';
import UniModalDialog from '../primitives/modal-dialog';
import { IUniWithColorProps, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps } from '../../common';
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

export interface IUniConfirmDialogProps extends IUniWithSXProps, IUniWithColorProps, IUniWithSizeProps, IUniWithVariantProps {
    title: string
    text: string
    show: boolean
    onConfirm: () => void
    onCancel: () => void
}


/**
 * UniConfirmDialog component renders a confirmation dialog with customizable title, text, and actions.
 * It uses the UniModalDialog component to display the dialog and UniButton components for the actions.
 * The dialog is translated using the useUniTranslator hook.
 *
 * @param {IUniConfirmDialogProps} props - The properties for the UniConfirmDialog component.
 * @param {string} props.title - The title of the dialog.
 * @param {() => void} props.onConfirm - The callback function to be called when the confirm button is clicked.
 * @param {() => void} props.onCancel - The callback function to be called when the cancel button is clicked.
 * @param {boolean} props.show - A boolean indicating whether the dialog should be shown.
 * @param {string} props.text - The text content of the dialog.
 * @param {object} [props.rest] - Additional properties to be passed to the UniModalDialog component.
 *
 * @returns {JSX.Element} The rendered UniConfirmDialog component.
 */
export default function UniConfirmDialog(props: IUniConfirmDialogProps): JSX.Element {
    const { title, onConfirm, onCancel, show, text, ...rest } = props    
    const t = useUniTranslator()

    return (<>
        <UniModalDialog
            open={show}
            outlined
            title={t(title)}
            actions={
                <>
                    <UniButton {...rest} neutral onClick={
                        () => {
                            onCancel()
                        }
                    }>{t("cancel")}</UniButton>
                    <UniButton {...rest} onClick={
                        () => {
                            onConfirm()
                        }
                    }>{t("confirm")}</UniButton>
                </>
            }
            {...rest}
        >
            {t(text)}
        </UniModalDialog>
    </>)
}