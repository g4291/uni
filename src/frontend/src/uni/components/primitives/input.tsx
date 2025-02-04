import React, { useEffect } from "react";
import { FormControl, FormHelperText, FormLabel, Input } from "@mui/joy";
import { SxProps } from "@mui/joy/styles/types";
import { getUniColor, getUniVariant, IUniWithColorProps, IUniWithDecoratorsProps, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps, UniColorProp, UniVariantProp } from "../../common";
import UniBox from "./box";


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
export interface IUniInputProps extends IUniWithSXProps, IUniWithVariantProps, IUniWithSizeProps, IUniWithColorProps, IUniWithDecoratorsProps {
    formControlSx?: SxProps

    placeholder?: string
    helperText?: React.ReactNode
    label?: React.ReactNode

    name?: string

    password?: boolean
    number?: boolean

    // control
    value?: string | number
    onChange?: (value: string) => any
    disabled?: boolean
    fullWidth?: boolean
    required?: boolean
}

/**
 * Base UniInput component
 * 
 * @param props IBaseUniSwitch
 * @returns JSX.Element
 */
export function UniInput(props: IUniInputProps): JSX.Element {
    const size = props.small ? "sm" : props.large ? "lg" : undefined;
    const variant = React.useMemo(() => getUniVariant(props, UNI_INPUT_CONFIG.defaultVariant), [props])
    const _color = React.useMemo(() => getUniColor(props, UNI_INPUT_CONFIG.defaultColor), [props])

    // controling
    const [value, setValue] = React.useState<string | number>("");
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
        <Input
            type={props.password ? "password" : props.number ? "number" : "text"}
            name={props.name}
            disabled={props.disabled}
            placeholder={props.placeholder}
            value={_value}
            variant={variant}
            size={size}
            color={_color}
            sx={{ m: UNI_INPUT_CONFIG.defaultMargin, ..._sx, ...props.sx } as SxProps}
            onChange={(e: React.ChangeEvent<HTMLElement>) => {
                if (!controlled) setValue((e.target as HTMLInputElement).value)
                if (props.onChange) props.onChange((e.target as HTMLInputElement).value)
            }}
            startDecorator={props.startDecorator}
            endDecorator={props.endDecorator}
        />
    )

    if (props.label !== undefined || props.helperText !== undefined) {
        return (
            <FormControl
                required={props.required}
                orientation="horizontal"
                sx={{ ..._formControlSx, ...props.formControlSx } as SxProps}
            >
                <UniBox.Box fullWidth={props.fullWidth}>
                    {props.label && <FormLabel sx={{ pb: 1 }}>{props.label}</FormLabel>}
                    {inputElement}
                    {
                        props.helperText !== undefined && <FormHelperText>{props.helperText}</FormHelperText>
                    }
                </UniBox.Box>
            </FormControl>
        )
    }

    return (
        <FormControl required={props.required}>
            {inputElement}
        </FormControl>
    )

}


export default UniInput;