import React from "react";
import { SxProps } from "@mui/joy/styles/types";

import { getUniColor, getUniVariant, IUniWithColorProps, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps, UniColorProp, UniVariantProp } from "../common";
import UniButton from "./primitives/button";
import { useUniTranslator } from "../translator";
import useUniLogout from "../api/hooks/logout";
import { Tooltip } from "@mui/joy";
import UniIcons from "../icons";


export const UNI_LOGOUT_BUTTON_CONFIG = {
    defaultSx: {

    },
    defaultVariant: "soft",
    defaultColor: "warning"

} as {
    defaultSx: SxProps,
    defaultColor: UniColorProp,
    defaultVariant: UniVariantProp
}

interface IUniLogoutButtonProps extends IUniWithSXProps, IUniWithSizeProps, IUniWithVariantProps, IUniWithColorProps {
    onClick?: () => any
    text?: string
    fullWidth?: boolean
    noTooltip?: boolean
}

/**
 * Renders a logout button component.
 *
 * @param {IUniLogoutButtonProps} props - The props for the UniLogoutButton component.
 * @returns {JSX.Element} The rendered UniLogoutButton component.
 */
export default function UniLogoutButton(props: IUniLogoutButtonProps): JSX.Element {
    const { sx, onClick, text, noTooltip, ...rest } = props;
    const t = useUniTranslator()
    const logout = useUniLogout()

    const color = React.useMemo(() => getUniColor(props, UNI_LOGOUT_BUTTON_CONFIG.defaultColor), [props])
    const variant = React.useMemo(() => getUniVariant(props, UNI_LOGOUT_BUTTON_CONFIG.defaultVariant), [props])

    const element = <div>
        <UniButton
            aria-label={"logout"}
            neutral={color === "neutral"}
            primary={color === "primary"}
            error={color === "danger"}
            warning={color === "warning"}
            success={color === "success"}

            outlined={variant === "outlined"}
            solid={variant === "solid"}
            soft={variant === "soft"}
            plain={variant === "plain"}

            sx={{ ...UNI_LOGOUT_BUTTON_CONFIG.defaultSx, ...props.sx } as SxProps}
            onClick={() => {
                logout()
                if (onClick) {
                    onClick()
                }
            }}
            endDecorator={text && <UniIcons.Logout />}
            {...rest}
        > {
                text ? t(text) : <UniIcons.Logout />
            }
        </UniButton>
    </div>

    if (noTooltip) return element

    return (
        <Tooltip title={t(text || "logout")}>
            {element}
        </Tooltip>
    )
}