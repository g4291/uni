import { SxProps } from "@mui/joy/styles/types";

// types
export type UniComponentSpacing = number | undefined
export type UniComponentSize = boolean | "auto" | number | undefined
export type UniVariantProp = "plain" | "outlined" | "soft" | "solid" | undefined
export type UniColorProp = "neutral" | "primary" | "success" | "danger" | "warning" | undefined
export type UniThemeMode = "light" | "dark" | "system" | undefined
export type UniBreakPoint = "xs" | "sm" | "md" | "lg" | "xl"
export type UniAlertSeverity = "error" | "warning" | "info" | "success"



// props
export interface IUniWithSXProps {
    sx?: SxProps
}

export interface IUniWithChildrenProps {
    children?: React.ReactNode
}

export interface IUniWithBorderProps {

    /**
     * Includes default border if true
     */
    border?: boolean
}

export interface IUniWithVariantProps {
    /**
     * plain variang, default solid
     */
    plain?: boolean

    /**
     * outlined variant, default solid
     */
    outlined?: boolean

    /**
     * soft variant, default solid
     */
    soft?: boolean
    
    /**
     * solid variant, default
     */
    solid?: boolean
}

export interface IUniWithColorProps {
    /**
     * Neutral color, default neutral
     */
    neutral?: boolean

    /**
     * Primary color, default neutral
     */
    primary?: boolean

    /**
     * Success color, default neutral
     */
    success?: boolean

    /**
     * Danger color, default neutral
     */
    error?: boolean

    /**
     * Warning color, default neutral
     */
    warning?: boolean
}

export interface IUniWithSizeProps {
    /**
     * Small size, default md
     */
    small?: boolean

    /**
     * Large size, default md
     */
    large?: boolean

    xs?: boolean
}

export interface IUniWithDecoratorsProps {
    /**
     * Start decorator, included before children
     */
    startDecorator?: React.ReactNode
    
    /**
     * End decorator, included after children
     */
    endDecorator?: React.ReactNode
}

export interface IUniToast {
    title: string
    message: string
    severity?: UniAlertSeverity
}

/**
 * Get UniVariant from props
 * 
 * @param props IUniWithVariantProps
 * @param defaultValue UniVariant
 * @returns UniVariant
 */
export function getUniVariant(props: IUniWithVariantProps, defaultValue: UniVariantProp): UniVariantProp {

    const { plain, outlined, soft, solid } = props;

    if (solid) return "solid"
    if (plain) return "plain"
    if (outlined) return "outlined"
    if (soft) return "soft"

    return defaultValue
}

export function getUniColor(props: IUniWithColorProps, defaultValue: UniColorProp): UniColorProp {
    const { neutral, primary, success, error, warning } = props;

    if (neutral) return "neutral"
    if (primary) return "primary"
    if (success) return "success"
    if (error) return "danger"
    if (warning) return "warning"

    return defaultValue
}


// export
const UNI_COMMON_CONFIG = {
    defaultBorder: {
        border: "1px solid",
        borderColor: "primary.500",
        borderRadius: 4
    },
} as {
    defaultBorder: SxProps
}

export const UniCommon = {
    config: UNI_COMMON_CONFIG
}

export default UniCommon