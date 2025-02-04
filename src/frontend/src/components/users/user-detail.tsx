import React from "react";

import UniFade from "../../uni/components/animations/fade";
import UniBox from "../../uni/components/primitives/box";
import { UniTypography as UT } from "../../uni/components/primitives/typography";
import { useUniTranslator } from "../../uni/translator";
import useUniTouaster from "../../uni/hooks/toaster";
import UniStack from "../../uni/components/primitives/stack";
import { copyObject } from "../../uni/utils";
import { TAB_SX } from "../../data/config";
import useUniScheduler from "../../uni/hooks/scheduler";
import UniModalDialog from "../../uni/components/primitives/modal-dialog";
import UniButton from "../../uni/components/primitives/button";
import { useUniLoading } from "../../uni/hooks/loading";
import useUniEntity, { IUniEntity } from "../../uni/api/hooks/entity";
import { Tab, TabList, TabPanel, Tabs } from "@mui/joy";
import UniGrid from "../../uni/components/primitives/grid";
import UniInput from "../../uni/components/primitives/input";
import UniTextarea from "../../uni/components/primitives/textarea";
import UniCard from "../../uni/components/primitives/card";
import UniDivider from "../../uni/components/primitives/divider";
import UniDeleteEntityWithConfirmButton from "../../uni/components/entity/delete-entity-button";
import useUniEntityFiles from "../../uni/api/hooks/entity-files";
import { UniFile } from "../../uni/datamodel";
import UniCipyContentButton from "../../uni/components/copy-content";
import { IUniUser } from "../../uni/api/common";
import UniIcons from "../../uni/icons";
import UniTooltip from "../../uni/components/primitives/tooltip";
import useUniApi from "../../uni/api/hooks/api";
import UniSwitch from "../../uni/components/primitives/switch";
import useUniUser from "../../uni/api/hooks/user";


interface IUserDetailElementProps {
    entity: IUniEntity<IUniUser | null>
}
interface IUserDetailSummaryProps extends IUserDetailElementProps {
    photos: UniFile[]
}
function UserDetailSummary(props: IUserDetailSummaryProps) {
    const t = useUniTranslator();
    const entity = props.entity;

    if (!entity.buffer) return null;

    const hasAvatar = entity.buffer.avatar !== ""
    return (<>
        <UniBox.Box fullWidth>
            <UniFade show>
                <UniGrid.Container spacing={1}>
                    <UniGrid.Item xs={12} md={hasAvatar ? 6 : 12}>
                        <UniCard
                            fullWidth
                            soft
                        >
                            <UniStack.Column spacing={1}>
                                <UniStack.Row spacing={1}>
                                    <UniBox.Box fullWidth><UniInput
                                        small
                                        fullWidth
                                        label={t("first name")}
                                        value={entity.buffer.first_name}
                                        disabled
                                    /></UniBox.Box>
                                    <UniBox.VHC><UniCipyContentButton content={entity.buffer.first_name} /></UniBox.VHC>
                                </UniStack.Row>
                                <UniStack.Row spacing={1}>
                                    <UniBox.Box fullWidth><UniInput
                                        small
                                        fullWidth
                                        label={t("last name")}
                                        value={entity.buffer.last_name}
                                        disabled
                                    /></UniBox.Box>
                                    <UniBox.VHC><UniCipyContentButton content={entity.buffer.last_name} /></UniBox.VHC>
                                </UniStack.Row>
                                <UniStack.Row spacing={1}>
                                    <UniBox.Box fullWidth><UniInput
                                        small
                                        fullWidth
                                        label={t("email")}
                                        value={entity.buffer.email}
                                        disabled
                                    /></UniBox.Box>
                                    <UniBox.VHC><UniCipyContentButton content={entity.buffer.email} /></UniBox.VHC>
                                </UniStack.Row>
                                <UniStack.Row spacing={1}>
                                    <UniBox.Box fullWidth><UniInput
                                        small
                                        fullWidth
                                        label={t("admin")}
                                        value={t(entity.buffer.root ? "true" : "false")}
                                        disabled
                                    /></UniBox.Box>
                                    <UniBox.VHC><UniCipyContentButton content={entity.buffer.email} /></UniBox.VHC>
                                </UniStack.Row>
                            </UniStack.Column>
                        </UniCard>
                    </UniGrid.Item>
                    {
                        hasAvatar && <UniGrid.Item xs={12} md={6}>
                            <UniBox.VHC fullWidth fullHeight>
                                <img src={entity.buffer.avatar} alt="avatar" style={{ borderRadius: "50%" }} />

                            </UniBox.VHC>
                        </UniGrid.Item>
                    }
                    <UniGrid.Item xs={12}>
                        <UniCard
                            fullWidth
                            soft
                            header={<UT.Title>{t("note")}</UT.Title>}
                        >
                            <UniTextarea
                                small
                                value={entity.buffer.note}
                                disabled
                                minRows={4}
                                maxRows={8}
                                fullWidth
                            />
                            <UniBox.HR fullWidth><UniCipyContentButton content={entity?.buffer.note || ""} /></UniBox.HR>
                        </UniCard>
                    </UniGrid.Item>
                </UniGrid.Container>
            </UniFade>
        </UniBox.Box >
    </>

    )
}

