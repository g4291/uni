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
export interface IUniBoxProps extends IUniWithChildrenProps, IUniWithSXProps, IUniWithBorderProps {
    fullWidth?: boolean;
    fullHeight?: boolean;
    flex?: boolean;
}

// Base UniBox component
const BaseUniBox = React.forwardRef<HTMLDivElement, IUniBoxProps>((props, ref) => {
    const { sx, fullWidth, fullHeight, flex, border, ...rest } = props;
    const _sx: any = border ? { ...UniCommon.config.defaultBorder } : {};

    const _fullWidth = fullWidth !== undefined ? fullWidth : UNI_BOX_CONFIG.defaultFullwidth;
    const _fullHeight = fullHeight !== undefined ? fullHeight : UNI_BOX_CONFIG.defaultFullheight;
    const _flex = flex !== undefined ? flex : UNI_BOX_CONFIG.defaultFlex;

    if (_fullWidth) _sx.width = "100%";
    if (_fullHeight) _sx.height = "100%";
    if (_flex) _sx.display = "flex";

    return (
        <Box
            ref={ref} // Forward the ref here
            sx={{ ...UNI_BOX_CONFIG.defaultBoxSx, ..._sx, ...sx } as SxProps}
            {...rest}
        />
    );
});

// Renders a UniBox component with custom styling and children.
export const UniBoxBasic = React.forwardRef<HTMLDivElement, IUniBoxProps>((props, ref) => {
    return <BaseUniBox ref={ref} {...props} />;
});

// Renders a UniBox component with vertical center alignment.
export const UniBoxVC = React.forwardRef<HTMLDivElement, IUniBoxProps>((props, ref) => {
    const { sx, children, ...rest } = props;
    return (
        <BaseUniBox
            ref={ref}
            sx={{
                ...UNI_BOX_CONFIG.defaultBoxSx,
                display: 'flex',
                justifyContent: 'flex-start',
                alignItems: "center",
                ...sx,
            } as SxProps}
            {...rest}
        >
            {children}
        </BaseUniBox>
    );
});

// Renders a UniBox component with vertical down alignment.
export const UniBoxVD = React.forwardRef<HTMLDivElement, IUniBoxProps>((props, ref) => {
    const { sx, children, ...rest } = props;
    return (
        <BaseUniBox
            ref={ref}
            sx={{
                ...UNI_BOX_CONFIG.defaultBoxSx,
                display: 'flex',
                justifyContent: 'flex-start',
                alignItems: "flex-end",
                ...sx,
            } as SxProps}
            {...rest}
        >
            {children}
        </BaseUniBox>
    );
});

// Renders a UniBox component with horizontal center alignment.
export const UniBoxHC = React.forwardRef<HTMLDivElement, IUniBoxProps>((props, ref) => {
    const { sx, children, ...rest } = props;
    return (
        <BaseUniBox
            ref={ref}
            sx={{
                ...UNI_BOX_CONFIG.defaultBoxSx,
                display: 'flex',
                justifyContent: 'center',
                alignItems: "flex-start",
                ...sx,
            } as SxProps}
            {...rest}
        >
            {children}
        </BaseUniBox>
    );
});

// Renders a UniBox component with horizontal right alignment.
export const UniBoxHR = React.forwardRef<HTMLDivElement, IUniBoxProps>((props, ref) => {
    const { sx, children, ...rest } = props;
    return (
        <BaseUniBox
            ref={ref}
            sx={{
                ...UNI_BOX_CONFIG.defaultBoxSx,
                display: 'flex',
                justifyContent: 'flex-end',
                alignItems: "flex-start",
                ...sx,
            } as SxProps}
            {...rest}
        >
            {children}
        </BaseUniBox>
    );
});

// Renders a UniBox component with vertical and horizontal center alignment.
export const UniBoxVHC = React.forwardRef<HTMLDivElement, IUniBoxProps>((props, ref) => {
    const { sx, children, ...rest } = props;
    return (
        <BaseUniBox
            ref={ref}
            sx={{
                ...UNI_BOX_CONFIG.defaultBoxSx,
                display: 'flex',
                justifyContent: 'center',
                alignItems: "center",
                ...sx,
            } as SxProps}
            {...rest}
        >
            {children}
        </BaseUniBox>
    );
});

// UniBox package
export const UniBox = {
    config: UNI_BOX_CONFIG,
    Box: UniBoxBasic,
    VC: UniBoxVC,
    VD: UniBoxVD,
    HC: UniBoxHC,
    HR: UniBoxHR,
    VHC: UniBoxVHC,
};

export default UniBox;