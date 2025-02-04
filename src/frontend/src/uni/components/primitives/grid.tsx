import React from "react";
import Grid from "@mui/joy/Grid";
import { SxProps } from "@mui/joy/styles/types";
import UniCommon, { IUniWithBorderProps, IUniWithChildrenProps, IUniWithSXProps, UniComponentSize, UniComponentSpacing } from "../../common";


// Grid config
export const UNI_GRID_CONGIG = {
    defaultSpacing: 2,
    defaultContainerSx: {
        m:0
    },
    defaultItemSx: {
        m:0
    },
    defaultSize: undefined
} as {
    defaultSpacing: UniComponentSpacing,
    defaultContainerSx: SxProps,
    defaultItemSx: SxProps,
    defaultSize: UniComponentSize
}

// props
export interface IUniGridProps extends IUniWithChildrenProps, IUniWithSXProps, IUniWithBorderProps {
    spacing?: UniComponentSpacing
    flexGrow?: boolean
}

export interface IUniGridItemProps extends IUniGridProps {
    xs?: UniComponentSize
    sm?: UniComponentSize
    md?: UniComponentSize
    lg?: UniComponentSize
    xl?: UniComponentSize
}

interface IBaseUniGridProps extends IUniGridProps {
    container?: boolean
    xs?: UniComponentSize
    sm?: UniComponentSize
    md?: UniComponentSize
    lg?: UniComponentSize
    xl?: UniComponentSize
}

/**
 * Base UniGrid component
 * 
 * @param props IBaseUniGridProps
 * @returns JSX.Element
 */
function BaseUniGrid(props: IBaseUniGridProps): JSX.Element {
    const { sx, container, spacing, children, xs, sm, md, lg, xl, border, flexGrow, ...rest } = props;
    const _sx: any = border ? {...UniCommon.config.defaultBorder} : {};
    if (flexGrow) _sx.flexGrow = 1;

    if (container) {        
        return (
            <Grid
                container
                sx={{ ...UNI_GRID_CONGIG.defaultContainerSx, ..._sx, ...sx } as SxProps}
                spacing={spacing !== undefined ? spacing : UNI_GRID_CONGIG.defaultSpacing}
                {...rest}>
                {children}
            </Grid>
        )
    }

    return (
        <Grid
            sx={{ ...UNI_GRID_CONGIG.defaultItemSx, ...sx } as SxProps}
            xs={xs || UNI_GRID_CONGIG.defaultSize}
            sm={sm || UNI_GRID_CONGIG.defaultSize}
            md={md || UNI_GRID_CONGIG.defaultSize}
            lg={lg || UNI_GRID_CONGIG.defaultSize}
            xl={xl || UNI_GRID_CONGIG.defaultSize}
            {...rest}
        >
            {children}
        </Grid>
    )
}

/**
 * Renders a Grid container
 * 
 * @param props IUniGridProps
 * @returns JSX.Element
 */
export function UniGridContainer(props: IUniGridProps): JSX.Element {
    return <BaseUniGrid container {...props} />
}

/**
 * Renders a Grid item
 * 
 * @param props IUniGridItemProps
 * @returns JSX.Element
 */
export function UniGridItem(props: IUniGridItemProps): JSX.Element {
    return <BaseUniGrid {...props} />
}


/**
 * UniGrid package
 */
export const UniGrid = {
    config: UNI_GRID_CONGIG,
    Container: UniGridContainer,
    Item: UniGridItem
}

export default UniGrid;