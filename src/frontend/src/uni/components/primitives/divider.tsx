import React from "react";
import { SxProps } from "@mui/joy/styles/types";
import { Divider } from "@mui/joy";
import { IUniWithChildrenProps, IUniWithSXProps, UniComponentSpacing } from "../../common";


// Divider config
export const UNI_DIVIDER_CONFIG = {
    defaultSpacing: 1,
    defaultSx: {
    },
    defaultFullwidth: false,
    defaultFullheight: false,
} as {
    defaultSpacing: UniComponentSpacing | string,
    defaultSx: SxProps,
    defaultFullwidth: boolean,
    defaultFullheight: boolean,
    
}

// props
export interface IUniDividerProps extends IUniWithChildrenProps, IUniWithSXProps {
    spacing?: UniComponentSpacing | string
    fullWidth?: boolean
    fullHeight?: boolean
}

interface IBaseUniDividerProps extends IUniDividerProps {
    vertical: boolean
}

/**
 * Base UniDivider component
 * 
 * @param props IBaseUniDividerProps
 * @returns JSX.Element
 */
function BaseUniDivider(props: IBaseUniDividerProps): JSX.Element {
    const { sx, vertical, spacing, children, fullWidth, fullHeight } = props;

    const _spacing = spacing !== undefined ? spacing : UNI_DIVIDER_CONFIG.defaultSpacing;
    const _orientation = vertical ? "vertical" : "horizontal";

    if (_spacing === undefined || _spacing === 0 || _spacing === "0") return (
        <Divider
            sx={{ ...UNI_DIVIDER_CONFIG.defaultSx, ...sx } as SxProps}
            orientation={_orientation}
        />
    )

    const _sx: any = {}
    if (vertical) {
        _sx.ml = _spacing
        _sx.mr = _spacing
    } else {
        _sx.mt = _spacing
        _sx.mb = _spacing
    }
    const _fullwidth = fullWidth !== undefined ? fullWidth : UNI_DIVIDER_CONFIG.defaultFullwidth;
    const _fullheight = fullHeight !== undefined ? fullHeight : UNI_DIVIDER_CONFIG.defaultFullheight;

    if (_fullwidth) _sx.width = "100%"
    if (_fullheight) _sx.height = "100%"

    return (
        <Divider
            sx={{ ...UNI_DIVIDER_CONFIG.defaultSx, ..._sx, ...sx } as SxProps}
            orientation={vertical ? "vertical" : "horizontal"}
        >{children}</Divider>
    )
}

/**
 * Renders a horizontal Divider
 * 
 * @param props IUniDividerProps
 * @returns JSX.Element
 */
export function UniDividerHorizontal(props: IUniDividerProps): JSX.Element {
    return <BaseUniDivider vertical={false} {...props} />
}

/**
 * Renders a vertical Divider
 * 
 * @param props IUniDividerProps
 * @returns JSX.Element
 */
export function UniDividerVertical(props: IUniDividerProps): JSX.Element {
    return <BaseUniDivider vertical={true} {...props} />
}


/**
 * UniDivider package
 */
export const UniDivider = {
    config: UNI_DIVIDER_CONFIG,
    H: UniDividerHorizontal,
    V: UniDividerVertical
}

export default UniDivider;