import React, { useEffect } from "react";
import { FormControl, FormHelperText, FormLabel, Option, Select } from "@mui/joy";
import { SxProps } from "@mui/joy/styles/types";
import { getUniColor, getUniVariant, IUniWithChildrenProps, IUniWithColorProps, IUniWithDecoratorsProps, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps, UniColorProp, UniVariantProp } from "../../common";
import UniBox from "./box";
import {UniTypography as UT} from "./typography";


// Input config
export const UNI_INPUT_CONFIG = {
    defaultMargin: 0,
    defaultSx: {
        width: 200,
    },
    defaultFormControlSx: {
    },
    defaultVariant: "outlined",
    defaultColor: "primary",
    defaultFullwidth: false,
} as {
    defaultMargin: string | number,
    defaultSx: SxProps,
    defaultFormControlSx: SxProps,
    defaultVariant: UniVariantProp,
    defaultColor: UniColorProp,
    defaultFullwidth: boolean,
}

// props
export interface IUniInputProps extends IUniWithChildrenProps, IUniWithSXProps, IUniWithVariantProps, IUniWithSizeProps, IUniWithColorProps, IUniWithDecoratorsProps {
    formControlSx?: SxProps

    placeholder?: string
    helperText?: React.ReactNode
    label?: React.ReactNode

    name?: string


    // control
    value?: string | number
    onChange?: (value: any) => any
    disabled?: boolean
    fullWidth?: boolean
}

/**
 * Base UniInput component
 * 
 * @param props IBaseUniSwitch
 * @returns JSX.Element
 */
export function UniSelect(props: IUniInputProps): JSX.Element {
    const size = props.small ? "sm" : props.large ? "lg" : undefined
    const variant = React.useMemo(() => getUniVariant(props, UNI_INPUT_CONFIG.defaultVariant), [props])
    const _color = React.useMemo(() => getUniColor(props, UNI_INPUT_CONFIG.defaultColor), [props])

    // controling
    const [value, setValue] = React.useState<string | number>("")
    const controlled = props.value !== undefined
    const _value = controlled ? props.value : value

    useEffect(() => {
        if (props.value !== undefined) setValue(props.value)
    }, [props.value])

    const _sx: any = { ...UNI_INPUT_CONFIG.defaultSx }
    const _formControlSx: any = { ...UNI_INPUT_CONFIG.defaultFormControlSx }
    if (props.fullWidth) {
        _sx.width = "100%"
        _formControlSx.width = "100%"
    }


    const inputElement = (
        <Select
            name={props.name}
            disabled={props.disabled}
            placeholder={props.placeholder}
            value={_value}
            variant={variant}
            size={size}
            color={_color}
            sx={{ m: UNI_INPUT_CONFIG.defaultMargin, ..._sx, ...props.sx } as SxProps}
            onChange={
                (e, v) => {
                    if (!controlled) setValue(v || "")
                    if (props.onChange) props.onChange(v ? v.toString() : "")
                }
            }
            startDecorator={props.startDecorator}
            endDecorator={props.endDecorator}
        >{props.children}</Select>
    )

    if (props.label !== undefined || props.helperText !== undefined) {
        return (
            <FormControl
                orientation="horizontal"
                sx={{ ..._formControlSx, ...props.formControlSx } as SxProps}
            >
                <UniBox.Box fullWidth={props.fullWidth}>
                    {props.label && <FormLabel sx={{ pb: 1 }}>{props.label}</FormLabel>}
                    {inputElement}
                    {
                        props.helperText !== undefined && <FormHelperText><UT.Text xs>{props.helperText}</UT.Text></FormHelperText>
                    }
                </UniBox.Box>
            </FormControl>
        )
    }

    return inputElement
}

export const UniSelectOption = Option;


export default UniSelect;