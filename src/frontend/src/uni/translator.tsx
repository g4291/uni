import React from 'react';
import { IUniWithChildrenProps } from './common';
import useUniLocalStorage from './hooks/local-storage';
import { locales } from '../data/translations';

const UNI_TRANSLATOR_CONFIG = {
    defaultStorageKey: "uni.translator.lang",
    defaultLang: "EN",
    defaultTranslations: {
        "EN": {}
    }
} as {
    defaultStorageKey: string,
    defaultLang: string,
    defaultTranslations: any
}

// Translator class
class Translator {
    dict: any
    lang: string
    
    constructor(lang: string, translations: any) {
        this.dict = {}
        this.lang = lang.toUpperCase()
        if(translations[this.lang]) {
            this.dict = translations[this.lang]
        }
    }

    private _capitalize(value: string): string {
        return (value.charAt(0).toUpperCase() + value.slice(1));
    }

    /**
     * translate
     * 
     * @param {string} keyword 
     * @param {bool} capitalize 
     * @returns 
     */
    public t(keyword: string, capitalize: boolean = true) {
        var result = "";
        if(!keyword) return ""
        const t = this.dict[keyword.toLowerCase()];

        if(t) result = t;
        else result = keyword;

        if(capitalize) result = this._capitalize(result);

        return result;

    }
}

// Context
export interface IUniTranslatorContext {
    lang?: string
    setLang?: (lang: string) => any
    translator?: Translator | null
    translations?: any
}
export const UniTranslatorContext = React.createContext<IUniTranslatorContext>({});


// Provider
export interface IUniTranslatorProps extends IUniWithChildrenProps {
    storageKey?: string
    defaultLanguage?: string
    translations?: any
}

function UniTranslatorProvider(props: IUniTranslatorProps) {
    const [lang, setLang] = useUniLocalStorage(props.storageKey || UNI_TRANSLATOR_CONFIG.defaultStorageKey, props.defaultLanguage || UNI_TRANSLATOR_CONFIG.defaultLang);
    const translations = props.translations || UNI_TRANSLATOR_CONFIG.defaultTranslations;

    const [translator, setTranslator] = React.useState<Translator | null>(null);
    const [initialized, setInitialized] = React.useState(false);

    React.useEffect(() => {
        const t = new Translator(lang, translations)
        setTranslator(t)

        // eslint-disable-next-line
    }, [lang])

    React.useEffect(() => {
        if (translator) setInitialized(true)

            // eslint-disable-next-line
    }, [translator])

    return (
        <UniTranslatorContext.Provider value={{
            lang: lang,
            setLang: setLang,
            translator: translator,
            translations: translations
        }}>
            {initialized && props.children}
        </UniTranslatorContext.Provider>
    )

}

// Hooks
export function useUniTranslator(): (v: string, capitalize?: boolean) => string {
    const { translator } = React.useContext(UniTranslatorContext)

    if(!translator) {
        return (v: string, capitalize: boolean = true) => {
            if (v === "") return ""
            if (capitalize) return v.charAt(0).toUpperCase() + v.slice(1)
            return v
        }
    }        
    return translator.t.bind(translator);
}

export function useUniLang(): [string, (lang: string) => any, string[]] {
    const ctx = React.useContext(UniTranslatorContext)
    const languages = Object.keys(ctx.translations)
    return [ctx.lang || "", ctx.setLang || (() => {}), languages]
}

export function useUniLocales(): string {
    const [lang] = useUniLang()

    return locales[lang as keyof typeof locales] || "en-US"
}


// export module
export const UniTranslator = {
    config: UNI_TRANSLATOR_CONFIG,
    ctx: UniTranslatorContext,
    Provider: UniTranslatorProvider,
    useTranslator: useUniTranslator
}


export default UniTranslator


