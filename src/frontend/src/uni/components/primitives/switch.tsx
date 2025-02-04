import React, { useEffect } from "react";
import { FormControl, FormHelperText, FormLabel, Switch } from "@mui/joy";
import { SxProps } from "@mui/joy/styles/types";
import { getUniColor, getUniVariant, IUniWithColorProps, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps, UniColorProp, UniVariantProp } from "../../common";
import {UniTypography as UT} from "./typography";


// Switch config
export const UNI_SWITCH_CONFIG = {
    defaultMargin: 0,
    defaultSx: {
    },
    defaultFormControlSx: {
        width: 200,
        justifyContent: 'space-between'
    },
    defaultVariant: "solid",
    defaultColor: "primary"
} as {
    defaultMargin: string | number,
    defaultSx: SxProps,
    defaultFormControlSx: SxProps,
    defaultVariant: UniVariantProp,
    defaultColor: UniColorProp
}

// props
export interface IUniSwitchProps extends IUniWithSXProps, IUniWithVariantProps, IUniWithSizeProps, IUniWithColorProps {
    formControlSx?: SxProps

    // labels
    label?: React.ReactNode
    helperText?: React.ReactNode
    onLabel?: React.ReactNode
    offLabel?: React.ReactNode

    // control
    checked?: boolean
    onChange?: (checked: boolean) => any
    disabled?: boolean
}

/**
 * Base UniSwitch component
 * 
 * @param props IBaseUniSwitch
 * @returns JSX.Element
 */
export function UniSwitch(props: IUniSwitchProps): JSX.Element {
    const size = props.small ? "sm" : props.large ? "lg" : undefined
    const variant = React.useMemo(() => getUniVariant(props, UNI_SWITCH_CONFIG.defaultVariant), [props])
    const _color = React.useMemo(() => getUniColor(props, UNI_SWITCH_CONFIG.defaultColor), [props])

    const [checked, setChecked] = React.useState(false);
    const controlled = props.checked !== undefined
    const _checked = controlled ? props.checked : checked

    useEffect(() => {
        if (props.checked !== undefined) setChecked(props.checked)
    }, [props.checked])


    const switchElement = (
        <Switch
            disabled={props.disabled}
            checked={_checked}
            variant={variant}
            size={size}
            color={_checked ? _color : undefined}
            sx={{ m: UNI_SWITCH_CONFIG.defaultMargin, ...UNI_SWITCH_CONFIG.defaultSx, ...props.sx } as SxProps}
            onChange={(e: React.ChangeEvent<HTMLElement>) => {
                if (!controlled) setChecked((e.target as HTMLInputElement).checked)
                if (props.onChange) props.onChange((e.target as HTMLInputElement).checked)
            }}
            endDecorator={_checked ? props.onLabel : props.offLabel}
        />
    )

    if (props.label !== undefined) {
        return (
            <FormControl
                orientation="horizontal"
                sx={{ ...UNI_SWITCH_CONFIG.defaultFormControlSx, ...props.formControlSx } as SxProps}
            >
                <div>
                    <FormLabel><UT.Text small={props.small}>{props.label}</UT.Text></FormLabel>
                    {
                        props.helperText !== undefined && <FormHelperText>{props.helperText}</FormHelperText>
                    }
                </div>
                {switchElement}
            </FormControl>
        )
    }

    return switchElement
}


export default UniSwitch;