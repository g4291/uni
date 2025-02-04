import React from "react";
import { SxProps } from "@mui/joy/styles/types";
import { Box } from "@mui/joy";
import UniCommon, { IUniWithBorderProps, IUniWithChildrenProps, IUniWithSXProps } from "../../common";


// Box config
export const UNI_BOX_CONFIG = {
    defaultBoxSx: {
        m: 0,
        p: 0,
        display: "block",
    },
    defaultFullwidth: false,
    defaultFullheight: false,
    defaultFlex: false,
} as {
    defaultBoxSx: SxProps,
    defaultFullwidth: boolean,
    defaultFullheight: boolean,
    defaultFlex: boolean,
}

// props
export interface IUniBoxProps extends IUniWithChildrenProps, IUniWithSXProps, IUniWithBorderProps{
    fullWidth?: boolean
    fullHeight?: boolean
    flex?: boolean
}

/**
 * Base UniBox component
 * 
 * @param props IUniBoxProps
 * @returns JSX.Element
 */
function BaseUniBox(props: IUniBoxProps): JSX.Element {
    const { sx, fullWidth, fullHeight, flex, border, ...rest } = props;
    const _sx: any = border ? {...UniCommon.config.defaultBorder} : {};

    const _fullwidth = fullWidth !== undefined ? fullWidth : UNI_BOX_CONFIG.defaultFullwidth;
    const _fullheight = fullHeight !== undefined ? fullHeight : UNI_BOX_CONFIG.defaultFullheight;
    const _flex = flex !== undefined ? flex : UNI_BOX_CONFIG.defaultFlex;

    if (_fullwidth) _sx.width = "100%"
    if (_fullheight) _sx.height = "100%"
    if (_flex) _sx.display = "flex"
    return (
        <Box sx={{ ...UNI_BOX_CONFIG.defaultBoxSx, ..._sx, ...sx } as SxProps} {...rest} />
    )
}

/**
 * Renders a UniBox component with custom styling and children.
 *
 * @param props - The props for the UniBox component.
 * @returns The rendered UniBox component.
 */
export function UniBoxBasic(props: IUniBoxProps): JSX.Element {
    return <BaseUniBox {...props} />
}

/**
 * Renders a UniBox component with vertical center alignment.
 * 
 * @param props - The props for the UniBoxVC component.
 * @returns The rendered UniBoxVC component.
 */
export function UniBoxVC(props: IUniBoxProps): JSX.Element {

    const { sx, children, ...rest } = props;
    return (
        <BaseUniBox sx={{
            ...UNI_BOX_CONFIG.defaultBoxSx,
            display: 'flex',
            justifyContent: 'flex-start',
            alignItems: "center",
            ...sx
        } as SxProps} {...rest}>
            {children}
        </BaseUniBox>
    )
}

/**
 * Renders a UniBox component with vertical down alignment.
 * 
 * @param props - The props for the UniBoxVD component.
 * @returns The rendered UniBoxVD component.
 */
export function UniBoxVD(props: IUniBoxProps): JSX.Element {

    const { sx, children, ...rest } = props;
    return (
        <BaseUniBox sx={{
            ...UNI_BOX_CONFIG.defaultBoxSx,
            display: 'flex',
            justifyContent: 'flex-start',
            alignItems: "flex-end",
            ...sx
        } as SxProps} {...rest}>
            {children}
        </BaseUniBox>
    )
}

/**
 * Renders a UniBox component with horizontal center alignment.
 * 
 * @param props - The props for the UniBoxHC component.
 * @returns The rendered UniBoxHC component.
 */
export function UniBoxHC(props: IUniBoxProps): JSX.Element {

    const { sx, children, ...rest } = props;
    return (
        <BaseUniBox sx={{
            ...UNI_BOX_CONFIG.defaultBoxSx,
            display: 'flex',
            justifyContent: 'center',
            alignItems: "flex-start",
            ...sx
        } as SxProps} {...rest}>
            {children}
        </BaseUniBox>
    )
}

/**
 * Renders a UniBox component with horizontal right alignment.
 * 
 * @param props - The props for the UniBoxHR component.
 * @returns The rendered UniBoxHR component.
 */
export function UniBoxHR(props: IUniBoxProps): JSX.Element {
    const { sx, children, ...rest } = props;
    return (
        <BaseUniBox sx={{
            ...UNI_BOX_CONFIG.defaultBoxSx,
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: "flex-start",
            ...sx
        } as SxProps} {...rest}>
            {children}
        </BaseUniBox>
    )
}

/**
 * Renders a UniBox component with vertical and horizontal center alignment.
 * 
 * @param props - The props for the UniBoxVHC component.
 * @returns The rendered UniBoxVHC component.
 */
export function UniBoxVHC(props: IUniBoxProps): JSX.Element {
    const { sx, children, ...rest } = props;
    return (
        <BaseUniBox sx={{
            ...UNI_BOX_CONFIG.defaultBoxSx,
            display: 'flex',
            justifyContent: 'center',
            alignItems: "center",
            ...sx
        } as SxProps} {...rest}>
            {children}
        </BaseUniBox>
    )
}


/**
 * UniBox package
 */
export const UniBox = {
    config: UNI_BOX_CONFIG,
    Box: UniBoxBasic,
    VC: UniBoxVC,
    VD: UniBoxVD,
    HC: UniBoxHC,
    HR: UniBoxHR,
    VHC: UniBoxVHC
}

export default UniBox;