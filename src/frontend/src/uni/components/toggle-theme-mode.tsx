import React from "react";
import { getUniColor, getUniVariant, IUniWithColorProps, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps, UniColorProp, UniThemeMode, UniVariantProp } from "../common";
import { SxProps } from "@mui/joy/styles/types";
import { useUniThemeMode } from "../theme";
import UniButton from "./primitives/button";
import { Tooltip } from "@mui/joy";
import { useUniTranslator } from "../translator";
import UniIcons from "../icons";


export const UNI_TOGGLE_THEME_MODE_CONFIG = {
    defaultSx: {

    },
    defaultVariant: "soft",
    defaultColor: "neutral"

} as {
    defaultSx: SxProps,
    defaultColor: UniColorProp,
    defaultVariant: UniVariantProp
}

interface IUniToggleThemeModeProps extends IUniWithSXProps, IUniWithSizeProps, IUniWithVariantProps, IUniWithColorProps {
    onClick?: (mode: UniThemeMode) => any
    text?: string
    fullWidth?: boolean
    noTooltip?: boolean
}

/**
 * Renders a toggle theme mode button.
 *
 * @param props - The component props.
 * @returns The rendered toggle theme mode button.
 */
export default function UniToggleThemeMode(props: IUniToggleThemeModeProps): JSX.Element {
    const { sx, onClick, text, noTooltip, ...rest } = props;
    const [mode, setMode] = useUniThemeMode();
    const t = useUniTranslator()

    const color = React.useMemo(() => getUniColor(props, UNI_TOGGLE_THEME_MODE_CONFIG.defaultColor), [props])
    const variant = React.useMemo(() => getUniVariant(props, UNI_TOGGLE_THEME_MODE_CONFIG.defaultVariant), [props])

    const icon = mode === "light" ? <UniIcons.DarkMode /> : <UniIcons.LightMode />

    const element = <div>
        <UniButton
            neutral={color === "neutral"}
            primary={color === "primary"}
            error={color === "danger"}
            warning={color === "warning"}
            success={color === "success"}

            outlined={variant === "outlined"}
            solid={variant === "solid"}
            soft={variant === "soft"}
            plain={variant === "plain"}

            sx={{ ...UNI_TOGGLE_THEME_MODE_CONFIG.defaultSx, ...props.sx } as SxProps}
            onClick={() => {
                setMode(mode === "light" ? "dark" : "light")
                if (onClick) {
                    onClick(mode === "light" ? "dark" : "light")
                }
            }}
            endDecorator={text && icon}
            {...rest}
        >
            {
                text ? t(text) : icon
            }
        </UniButton>
    </div>

    if (noTooltip) return element

    return (
        <Tooltip title={mode === "light" ? t("Switch to dark mode") : t("Switch to light mode")}>
            {element}
        </Tooltip>
    )
}