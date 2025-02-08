import React from "react";
import { Button } from "@mui/joy";
import { SxProps } from "@mui/joy/styles/types";
import { getUniColor, getUniVariant, IUniWithChildrenProps, IUniWithColorProps, IUniWithDecoratorsProps, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps, UniColorProp, UniVariantProp } from "../../common";


// Button config
export const UNI_BUTTON_CONFIG = {
    defaultMargin: 0,
    defaultSx: {
    },
    defaultVariant: "solid",
    defaultColor: "neutral",
    defaultUppercase: false,
    defaultSmall: false,
} as {
    defaultMargin: string | number,
    defaultSx: SxProps,
    defaultVariant: UniVariantProp,
    defaultColor: UniColorProp,
    defaultUppercase: boolean,
    defaultSmall: boolean,
}

// props
export interface IUniButtonProps extends IUniWithChildrenProps, IUniWithSXProps, IUniWithVariantProps, IUniWithSizeProps, IUniWithDecoratorsProps, IUniWithColorProps {
    onClick?: (e: React.MouseEvent<HTMLAnchorElement, MouseEvent>) => any
    disabled?: boolean
    fullWidth?: boolean
    loading?: boolean
    uppercase?: boolean
    submit?: boolean

    left?: boolean
    right?: boolean
}

/**
 * Base UniButton component
 * 
 * @param props IBaseUniButton
 * @returns JSX.Element
 */
export function UniButton(props: IUniButtonProps): JSX.Element {
    const { sx, children, onClick, small, large } = props;

    const size = small ? "sm" : large ? "lg" : undefined;
    const _size = size === undefined ? (UNI_BUTTON_CONFIG.defaultSmall ? "sm" : undefined) : size
    const variant = React.useMemo(() => getUniVariant(props, UNI_BUTTON_CONFIG.defaultVariant), [props])
    const color = React.useMemo(() => getUniColor(props, UNI_BUTTON_CONFIG.defaultColor), [props])

    const _sx: any = {m: (props.fullWidth ? 0 : UNI_BUTTON_CONFIG.defaultMargin), ...UNI_BUTTON_CONFIG.defaultSx, ...sx}
    if (props.uppercase) _sx.textTransform = "uppercase"
    if (props.left)_sx.justifyContent = "flex-start"
    if (props.right) _sx.justifyContent = "flex-end"
    
    return (
        <Button 
        disabled={props.disabled}
        loading={props.loading}
        startDecorator={props.startDecorator}
        endDecorator={props.endDecorator}
        fullWidth={props.fullWidth}
        type={props.submit ? "submit" : undefined}

        variant={variant} size={_size} onClick={(e) => {
            if (onClick) {
                onClick(e)
            }
        }} sx={_sx as SxProps} color={color}>
            {children}
        </Button>
    )
}


export default UniButton;