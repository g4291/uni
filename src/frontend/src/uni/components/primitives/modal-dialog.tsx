import React from "react";
import { SxProps } from "@mui/joy/styles/types";
import { DialogActions, DialogContent, DialogTitle, Modal, ModalClose, ModalDialog } from "@mui/joy";

import { getUniColor, getUniVariant, IUniWithBorderProps, IUniWithChildrenProps, IUniWithColorProps, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps, UniColorProp, UniComponentSize, UniComponentSpacing, UniVariantProp } from "../../common";


// ModalDialog config
const UNI_MODAL_DIALOG_CONFIG = {
    defaultSpacing: 1,
    defaultModalDialogContentSx: {
        p: 0,
        scrollbarWidth: "thin"
    },
    defaultModalDialogTitleSx: {

    },
    defaultSize: undefined,
    defaultVariant: "plain",
    defaultColor: "neutral"
} as {
    defaultSpacing: UniComponentSpacing,
    defaultModalDialogContentSx: SxProps,
    defaultModalDialogTitleSx: SxProps,
    defaultSize: UniComponentSize,
    defaultVariant: UniVariantProp,
    defaultColor: UniColorProp
}

export interface IModalDialogProps extends IUniWithChildrenProps, IUniWithSXProps, IUniWithBorderProps, IUniWithSizeProps, IUniWithVariantProps, IUniWithColorProps {
    actions?: React.ReactNode
    open: boolean
    onClose?: () => any

    title?: React.ReactNode
    titleSx?: SxProps
    bodySx?: SxProps

    close?: boolean
    fullscreen?: boolean
}


/**
 * Base UniModalDialog component
 * 
 * @param props IBaseUniModalDialogProps
 * @returns JSX.Element
 */
function UniModalDialog(props: IModalDialogProps): JSX.Element {

    const size = props.small ? "sm" : props.large ? "lg" : undefined;
    const variant = React.useMemo(() => getUniVariant(props, UNI_MODAL_DIALOG_CONFIG.defaultVariant), [props])
    const color = React.useMemo(() => getUniColor(props, UNI_MODAL_DIALOG_CONFIG.defaultColor), [props])

    const titleSx = { ...UNI_MODAL_DIALOG_CONFIG.defaultModalDialogContentSx, ...props.titleSx } as SxProps
    return (
        <Modal
            open={props.open}
            onClose={() => {
                if (props.onClose) props.onClose()
            }}
        >
            <ModalDialog sx={props.bodySx} color={color} variant={variant} size={size} layout={props.fullscreen ? "fullscreen" : "center"}>
                {props.close && <ModalClose />}
                {props.title ? <DialogTitle sx={titleSx}>{props.title}</DialogTitle> : props.close && <DialogTitle sx={titleSx}>&nbsp;</DialogTitle>}
                <DialogContent sx={{ ...UNI_MODAL_DIALOG_CONFIG.defaultModalDialogContentSx, ...props.sx } as SxProps}>
                    {props.children}
                </DialogContent>
                {props.actions && <DialogActions>
                    {props.actions}
                </DialogActions>}
            </ModalDialog>
        </Modal>
    )
}


export default UniModalDialog