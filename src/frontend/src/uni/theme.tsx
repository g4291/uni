import React from "react";
import { CssBaseline, CssVarsProvider, CssVarsThemeOptions, extendTheme, useColorScheme, useTheme } from "@mui/joy";
import { IUniWithChildrenProps, UniThemeMode } from "./common";


// Theme config
const UNI_THEME_CONFIG = {
    defaultStorageKey: "uni.theme.mode",
    defaultThemeMode: "light" as UniThemeMode,
    defaultThemeOptions: {
        "colorSchemes": {
            "light": {
                "palette": {

                }
            },
            "dark": {
                "palette": {
                    "primary": {

                    }
                }
            }
        }
    }
} as {
    defaultStorageKey: string,
    defaultThemeMode: UniThemeMode,
    defaultThemeOptions: CssVarsThemeOptions,
}

// context
export interface IUniThemeContext {
    storageKey: {
        get: () => string,
        set: React.Dispatch<React.SetStateAction<string>>
    }

}
export const UniThemeContext = React.createContext<IUniThemeContext>({} as IUniThemeContext);

// provider
export interface IUniThemeProviderProps extends IUniWithChildrenProps {
    themeStorageKey?: string
    themeOptions?: CssVarsThemeOptions
}
function UniThemeProvider(props: IUniThemeProviderProps): JSX.Element {
    const [storageKey, setStorageKey] = React.useState(props.themeStorageKey || UNI_THEME_CONFIG.defaultStorageKey)
    const themeOpts = {
        cssVarPrefix: "mode-toggle",
        ...UNI_THEME_CONFIG.defaultThemeOptions,
        ...props.themeOptions
    }
    const theme = extendTheme(themeOpts)
    
    return (
        <UniThemeContext.Provider value={{
            storageKey: {
                get: () => storageKey,
                set: setStorageKey
            }
        }}>
            <CssVarsProvider theme={theme} modeStorageKey={storageKey}>
                <CssBaseline />
                {props.children}
            </CssVarsProvider>
        </UniThemeContext.Provider>
    )
}

/**
 * Hook to get and set the current UniThemeMode
 * 
 * @returns [UniThemeMode, (mode: UniThemeMode | null) => void]
 */
export function useUniThemeMode(): [UniThemeMode, (mode: UniThemeMode | null) => void] {
    const { mode, setMode } = useColorScheme()
    return [mode, setMode as (mode: UniThemeMode | null) => void]
}

/**
 * Hook to get the current UniColorScheme
 * 
 * @returns UniColorScheme
 */
export const useUniColorScheme = useColorScheme

/**
 * Hook to get the current UniTheme
 * 
 * @returns UniThemeMode
 */
export const useUniTheme = useTheme

/**
 * Extend the UniTheme
 * 
 * @param themeOptions CssVarsThemeOptions
 */
export const extendUniTheme = extendTheme

/**
 * UniModalDialog package
 */
export const UniTheme = {
    config: UNI_THEME_CONFIG,
    ctx: UniThemeContext,
    Provider: UniThemeProvider,
    useThemeMode: useUniThemeMode,
    extendTheme: extendUniTheme

}

export default UniTheme;