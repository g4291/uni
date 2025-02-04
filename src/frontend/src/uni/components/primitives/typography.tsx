import React from "react";
import { Typography, TypographySystem } from "@mui/joy";
import { ColorPaletteProp, SxProps, TextColor } from "@mui/joy/styles/types";
import UniCommon, { IUniWithBorderProps, IUniWithChildrenProps, IUniWithSizeProps, IUniWithSXProps } from "../../common";

// types
type UniHeadingLevel = "h1" | "h2" | "h3" | "h4" | "h5" | "h6";

// Typography config
export const UNI_TYPO_CONFIG = {

} as {
    
}

// props
export interface IUniTypographyProps extends IUniWithChildrenProps, IUniWithSXProps, IUniWithBorderProps, IUniWithSizeProps {
    component?: any
    startDecorator?: React.ReactNode
    endDecorator?: React.ReactNode
    gutterBottom?: boolean
    textColor?: TextColor
    noWrap?: boolean
    fullWidth?: boolean

    color?: ColorPaletteProp
}

// heading
interface IBaseUniHeadingProps extends IUniTypographyProps {
    level: UniHeadingLevel
}

/**
 * Base UniHeading component
 * 
 * @param props IBaseUniHeadingProps
 * @returns JSX.Element
 */
function BaseUniHeading(props: IBaseUniHeadingProps): JSX.Element {
    const {sx, level, children, border, ...rest} = props;

    const _sx = border ? UniCommon.config.defaultBorder : {};
    return (
        <Typography sx={{..._sx, ...sx} as SxProps} level={(level as keyof TypographySystem)} {...rest}>
            {children}
        </Typography>
    )
}

/**
 * Renders a H1 component
 *  
 * @param props IUniTypographyProps
 * @returns JSX.Element
 */
export function UniH1(props: IUniTypographyProps): JSX.Element {
    return <BaseUniHeading level="h1" {...props} />
}

/**
 * Renders a H2 component
 *  
 * @param props IUniTypographyProps
 * @returns JSX.Element
 */
export function UniH2(props: IUniTypographyProps): JSX.Element {
    return <BaseUniHeading level="h2" {...props} />
}

/**
 * Renders a H3 component
 *  
 * @param props IUniTypographyProps
 * @returns JSX.Element
 */
export function UniH3(props: IUniTypographyProps): JSX.Element {
    return <BaseUniHeading level="h3" {...props} />
}

/**
 * Renders a H4 component
 *  
 * @param props IUniTypographyProps
 * @returns JSX.Element
 */
export function UniH4(props: IUniTypographyProps): JSX.Element {
    return <BaseUniHeading level="h4" {...props} />
}

/**
 * Renders a H5 component
 *  
 * @param props IUniTypographyProps
 * @returns JSX.Element
 */
export function UniH5(props: IUniTypographyProps): JSX.Element {
    return <BaseUniHeading level="h5" {...props} />
}

// Text
interface IBaseUniTextProps extends IUniTypographyProps {
    component?: any
    level?: keyof TypographySystem
}

function BaseUniText(props: IBaseUniTextProps): JSX.Element {
    const { sx, level, children, component, small, large, border, xs, fullWidth, ...rest } = props;

    const _level = level || ( xs ? "body-xs": small ? "body-sm" : large ? "body-lg" : undefined);
    const _sx: any = border ? UniCommon.config.defaultBorder : {};
    fullWidth && (_sx.width = "100%");
    return (
        <Typography sx={{..._sx, ...sx} as SxProps} level={_level} component={component || "span"}  {...rest}>
            {children}
        </Typography>
    )
}

/**
 * Renders a Text component
 * 
 * @param props IUniTypographyProps
 * @returns JSX.Element
 */
export function UniText(props: IUniTypographyProps): JSX.Element {
    return <BaseUniText {...props} />
}

/**
 * Renders a Paragraph component
 * 
 * @param props IUniTypographyProps
 * @returns JSX.Element
 */
export function UniParagraph(props: IUniTypographyProps): JSX.Element {
    return <BaseUniText component="p" {...props} />
}

// Title
interface IBaseUniTitleProps extends IUniTypographyProps {
    level?: keyof TypographySystem
}

/**
 * Base UniTitle component
 * 
 * @param props IBaseUniTitleProps
 * @returns JSX.Element
 */
function BaseUniTitle(props: IBaseUniTitleProps): JSX.Element {
    const { sx, level, children, component, small, large, border, ...rest } = props;

    const _level = level || (small ? "body-sm" : large ? "body-lg" : "body-md");
    const _sx = border ? UniCommon.config.defaultBorder : {};
    return (
        <Typography sx={{..._sx, fontWeight: "bold", ...sx} as SxProps} level={_level} component={component || "p"}  {...rest}>
            {children}
        </Typography>
    )
}

/**
 * Renders a Title component
 * 
 * @param props IUniTypographyProps
 * @returns JSX.Element
 */
export function UniTitle(props: IUniTypographyProps): JSX.Element {
    return <BaseUniTitle {...props} />
}

/**
 * UniTypography package
 */
export const UniTypography = {
    config: UNI_TYPO_CONFIG,
    H1: UniH1,
    H2: UniH2,
    H3: UniH3,
    H4: UniH4,
    H5: UniH5,
    Text: UniText,
    Paragraph: UniParagraph,
    Title: UniTitle,
}

export default UniTypography;