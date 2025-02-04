import React from "react";
import Stack from "@mui/joy/Stack";
import { SxProps } from "@mui/joy/styles/types";
import UniCommon, { IUniWithBorderProps, IUniWithChildrenProps, IUniWithSXProps, UniComponentSize, UniComponentSpacing } from "../../common";


// Stack config
export const UNI_STACK_CONFIG = {
    defaultSpacing: 1,
    defaultSx: {
        m:0,
        mt:0
    },
    defaultSize: undefined,
    defaultFullwidth: false,
    defaultFullheight: false,
} as {
    defaultSpacing: UniComponentSpacing,
    defaultSx: SxProps,
    defaultSize: UniComponentSize,
    defaultFullwidth: boolean,
    defaultFullheight: boolean,
    
}

// props
export interface IUniStackProps extends IUniWithChildrenProps, IUniWithSXProps, IUniWithBorderProps {
    spacing?: UniComponentSpacing
    reverse?: boolean
    fullWidth?: boolean
    fullHeight?: boolean
}

interface IBaseUniStackProps extends IUniStackProps {
    row: boolean
}

/**
 * Base UniStack component
 * 
 * @param props IBaseUniStackProps
 * @returns JSX.Element
 */
function BaseUniStack(props: IBaseUniStackProps): JSX.Element {
    const { sx, row, reverse, spacing, children, fullHeight, fullWidth, border, ...rest } = props;

    const direction = row ? reverse ? "row-reverse" : "row" : reverse ? "column-reverse" : "column";

    const _sx: any = border ? {...UniCommon.config.defaultBorder} : {};
    const _fullwidth = fullWidth !== undefined ? fullWidth : UNI_STACK_CONFIG.defaultFullwidth;
    const _fullheight = fullHeight !== undefined ? fullHeight : UNI_STACK_CONFIG.defaultFullheight;

    if (_fullwidth) _sx.width = "100%"
    if (_fullheight) _sx.height = "100%"
    return (
        <Stack
            direction={direction}
            sx={{ ...UNI_STACK_CONFIG.defaultSx, ..._sx, ...sx } as SxProps}
            spacing={spacing !== undefined ? spacing : UNI_STACK_CONFIG.defaultSpacing}
            {...rest}>
            {children}
        </Stack>
    )
}

/**
 * Renders a Stack column
 * 
 * @param props IUniStackProps
 * @returns JSX.Element
 */
export function UniStackColumn(props: IUniStackProps): JSX.Element {
    return <BaseUniStack row={false} {...props} />
}

/**
 * Renders a Stack row
 * 
 * @param props IUniStackItemProps
 * @returns JSX.Element
 */
export function UniStackRow(props: IUniStackProps): JSX.Element {
    return <BaseUniStack row={true} {...props} />
}


/**
 * UniStack package
 */
export const UniStack = {
    config: UNI_STACK_CONFIG,
    Column: UniStackColumn,
    Row: UniStackRow
}

export default UniStack;