function UserDetailGeneral(props: IUserDetailElementProps) {
    const t = useUniTranslator();
    const entity = props.entity;

    if (!entity.buffer) return null;

    return (<>
        <UniCard
            fullWidth
            soft
            header={<UT.Title>{t("name")}</UT.Title>}
        >
            <UniGrid.Container spacing={1}>
                <UniCard
                    fullWidth
                    soft
                >
                    <UniStack.Column spacing={1}>
                        <UniStack.Row spacing={1}>
                            <UniBox.Box fullWidth><UniInput
                                small
                                fullWidth
                                label={t("first name")}
                                value={entity.buffer.first_name}
                                onChange={(v) => {
                                    const buff = copyObject(entity.buffer)
                                    buff.first_name = v
                                    entity.updateBuffer(buff, false)
                                }}
                            /></UniBox.Box>
                        </UniStack.Row>
                        <UniStack.Row spacing={1}>
                            <UniBox.Box fullWidth><UniInput
                                small
                                fullWidth
                                label={t("last name")}
                                value={entity.buffer.last_name}
                                onChange={(v) => {
                                    const buff = copyObject(entity.buffer)
                                    buff.last_name = v
                                    entity.updateBuffer(buff, false)
                                }}
                            /></UniBox.Box>
                        </UniStack.Row>
                    </UniStack.Column>


                </UniCard>
            </UniGrid.Container>

        </UniCard>

        <UniTextarea
            value={entity.buffer.note}
            label={t("note", true)}
            minRows={4}
            maxRows={8}
            fullWidth
            onChange={(v) => {
                const buff = copyObject(entity.buffer)
                buff.note = v
                entity.updateBuffer(buff, false)
            }}
        />
    </>

    )
}

