import React from "react";
import SvgIcon from '@mui/joy/SvgIcon';

import { IUniWithColorProps, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps } from "../common";
import UniStack from "./primitives/stack";
import UniBox from "./primitives/box";
import { useUniBreakPoint } from "../hooks/breakpoint";
import UniToggleThemeMode from "./toggle-theme-mode";
import { UniTypography as UT } from "./primitives/typography";
import UniDivider from "./primitives/divider";
import UniButton from "./primitives/button";
import UniInput from "./primitives/input";
import UniLink from "./primitives/link";
import { useUniTranslator } from "../translator";
import UniToggleLang from "./toggle-language";
import { GlobalStyles } from "@mui/joy";
import { SxProps } from "@mui/joy/styles/types";


const TRANSITION_VAR = "--uni-login-transition-duration"

export const UNI_SIGN_IN_CONFIG = {
    defaultDarkBgImageUrl: "https://images.unsplash.com/photo-1509978778156-518eea30166b",
    defaultLightBgImageUrl: "https://images.unsplash.com/photo-1709423378028-a7255e805cf6",
    defaultSideElement: true,
    transitionDuration: "0.5s",
    formSx: {
        minWidth: "350px",
        maxWidth: "400px",
        pr: "10px",
        pl: "10px"
    }

} as {
    defaultDarkBgImageUrl: string,
    defaultLightBgImageUrl: string,
    defaultSideElement: boolean,
    transitionDuration: string,
    formSx: SxProps
}

interface IUniSignIn extends IUniWithSXProps, IUniWithSizeProps, IUniWithVariantProps, IUniWithColorProps {
    headerComponent?: React.ReactNode
    footerComponent?: React.ReactNode
    sideComponent?: React.ReactNode

    onLogin?: (userName: string, password: string) => any
    onGoogleLogin?: () => any
    onForgotPassword?: () => any
    onSignUp?: () => any

    signUpHref?: string
    forgotPasswordHref?: string

    lightBgImage?: string
    darkBgImage?: string

    sideElement?: boolean
    signUp?: boolean
    googleLogin?: boolean
    forgotPassword?: boolean
    loading?: boolean
    googleLoading?: boolean
    email?: boolean
    langSelector?: boolean
    themeSelector?: boolean
    rightToLeft?: boolean
}

/**
 * Renders a sign-in component for the Uni application.
 *
 * @param props - The component props.
 * @returns The rendered sign-in component.
 */
