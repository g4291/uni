import React from "react";

import UniFade from "../../uni/components/animations/fade";
import UniBox from "../../uni/components/primitives/box";
import { useUniTranslator } from "../../uni/translator";
import useUniTouaster from "../../uni/hooks/toaster";
import UniStack from "../../uni/components/primitives/stack";
import { getId } from "../../uni/utils";
import UniModalDialog from "../../uni/components/primitives/modal-dialog";
import UniButton from "../../uni/components/primitives/button";
import { useUniLoading } from "../../uni/hooks/loading";
import UniInput from "../../uni/components/primitives/input";
import useUniApi from "../../uni/api/hooks/api";
import { UniCreateUserModel } from "../../uni/datamodel";
import { UniTypography as UT } from "../../uni/components/primitives/typography";
import UniTooltip from "../../uni/components/primitives/tooltip";
import UniIcons from "../../uni/icons";


export interface IUserNew {
    onClose: () => any
    onCreated?: (id: string) => any
}

export default function UserNew(props: IUserNew): JSX.Element {
    const t = useUniTranslator()
    const toast = useUniTouaster()
    const loading = useUniLoading()
    const api = useUniApi()
    const [email, setEmail] = React.useState<string>("")
    const [password, setPassword] = React.useState<string>("")
    const [passwordCheck, setPasswordCheck] = React.useState<string>("")
    const [showPassword, setShowPassword] = React.useState<boolean>(false)

    const disabled = loading.loading || email === "" || password === "" || password !== passwordCheck


    const handleClose = () => {
        props.onClose()
    }

    const handleCreate = () => {
        if (email === "" || password === "") {
            toast("error", t("Please provide email and password"), "error")
            return
        }

        if (password !== passwordCheck) {
            toast("error", t("Passwords do not match"), "error")
            return
        }

        const createUser: UniCreateUserModel = {
            id: getId(),
            email: email,
            password: password
        }

        loading.on()
        api.post("/user/create", createUser,
            (data) => {
                toast("success", t("user created"), "success")
                loading.off()
                if (props.onCreated) {
                    props.onCreated(data.id)
                }
                handleClose()
            },
            (e) => {
                toast("error", t("user creation failed") + ": " + e.detail, "error")
                loading.off()
            }
        )
    }

    const passwordDecorator = <UniButton
        small
        plain
        onClick={() => setShowPassword(!showPassword)}
    >
        <UniTooltip title={showPassword ? t("Hide password") : t("Show password")}>
            {
                showPassword ? <UniIcons.VisibilityOff /> : <UniIcons.Visibility />
            }
        </UniTooltip>
    </UniButton>

    return <>
        <UniModalDialog
            outlined
            primary
            open
            title={t("New user")}
            bodySx={{ width: "400px", maxWidth: "100%" }}
            sx={{ p: 0 }}
            actions={
                <>
                    <UniButton
                        soft
                        onClick={handleClose}
                    >
                        {t("close")}
                    </UniButton>
                    <UniButton
                        loading={loading.loading}
                        disabled={disabled}
                        soft
                        success
                        onClick={handleCreate}
                    >
                        {t("create")}
                    </UniButton>
                </>
            }
        >
            <UniFade show>
                <UniBox.Box fullWidth fullHeight>
                    <UniStack.Column spacing={1}>

                        <UniInput
                            disabled={loading.loading}
                            fullWidth
                            small
                            error={!validateEmail(email)}
                            label={t("email")}
                            required
                            value={email}
                            onChange={(setEmail)}
                        />
                        <UniInput
                            password={!showPassword}
                            fullWidth
                            small
                            name={"new-password"}
                            required
                            error={password === ""}
                            label={t("password")}
                            value={password}
                            onChange={setPassword}
                            endDecorator={passwordDecorator}
                        />
                        <UniInput
                            password={!showPassword}
                            fullWidth
                            small
                            name={"new-password-check"}
                            required
                            disabled={password === ""}
                            error={passwordCheck !== password}
                            label={t("password check")}
                            value={passwordCheck}
                            onChange={setPasswordCheck}
                            endDecorator={passwordDecorator}
                        />
                        <UT.Text xs color="danger">
                            {
                                !validateEmail(email)
                                    ? t("Please provide a valid email")
                                    : <>
                                        &nbsp;
                                    </>
                            }
                        </UT.Text>
                        <UT.Text xs color="danger">
                            {
                                password !== passwordCheck
                                    ? t("Passwords do not match")
                                    : <>
                                        &nbsp;
                                    </>
                            }
                        </UT.Text>

                    </UniStack.Column>
                </UniBox.Box>
            </UniFade>
        </UniModalDialog>
    </>
}

function validateEmail(email: string): boolean {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return re.test(email)
}