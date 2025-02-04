import React, { useEffect } from "react";
import { FormControl, FormHelperText, FormLabel, Textarea } from "@mui/joy";
import { SxProps } from "@mui/joy/styles/types";
import { getUniColor, getUniVariant, IUniWithColorProps, IUniWithDecoratorsProps, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps, UniColorProp, UniVariantProp } from "../../common";
import UniBox from "./box";


// Input config
export const UNI_TEXTAREA_CONFIG = {
    defaultMargin: 0,
    defaultSx: {
        width: 300,
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
export interface IUniTextareaProps extends IUniWithSXProps, IUniWithVariantProps, IUniWithSizeProps, IUniWithColorProps, IUniWithDecoratorsProps {
    formControlSx?: SxProps

    placeholder?: string
    helperText?: React.ReactNode
    label?: React.ReactNode

    name?: string

    // control
    value?: string | number
    onChange?: (value: string) => any
    disabled?: boolean
    fullWidth?: boolean
    required?: boolean

    minRows?: number
    maxRows?: number
    submit?: boolean
    inputRef? : React.RefObject<HTMLTextAreaElement | null>
}

/**
 * Base UniInput component
 * 
 * @param props IBaseUniSwitch
 * @returns JSX.Element
 */
export function UniTextarea(props: IUniTextareaProps): JSX.Element {
    const size = props.small ? "sm" : props.large ? "lg" : undefined;
    const variant = React.useMemo(() => getUniVariant(props, UNI_TEXTAREA_CONFIG.defaultVariant), [props])
    const _color = React.useMemo(() => getUniColor(props, UNI_TEXTAREA_CONFIG.defaultColor), [props])

    // controling
    const [value, setValue] = React.useState<string | number>("");
    const controlled = props.value !== undefined
    const hasRef = props.inputRef !== undefined
    const _value = controlled ? props.value : hasRef ? undefined : value
    const _slotProps: any = props.inputRef !== undefined? { textarea: {ref: props.inputRef}} : undefined

    useEffect(() => {
        if (props.value !== undefined) setValue(props.value)
    }, [props.value])

    const _sx: any = { ...UNI_TEXTAREA_CONFIG.defaultSx }
    const _formControlSx: any = { ...UNI_TEXTAREA_CONFIG.defaultFormControlSx }
    if (props.fullWidth) {
        _sx.width = "100%"
        _formControlSx.width = "100%"
    }

    const inputElement = (
        <Textarea
            slotProps={_slotProps}
            onKeyDown={(e: any)=>{
                if (e.key === "Enter" && e.ctrlKey && props.submit) {
                    e.preventDefault()
                    e.target?.form?.dispatchEvent(
                        new Event("submit", { cancelable: true, bubbles: true })
                    )
                }
            }}
            minRows={props.minRows}
            maxRows={props.maxRows}
            name={props.name}
            disabled={props.disabled}
            placeholder={props.placeholder}
            value={_value}
            variant={variant}
            size={size}
            color={_color}
            sx={{ m: UNI_TEXTAREA_CONFIG.defaultMargin, ..._sx, ...props.sx } as SxProps}
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

    if (props.required) {
        return (
            <FormControl required={props.required}>
                {inputElement}
            </FormControl>
        )
    }

    return inputElement
}


export default UniTextarea;