export default function UniSignIn(props: IUniSignIn): JSX.Element {
    const t = useUniTranslator()
    const bp = useUniBreakPoint()
    const [username, setUsername] = React.useState<string>("");
    const [password, setPassword] = React.useState<string>("");

    const headerElement = (
        <UniBox.Box sx={{ p: 1, borderBottom: "1px solid", borderColor: "divider" }}>
            <UniStack.Row spacing={0}>
                <UniBox.VC fullWidth>{props.headerComponent}</UniBox.VC>
                <UniBox.HR fullWidth>
                    <UniStack.Row fullHeight spacing={1} sx={{alignItems: "center"}}>
                        {props.langSelector && <UniToggleLang small />}
                        {props.themeSelector && <UniToggleThemeMode small />}
                    </UniStack.Row>
                </UniBox.HR>
            </UniStack.Row>
        </UniBox.Box>
    )

    const signUpElement = (
        <UniBox.VHC fullHeight fullWidth>
            <GlobalStyles styles={{
                ":root": {
                    "--uni-login-transition-duration": UNI_SIGN_IN_CONFIG.transitionDuration,
                }
            }} />
            <UniStack.Column fullWidth sx={UNI_SIGN_IN_CONFIG.formSx}>
                <UT.H2>{t("Sign In")}</UT.H2>
                {
                    props.signUp && <UT.Text small>{t("are you new here?")} <UniLink href={props.signUpHref} onClick={props.onSignUp}>{t("sign up")}!</UniLink></UT.Text>
                }
                {
                    props.googleLogin && <UniStack.Column fullWidth>
                        <UniBox.Box fullWidth>
                            <UniButton
                                disabled={props.googleLoading}
                                loading={props.googleLoading}
                                sx={{ mt: 2, mb: 1 }}
                                soft
                                fullWidth
                                onClick={() => {
                                    if (props.onGoogleLogin) props.onGoogleLogin()
                                }}
                                startDecorator={!props.googleLoading && <UniGoogleIcon />}
                            >{t("continue with Google")}</UniButton>
                        </UniBox.Box>
                        <UniDivider.H fullWidth>
                            <UT.Text small>{t("or", false)}</UT.Text>
                        </UniDivider.H>
                    </UniStack.Column>
                }
                <form onSubmit={(e) => {
                    e.preventDefault()
                    if (props.onLogin) props.onLogin(username, password)
                }}>
                    <UniBox.Box fullWidth sx={{ pt: 1 }}>
                        <UniInput
                            required
                            fullWidth
                            name={props.email ? "email" : "username"}
                            label={props.email ? t("Email") : t("Username")}
                            placeholder={(props.email ? t("enter your email") : t("enter your username"))}
                            value={username}
                            onChange={(value: string) => setUsername(value)}
                        />
                    </UniBox.Box>
                    <UniBox.Box fullWidth sx={{ pt: 1, pb: 1 }}>
                        <UniInput
                            required
                            fullWidth
                            name="password"
                            label={t("Password")}
                            placeholder={t("Enter your password")}
                            password
                            value={password}
                            onChange={(value: string) => setPassword(value)}
                        />
                    </UniBox.Box>
                    {
                        props.forgotPassword && <UniBox.Box fullWidth sx={{ pt: 1 }}>
                            <UniBox.HR fullWidth>
                                <UT.Text small><UniLink href={props.forgotPasswordHref} onClick={props.onForgotPassword}>{t("forgot password?")}</UniLink></UT.Text>
                            </UniBox.HR>
                        </UniBox.Box>
                    }
                    <UniBox.Box fullWidth sx={{ pt: 1 }}>
                        <UniButton
                            submit
                            disabled={props.loading || !username || !password}
                            loading={props.loading}
                            fullWidth
                            primary
                        >{t("sign in")}</UniButton>
                    </UniBox.Box>
                </form>
            </UniStack.Column>
        </UniBox.VHC>
    )

    const footerElement = props.footerComponent && <UniBox.Box fullWidth>{props.footerComponent}</UniBox.Box>
    const sideElement = (bp !== "xs" && bp !== "sm") && <>
        <UniBox.VHC
            fullHeight
            fullWidth
            sx={{
                transition:
                    `background-image var(${TRANSITION_VAR}), left var(${TRANSITION_VAR}) !important`,
                transitionDelay: `var(${TRANSITION_VAR})`,
                backgroundImage:
                    `url(${props.lightBgImage || UNI_SIGN_IN_CONFIG.defaultLightBgImageUrl})`,
                '[data-joy-color-scheme="dark"] &': {
                    backgroundImage:
                        `url(${props.darkBgImage || UNI_SIGN_IN_CONFIG.defaultDarkBgImageUrl})`,
                },
                backgroundSize: "cover",
                backgroundPosition: "center",
                position: "relative",
            }}
        >{props.sideComponent}</UniBox.VHC>
    </>

    if (props.rightToLeft) {
        return (
            <UniStack.Row fullWidth sx={{ height: "100dvh" }} spacing={0}>
                {
                    props.sideElement === undefined
                        ? UNI_SIGN_IN_CONFIG.defaultSideElement && sideElement
                        : props.sideElement && sideElement
                }
                <UniStack.Column fullWidth fullHeight spacing={0}>
                    {headerElement}
                    {signUpElement}
                    {footerElement}
                </UniStack.Column>
            </UniStack.Row>
        )
    }

    return (
        <UniStack.Row fullWidth sx={{ height: "100dvh" }} spacing={0}>
            <UniStack.Column fullWidth fullHeight spacing={0}>
                {headerElement}
                {signUpElement}
                {footerElement}
            </UniStack.Column>
            {
                props.sideElement === undefined
                    ? UNI_SIGN_IN_CONFIG.defaultSideElement && sideElement
                    : props.sideElement && sideElement
            }
        </UniStack.Row>
    )
}

export function UniGoogleIcon() {
    return (
        <SvgIcon fontSize="xl">
            <g transform="matrix(1, 0, 0, 1, 27.009001, -39.238998)">
                <path
                    fill="#4285F4"
                    d="M -3.264 51.509 C -3.264 50.719 -3.334 49.969 -3.454 49.239 L -14.754 49.239 L -14.754 53.749 L -8.284 53.749 C -8.574 55.229 -9.424 56.479 -10.684 57.329 L -10.684 60.329 L -6.824 60.329 C -4.564 58.239 -3.264 55.159 -3.264 51.509 Z"
                />
                <path
                    fill="#34A853"
                    d="M -14.754 63.239 C -11.514 63.239 -8.804 62.159 -6.824 60.329 L -10.684 57.329 C -11.764 58.049 -13.134 58.489 -14.754 58.489 C -17.884 58.489 -20.534 56.379 -21.484 53.529 L -25.464 53.529 L -25.464 56.619 C -23.494 60.539 -19.444 63.239 -14.754 63.239 Z"
                />
                <path
                    fill="#FBBC05"
                    d="M -21.484 53.529 C -21.734 52.809 -21.864 52.039 -21.864 51.239 C -21.864 50.439 -21.724 49.669 -21.484 48.949 L -21.484 45.859 L -25.464 45.859 C -26.284 47.479 -26.754 49.299 -26.754 51.239 C -26.754 53.179 -26.284 54.999 -25.464 56.619 L -21.484 53.529 Z"
                />
                <path
                    fill="#EA4335"
                    d="M -14.754 43.989 C -12.984 43.989 -11.404 44.599 -10.154 45.789 L -6.734 42.369 C -8.804 40.429 -11.514 39.239 -14.754 39.239 C -19.444 39.239 -23.494 41.939 -25.464 45.859 L -21.484 48.949 C -20.534 46.099 -17.884 43.989 -14.754 43.989 Z"
                />
            </g>
        </SvgIcon>
    );
}