function UserDetailPassword(props: IUserDetailElementProps) {
    const t = useUniTranslator()
    const toast = useUniTouaster()
    const api = useUniApi()
    const loading = useUniLoading()
    const entity = props.entity;

    const [password, setPassword] = React.useState("")
    const [passwordCheck, setPasswordCheck] = React.useState("")
    const [showPassword, setShowPassword] = React.useState(false)

    if (!entity.buffer) return null;

    const handlePasswordChange = () => {
        if (password === "") {
            toast("error", t("Please provide a password"), "error")
            return
        }
        if (password !== passwordCheck) {
            toast("error", t("Passwords do not match"), "error")
            return
        }

        loading.on()
        api.post("/user/password/change", { user_id: entity.id, password: password },
            () => {
                toast("success", t("Password changed"), "success")
                loading.off()
                setPassword("")
                setPasswordCheck("")
                loading.off()
            },
            (e) => {
                toast("error", t("Password change failed") + ": " + e.detail, "error")
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



    return (<>
        <UniCard
            fullWidth
            soft
            header={<UT.Title>{t("Password change")}</UT.Title>}
        >
            <UniGrid.Container spacing={1}>
                <UniCard
                    fullWidth
                    soft
                >
                    <UniStack.Column spacing={1}>
                        <UniStack.Row spacing={1}>
                            <UniBox.Box fullWidth><UniInput
                                password={!showPassword}
                                small
                                sx={{ maxWidth: "300px", width: "100%" }}
                                name={"new-password"}
                                required
                                error={password === ""}
                                label={t("password")}
                                value={password}
                                onChange={setPassword}
                                endDecorator={passwordDecorator}
                            /></UniBox.Box>
                        </UniStack.Row>
                        <UniStack.Row spacing={1}>
                            <UniBox.Box fullWidth><UniInput
                                password={!showPassword}
                                small
                                sx={{ maxWidth: "300px", width: "100%" }}
                                name={"new-password-check"}
                                required
                                disabled={password === ""}
                                error={passwordCheck !== password}
                                label={t("password check")}
                                value={passwordCheck}
                                onChange={setPasswordCheck}
                                endDecorator={passwordDecorator}
                            /></UniBox.Box>
                        </UniStack.Row>
                        <UniBox.HR fullWidth sx={{ pt: 1 }}>
                            <UniButton
                                soft
                                small
                                error
                                disabled={password === "" || passwordCheck !== password}
                                loading={loading.loading}
                                onClick={handlePasswordChange}
                            >
                                {t("change password")}
                            </UniButton>
                        </UniBox.HR>
                    </UniStack.Column>


                </UniCard>
            </UniGrid.Container>

        </UniCard>
    </>

    )
}

function UserDetailPermissions(props: IUserDetailElementProps) {
    const t = useUniTranslator()
    const toast = useUniTouaster()
    const api = useUniApi()
    const loading = useUniLoading()
    const entity = props.entity;
    const [currentUser] = useUniUser()
    const [root, setRoot] = React.useState(false)

    const handleRootChange = () => {
        loading.on()
        api.post("/user/root/change", { user_id: entity.id, root: root },
            () => {
                toast("success", t("permission changed"), "success")
                entity.reload()
                loading.off()
            },
            (e) => {
                toast("error", t("permission change failed") + ": " + e.detail, "error")
                entity.reload()
                loading.off()
            }
        )
    }

    React.useEffect(() => {
        if (!entity.data) return
        setRoot(entity.data.root)
    }, [entity.data])

    if (!entity.buffer) return null;

    const disabled = entity.data?.root === root || entity.data?.id === currentUser.id

    return (<>
        <UniCard
            fullWidth
            soft
            header={<UT.Title>{t("Permissions")}</UT.Title>}
        >
            <UniGrid.Container spacing={1}>
                <UniCard
                    fullWidth
                    soft
                >
                    <UniStack.Column spacing={1}>
                        <UniSwitch
                            label={t("admin")}
                            checked={root}
                            onChange={(v) => {
                                setRoot(v)
                                const buff = copyObject(entity.buffer)
                                buff.root = v
                                entity.updateBuffer(buff, false)
                            }}
                        />
                        <UniBox.HR fullWidth sx={{ pt: 1 }}>
                            <UniButton
                                soft
                                small
                                error
                                disabled={disabled}
                                loading={loading.loading}
                                onClick={handleRootChange}
                            >
                                {t("confirm")}
                            </UniButton>
                        </UniBox.HR>
                    </UniStack.Column>
                </UniCard>
            </UniGrid.Container>
        </UniCard>
    </>

    )
}

export interface IProductDetailProps {
    productId: string
    onClose: () => any
}

export default function UserDetail(props: IProductDetailProps): JSX.Element {
    const t = useUniTranslator()
    const loading = useUniLoading()
    const entity = useUniEntity<IUniUser>("/user", props.productId)
    const [tab, setTab] = React.useState(0)
    useUniScheduler(entity.reload, 10000);
    const photos = useUniEntityFiles(entity?.data, "photo_ids")

    const disabled = false;

    const handleClose = () => {
        props.onClose()
    }

    if (!entity) return <></>;

    return <>
        <UniModalDialog
            outlined
            primary
            open
            title={t("User details") + ": " + entity.buffer?.email || ""}
            bodySx={{ maxHeight: "95dvh", height: "800px", width: "800px", maxWidth: "95%" }}
            // onClose={handleClose}
            sx={{ p: 0 }}
            actions={
                <>
                    <UniButton
                        loading={loading.loading}
                        disabled={disabled}
                        soft
                        primary
                        onClick={() => {
                            entity.save()
                        }}
                    >
                        {t("save")}
                    </UniButton>
                    <UniButton
                        disabled={disabled}
                        soft
                        onClick={handleClose}
                    >
                        {t("close")}
                    </UniButton>
                    <UniDivider.V />
                    <UniDeleteEntityWithConfirmButton
                        id={entity.id}
                        endpoint="/user"
                        name="user"
                        onSuccess={handleClose}
                        soft
                        error
                    >
                        {t("delete")}
                    </UniDeleteEntityWithConfirmButton>
                </>
            }
        >
            <UniFade show>
                <UniBox.Box fullWidth fullHeight>
                    <Tabs value={tab} onChange={(e, v) => setTab(v as number)} variant="plain" >
                        <TabList
                            disableUnderline
                            sx={TAB_SX}
                        >
                            <Tab value={0}>{t("Summary")}</Tab>
                            <Tab value={1}>{t("General")}</Tab>
                            <Tab value={2}>{t("Permissions")}</Tab>
                            <Tab value={3}>{t("Password")}</Tab>
                        </TabList>
                        <TabPanel value={0} sx={{ p: 0 }}>
                            <UniStack.Column spacing={1}>
                                <UserDetailSummary photos={photos} entity={entity} />
                            </UniStack.Column>
                        </TabPanel>
                        <TabPanel value={1} sx={{ p: 0 }}>
                            <UniStack.Column spacing={1}>
                                <UserDetailGeneral entity={entity} />
                            </UniStack.Column>
                        </TabPanel>
                        <TabPanel value={2} sx={{ p: 0 }}>
                            <UniStack.Column spacing={1}>
                                <UserDetailPermissions entity={entity} />
                            </UniStack.Column>
                        </TabPanel>
                        <TabPanel value={3} sx={{ p: 0 }}>
                            <UniStack.Column spacing={1}>
                                <UserDetailPassword entity={entity} />
                            </UniStack.Column>
                        </TabPanel>
                    </Tabs>
                </UniBox.Box>
            </UniFade>
        </UniModalDialog>
    </>
}