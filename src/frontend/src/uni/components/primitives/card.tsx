import React from "react";
import { SxProps } from "@mui/joy/styles/types";
import { Card, CardActions, CardContent, CardOverflow } from "@mui/joy";
import { getUniColor, getUniVariant, IUniWithChildrenProps, IUniWithColorProps, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps, UniColorProp, UniVariantProp } from "../../common";
import { useUniThemeMode } from "../../theme";


// ModalDialog config
export const UNI_CARD_CONFIG = {
    defaultCardContentSx: {
        scrollbarWidth: "thin"
    },
    defaultSx: {
        width: "400px",
    },
    defaultSmall: false,
    defaultLarge: false,
    defaultFullwidth: false,
    defaultOverflow: false,
    defaultResizableH: false,
    defaultResizableV: false,
    defaultVariant: "plain",
    defaultColor: "neutral"
} as {
    defaultCardContentSx: SxProps,
    defaultSx: SxProps,
    defaultSmall: boolean,
    defaultLarge: boolean,
    defaultFullwidth: boolean,
    defaultOverflow: boolean,
    defaultResizableH: boolean,
    defaultResizableV: boolean,
    defaultVariant: UniVariantProp,
    defaultColor: UniColorProp

}

export interface IUniCardProps extends IUniWithChildrenProps, IUniWithSXProps, IUniWithVariantProps, IUniWithSizeProps, IUniWithColorProps {
    header?: React.ReactNode
    footer?: React.ReactNode
    actions?: React.ReactNode

    contentSx?: SxProps
    fullWidth?: boolean

    close?: boolean

    overflow?: boolean
    resizableH?: boolean
    resizableV?: boolean
    onClick?: () => any
}

/**
 * Base UniModalDialog component
 * 
 * @param props IBaseUniModalDialogProps
 * @returns JSX.Element
 */
export function UniCard(props: IUniCardProps): JSX.Element {
    // helpers
    const _small = props.small !== undefined ? props.small : UNI_CARD_CONFIG.defaultSmall
    const _large = props.large !== undefined ? props.large : UNI_CARD_CONFIG.defaultLarge
    const _resizableV = props.resizableV !== undefined ? props.resizableV : UNI_CARD_CONFIG.defaultResizableV
    const _resizableH = props.resizableH !== undefined ? props.resizableH : UNI_CARD_CONFIG.defaultResizableH
    const _resizableBoth = _resizableH && _resizableV
    const _overflow = props.overflow !== undefined ? props.overflow : UNI_CARD_CONFIG.defaultOverflow
    const _fullwidth = props.fullWidth !== undefined ? props.fullWidth : UNI_CARD_CONFIG.defaultFullwidth

    const size = (_small) ? "sm" : (_large) ? "lg" : undefined;
    const variant = React.useMemo(() => getUniVariant(props, UNI_CARD_CONFIG.defaultVariant), [props])
    const color = React.useMemo(() => getUniColor(props, UNI_CARD_CONFIG.defaultColor), [props])

    const contentSx = { ...UNI_CARD_CONFIG.defaultCardContentSx, ...props.contentSx } as SxProps
    const cardSx = { ...UNI_CARD_CONFIG.defaultSx, ...props.sx } as any

    const [mode] = useUniThemeMode()
    
    if (_resizableH) {
        cardSx.overflow = "auto"
        cardSx.resize= "horizontal"
    }
    if (_resizableV) {
        cardSx.overflow = "auto"
        cardSx.resize= "vertical"
    }
    if (_resizableBoth) {
        cardSx.resize= "both"
    }

    _fullwidth && (cardSx.width = "100%")
    if (props.onClick) {
        (cardSx.cursor = "pointer")
        cardSx["&:hover"] = {
            boxShadow: mode === "dark" ? "0 0 10px 0 rgba(255,255,255,0.2)" : "0 0 10px 0 rgba(0,0,0,0.2)"
        }
    } 

    const innerContent = (
        <CardContent sx={contentSx}>
            {props.children}
        </CardContent>
    )


    return (
        <>
            <Card
                variant={variant}
                color={color}
                size={size}
                sx={cardSx as SxProps}
                onClick={props.onClick}
            >
                {
                    props.header && (
                        _overflow ? <CardOverflow>{props.header}</CardOverflow> : props.header
                    )
                }

                {innerContent}

                {
                    props.footer && (
                        _overflow ? <CardOverflow>{props.footer}</CardOverflow> : props.footer
                    )
                }
                {props.actions && <CardActions>
                    {props.actions}
                </CardActions> }
            </Card>
        </>
    )

}

export default UniCard;