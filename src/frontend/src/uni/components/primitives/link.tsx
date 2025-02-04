import React from "react";
import { Link } from "@mui/joy";
import { SxProps } from "@mui/joy/styles/types";
import { getUniColor, getUniVariant, IUniWithChildrenProps, IUniWithColorProps, IUniWithDecoratorsProps, IUniWithSXProps, IUniWithVariantProps, UniColorProp, UniVariantProp } from "../../common";


// Button config
export const UNI_LINK_CONFIG = {
    defaultMargin: 0,
    defaultSx: {
        color: "primary.500"
    },
    defaultVariant: "plain",
    defaultColor: "primary",
    underline: "none"
} as {
    defaultMargin: string | number,
    defaultSx: SxProps,
    defaultVariant: UniVariantProp,
    defaultColor: UniColorProp,
    underline: "none" | "hover" | "always" | undefined
}

// props
export interface IUniLinkProps extends IUniWithChildrenProps, IUniWithSXProps, IUniWithVariantProps, IUniWithDecoratorsProps, IUniWithColorProps {
    href?: string
    target?: string

    onClick?: () => any
    disabled?: boolean
}

/**
 * Base UniLink component
 * 
 * @param props IBaseUniLink
 * @returns JSX.Element
 */
export function UniLink(props: IUniLinkProps): JSX.Element {
    const { sx, children, onClick } = props;

    const variant = React.useMemo(() => getUniVariant(props, UNI_LINK_CONFIG.defaultVariant), [props])
    const color = React.useMemo(() => getUniColor(props, UNI_LINK_CONFIG.defaultColor), [props])

    const _sx = {m: UNI_LINK_CONFIG.defaultMargin, ...UNI_LINK_CONFIG.defaultSx, ...sx} as SxProps
    return (
        <Link 
        href={props.href}
        underline={UNI_LINK_CONFIG.underline}
        target={props.target}
        disabled={props.disabled}
        startDecorator={props.startDecorator}
        endDecorator={props.endDecorator}
        variant={variant} 
        onClick={() => {
            if (onClick) {
                onClick()
            }
        }} 
        sx={_sx} 
        color={color}>
            {children}
        </Link>
    )
}


export default UniLink;