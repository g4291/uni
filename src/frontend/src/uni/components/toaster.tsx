import React, { useCallback, useMemo } from "react";
import { Snackbar, SnackbarOrigin } from "@mui/joy";
import { SxProps } from "@mui/joy/styles/types";

import { getUniVariant, IUniToast, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps, UniAlertSeverity, UniVariantProp } from "../common";
import UniButton from "./primitives/button";
import useUniLocalStorage from "../hooks/local-storage";
import { UniTypography as UT } from "./primitives/typography";
import UniStack from "./primitives/stack";
import { CloseOutlined } from "@mui/icons-material";
import { useUniTranslator } from "../translator";
import UniIcons from "../icons";


export const UNI_TOASTER_CONFIG = {
    defaultSx: {
        maxWidth: "400px",
        alignItems: "flex-start",
        // boxShadow: "0px 0px 10px rgba(0,0,0,0.2)"
    },
    defaultVariant: "outlined",
    defaultSeverity: "info",
    toasterStorageKey: "uni.toaster.message",
    defaultDuration: 6000



} as {
    defaultSx: SxProps,
    defaultVariant: UniVariantProp
    defaultSeverity: UniAlertSeverity
    toasterStorageKey: string
    defaultDuration: number
}

interface IUniToasterProps extends IUniWithSXProps, IUniWithVariantProps, IUniWithSizeProps {
    duration?: number
    anchorOrigin?: SnackbarOrigin
}

/**
 * Renders a toaster component.
 *
 * @param props - The component props.
 * @returns The rendered toaster component.
 */
export default function UniToaster(props: IUniToasterProps): JSX.Element {
    const [open, setOpen] = React.useState(false);
    const [message, , clearMessage] = useUniLocalStorage<IUniToast | null>(UNI_TOASTER_CONFIG.toasterStorageKey, null)
    const t = useUniTranslator()

    
    // clear message
    const clear = useCallback(() => {
        clearMessage()
        setOpen(false)
        
    }, [clearMessage, setOpen])
    
    // clear on mount
    React.useEffect(() => {
        clear()

        // eslint-disable-next-line
    }, [])
    
    // effect, on new message
    React.useEffect(() => {
        if (message) {
            setOpen(true)
        }

        // set timeout to clear message
        const timeout = setTimeout(() => {
            clear()
        }, props.duration || UNI_TOASTER_CONFIG.defaultDuration)

        // clear timeout on new message an unmount
        return () => clearTimeout(timeout)

        // eslint-disable-next-line
    }, [message])


    // severity
    const severity = message?.severity || UNI_TOASTER_CONFIG.defaultSeverity
    const color = useMemo(() => {
        if (severity === "error") return "danger"
        else if (severity === "warning") return "warning"
        else if (severity === "success") return "success"
        else if (severity === "info") return "primary"
        return "primary"
    }, [severity])

    // decorators
    const startDecorator = useMemo(() => {
        if (severity === "error") return <UniIcons.Error />
        else if (severity === "warning") return <UniIcons.Warning />
        else if (severity === "success") return <UniIcons.Success />
        return undefined
    }, [severity])
    const endDecorator = <UniButton onClick={clear} small plain neutral><CloseOutlined /></UniButton>

    // variant
    const variant = React.useMemo(() => getUniVariant(props, UNI_TOASTER_CONFIG.defaultVariant), [props])

    // nothing to show
    if (!message) return <></>

    // render
    return (
        <>
            <Snackbar
                sx={{ ...UNI_TOASTER_CONFIG.defaultSx, ...props.sx } as SxProps}
                open={open}
                startDecorator={startDecorator}
                endDecorator={endDecorator}
                variant={variant}
                color={color}
                anchorOrigin={props.anchorOrigin}
                onClose={(e, reason) => {
                    // if (reason === "clickaway" || reason === "escapeKeyDown") return
                    clear()
                }}>
                <UniStack.Column spacing={0}>
                    {message?.title !== "" && <UT.Title >{t(message.title)}</UT.Title>}
                    <UT.Text small={props.small} large={props.large}>{t(message.message)}</UT.Text>
                </UniStack.Column>
            </Snackbar>
        </>
    )
}