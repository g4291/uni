import React from "react";

import UniFade from "../uni/components/animations/fade";
import UniBox from "../uni/components/primitives/box";
import { useUniTranslator } from "../uni/translator";
import UniStack from "../uni/components/primitives/stack";
import { DETAIL_UPDATE_INTERVAL, TAB_SX } from "../data/config";
import useUniScheduler from "../uni/hooks/scheduler";
import UniModalDialog from "../uni/components/primitives/modal-dialog";
import UniButton from "../uni/components/primitives/button";
import { useUniLoading } from "../uni/hooks/loading";
import { IUniEntity } from "../uni/api/hooks/entity";
import { Tab, TabList, TabPanel, Tabs } from "@mui/joy";
import UniDivider from "../uni/components/primitives/divider";
import UniDeleteEntityWithConfirmButton from "../uni/components/entity/delete-entity-button";
import UniConfirmDialog from "../uni/components/dialogs/confirm-dialog";
import EntityDetailHeader from "./entity-detail-header";



export interface IEntityDetailProps<T> {
    entity: IUniEntity<T | null>
    name: string
    onClose: () => any
    type: string
    tabs: string[]
    tabPanels: React.ReactNode[]
    closeOnEsc?: boolean
}

/**
 * EntityDetail component displays detailed information about an entity and provides options to save, close, or delete the entity.
 * It also includes tabbed navigation for different sections of the entity details.
 *
 * @template T - The type of the entity.
 * @param {IEntityDetailProps<T>} props - The properties for the EntityDetail component.
 * @returns {JSX.Element} The rendered EntityDetail component.
 *
 * @component
 *
 * @param {IEntityDetailProps<T>} props.entity - The entity object containing the details to be displayed.
 * @param {string} props.type - The type of the entity (e.g., "user", "product").
 * @param {string} props.name - The name of the entity.
 * @param {Array<string>} props.tabs - The list of tab names to be displayed.
 * @param {Array<JSX.Element>} props.tabPanels - The list of tab panels corresponding to each tab.
 * @param {Function} props.onClose - The function to be called when the modal is closed.
 * @param {boolean} [props.closeOnEsc] - Whether the modal should close when the Escape key is pressed.
 */
export default function EntityDetail<T>(props: IEntityDetailProps<T>): JSX.Element {
    const t = useUniTranslator()
    const loading = useUniLoading()
    const [tab, setTab] = React.useState(0)
    const [closeConfirm, setCloseConfirm] = React.useState(false)

    // schedule entity reload
    useUniScheduler(props.entity.reload, DETAIL_UPDATE_INTERVAL);

    const handleClose = (save?: boolean) => {
        if (save) {
            if (!props.entity.saved) props.entity.save()
            props.onClose()
            return
        }
        if (!props.entity.saved) {
            setCloseConfirm(true)
            return
        }
        props.onClose()
    }

    if (!props.entity) return <></>;

    return <>
        <UniModalDialog
            outlined
            primary
            open
            onClose={
                () => {
                    if (props.closeOnEsc) {
                        handleClose()
                    }
                }
            }
            title={<EntityDetailHeader entity={props.entity} title={t(props.type + " details") + ": " + props.name} />}
            bodySx={{ height: "1000px", width: "1000px", maxHeight: "100dvh", maxWidth: "100dvw" }}
            sx={{ p: 0 }}
            actions={
                <>
                    <UniButton
                        loading={loading.loading}
                        disabled={props.entity.modified}
                        soft
                        primary
                        onClick={() => {
                            handleClose(true)
                        }}
                    >
                        {t("save and close")}
                    </UniButton>
                    <UniButton
                        loading={loading.loading}
                        disabled={props.entity.modified || props.entity.saved}
                        soft
                        primary
                        onClick={() => {
                            props.entity.save()
                        }}
                    >
                        {t("save")}
                    </UniButton>
                    <UniButton
                        soft
                        onClick={() => { handleClose() }}
                    >
                        {t("close")}
                    </UniButton>
                    <UniDivider.V />
                    <UniDeleteEntityWithConfirmButton
                        id={props.entity.id}
                        endpoint={"/"+props.type}
                        name={t(props.type, false) + ": " + props.name}
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
                            {
                                props.tabs.map((tab, i) => {
                                    return <Tab key={i} value={i}>{t(tab)}</Tab>
                                })
                            }
                            {/* <Tab value={props.tabs.length}>{t("Photos")}</Tab> */}
                        </TabList>
                        {
                            props.tabPanels.map((panel, i) => {
                                return <TabPanel key={i} value={i} sx={{ p: 0 }}>

                                    <UniStack.Column spacing={1}>
                                        {panel}
                                    </UniStack.Column>
                                </TabPanel>
                            })
                        }
                        {/* <TabPanel value={props.tabs.length} sx={{ p: 0 }}>
                            <UniStack.Column spacing={1}>
                                <PhotoGallery photos={props.photos} entity={props.entity} entityType={props.type} exportFilename={props.photosExportFilename} />
                            </UniStack.Column>
                        </TabPanel> */}
                    </Tabs>
                </UniBox.Box>
            </UniFade>
            <UniConfirmDialog title="Data not saved" text="Do you want to discard changes?" small error show={closeConfirm} onCancel={() => { setCloseConfirm(false) }} onConfirm={() => { props.onClose() }} />
        </UniModalDialog>
    </>
}