import React from "react";
import { Dropdown, Menu, MenuButton, MenuItem } from "@mui/joy";
import { SxProps } from "@mui/joy/styles/types";
import { getUniColor, getUniVariant, IUniWithChildrenProps, IUniWithColorProps, IUniWithDecoratorsProps, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps, UniColorProp, UniVariantProp } from "../../common";


// Button config
export const UNI_MENU_CONFIG = {
    defaultMargin: 0,
    defaultSx: {
    },
    defaultVariant: "solid",
    defaultColor: "neutral",
    defaultUppercase: false,
    defaultZIndex: 2000
} as {
    defaultMargin: string | number,
    defaultSx: SxProps,
    defaultVariant: UniVariantProp,
    defaultColor: UniColorProp,
    defaultUppercase: boolean,
    defaultZIndex: number
}

// props
export interface IUniMenuProps extends IUniWithChildrenProps, IUniWithSXProps, IUniWithVariantProps, IUniWithSizeProps, IUniWithDecoratorsProps, IUniWithColorProps {
    disabled?: boolean
    loading?: boolean
    menuItems?: React.ReactNode[]
    uppercase?: boolean

}

/**
 * Base UniButton component
 * 
 * @param props IBaseUniButton
 * @returns JSX.Element
 */
export function UniMenu(props: IUniMenuProps): JSX.Element {
    const { sx, small, large } = props;

    const size = small ? "sm" : large ? "lg" : undefined;
    const variant = React.useMemo(() => getUniVariant(props, UNI_MENU_CONFIG.defaultVariant), [props])
    const color = React.useMemo(() => getUniColor(props, UNI_MENU_CONFIG.defaultColor), [props])

    const _sx: any = {...UNI_MENU_CONFIG.defaultSx, ...sx}
    if (props.uppercase) {
        _sx.textTransform = "uppercase"
    }
    return (
        <Dropdown>
        <MenuButton 
        disabled={props.disabled}
        loading={props.loading}
        startDecorator={props.startDecorator}
        endDecorator={props.endDecorator}

        variant={variant} size={size}  sx={_sx as SxProps} color={color}>
            {props.children}
        </MenuButton>
        <Menu sx={{zIndex: UNI_MENU_CONFIG.defaultZIndex}}>
            {
                props.menuItems?.map((item, index) => {
                    return (
                        <MenuItem sx={{zIndex: UNI_MENU_CONFIG.defaultZIndex}} key={index}>
                            {item}
                        </MenuItem>
                    )
                })
            }
        </Menu>

        </Dropdown>
    )
}


export default UniMenu;