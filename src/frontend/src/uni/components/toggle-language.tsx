
import React from "react";
import { getUniColor, getUniVariant, IUniWithColorProps, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps, UniColorProp, UniVariantProp } from "../common";
import { SxProps } from "@mui/joy/styles/types";
import { useUniLang } from "../translator";
import UniSelect, { UniSelectOption } from "./primitives/select";


export const UNI_TOGGLE_LANG_CONFIG = {
    defaultSx: {
        width: "60px"
    },
    defaultVariant: "soft",
    defaultColor: "neutral"

} as {
    defaultSx: SxProps,
    defaultColor: UniColorProp,
    defaultVariant: UniVariantProp
}

interface IUniToggleLang extends IUniWithSXProps, IUniWithSizeProps, IUniWithVariantProps, IUniWithColorProps {
    onChange?: (lang: string) => any
    label?: string
    fullWidth?: boolean
}

/**
 * Renders a toggle language component.
 *
 * @param {IUniToggleLang} props - The component props.
 * @returns {JSX.Element} The rendered toggle language component.
 */
export default function UniToggleLang(props: IUniToggleLang): JSX.Element {
    const { sx, onChange, ...rest } = props;
    const [lang, setLang, languages] = useUniLang()

    const color = React.useMemo(() => getUniColor(props, UNI_TOGGLE_LANG_CONFIG.defaultColor), [props])
    const variant = React.useMemo(() => getUniVariant(props, UNI_TOGGLE_LANG_CONFIG.defaultVariant), [props])

    if (languages.length <= 1) return <></>

    const _sx: any = { ...UNI_TOGGLE_LANG_CONFIG.defaultSx, ...sx }
    if (props.fullWidth) {
        _sx.width = "100%"
    }

    return (
            <div>
            <UniSelect
                neutral={color === "neutral"}
                primary={color === "primary"}
                error={color === "danger"}
                warning={color === "warning"}
                success={color === "success"}

                outlined={variant === "outlined"}
                solid={variant === "solid"}
                soft={variant === "soft"}
                plain={variant === "plain"}

                value={lang}
                sx={_sx as SxProps}
                onChange={(e) => {
                    setLang(e)
                    if (props.onChange) props.onChange(e)
                }}
                {...rest}
            >
                {languages.map((lang, index) => {
                    return (
                        <UniSelectOption key={index} value={lang}>{lang}</UniSelectOption>
                    )
                })}
            </UniSelect>
        </div>
    )
}