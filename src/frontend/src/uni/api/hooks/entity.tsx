import React from "react";
import useUniApi from "./api";
import { IUniLoading, useUniLoading } from "../../hooks/loading";
import useUniTouaster from "../../hooks/toaster";
import useUniPrevious from "../../hooks/previous";
import { compareObjects, copyObject } from "../../utils";
import { UniTypography as UT } from "../../components/primitives/typography";
import { useUniTranslator } from "../../translator";
import UniFade from "../../components/animations/fade";


export interface IUniEntity<T> {
    id: string,
    data: T;
    buffer: T;
    modified: boolean;
    clearModified: () => void;
    reload: (reloadBuffer?: boolean) => void;
    updateBuffer: (entity: T, save: boolean) => void;
    save: () => void;
    handleForm: (data: any, field: string) => void;
    endpoint: string
    loading: IUniLoading,
    saved: boolean,
    info: React.ReactNode
}

/**
 * Custom hook to manage the state and operations of a UniEntity.
 * 
 * @template T - The type of the entity.
 * @param {string} endpoint - The API endpoint to fetch and update the entity.
 * @param {string} id - The unique identifier of the entity.
 * @returns {IUniEntity<T | null>} An object containing the entity state and various utility functions.
 * 
 * @typedef {Object} IUniEntity
 * @property {string} id - The unique identifier of the entity.
 * @property {T | null} data - The current state of the entity.
 * @property {T | null} buffer - The work buffer for the entity.
 * @property {boolean} modified - Indicates if the entity has been modified.
 * @property {Function} clearModified - Function to clear the modified state.
 * @property {Function} reload - Function to reload the entity from the server.
 * @property {Function} updateBuffer - Function to update the work buffer and optionally save the entity.
 * @property {Function} save - Function to save the entity.
 * @property {Function} handleForm - Function to handle form data changes.
 * @property {string} endpoint - The API endpoint.
 * @property {Object} loading - The loading state.
 * @property {boolean} saved - Indicates if the entity has been saved.
 * @property {React.ReactNode} info - The info element to display modification and save status.
 */
export function useUniEntity<T>(endpoint: string, id: string): IUniEntity<T | null> {
    const t = useUniTranslator()
    const api = useUniApi()
    const loading = useUniLoading()
    const toast = useUniTouaster()

    // entity states
    const [entity, setEntity] = React.useState<T | null>(null);
    const [workBuffer, setWorkBuffer] = React.useState<T | null>(null);
    const prevEntity = useUniPrevious(entity);
    const [saved, setSaved] = React.useState<boolean>(true)

    // modified
    const [modified, setModified] = React.useState(false)
    const clearModified = () => {
        setModified(false);
    }

    // modification check
    // compare with previous entity
    React.useEffect(() => {
        if (entity && prevEntity) {

            // buffer updated, nothing to check
            if (compareObjects(entity, workBuffer)) return

            if (!compareObjects((prevEntity as any).updated, (entity as any).updated)) {
                setModified(true)
            }
        }

        // eslint-disable-next-line
    }, [entity])

    React.useEffect(() => {
        if (workBuffer && entity) {
            if (!compareObjects(workBuffer, entity)) {
                setSaved(false)
            } else {
                setSaved(true)
            }
        }
        
        // eslint-disable-next-line
    }, [workBuffer])

    // reload entity
    const reload = React.useCallback(
        (reloadBuffer: boolean = false) => {
            if (!id) {
                setEntity(
                    null
                )
                setWorkBuffer(
                    null
                )

                return
            }
            loading.on()
            api.post(endpoint + "/get?entity_id=" + id, {}, (result) => {
                // reload entity
                setEntity(
                    copyObject(result) as T
                )

                // reload workBuffer?
                if (!workBuffer || (reloadBuffer)) {
                    setWorkBuffer(
                        copyObject(result) as T
                    )
                    setModified(false)
                    setSaved(true)
                }
                loading.off()

            },
                (e) => {
                    toast("error", e.detail, "error")
                    loading.off()
                })

        }, [id, api, workBuffer, loading, endpoint, toast]
    )

    // save entity
    const _save = React.useCallback((e: T | null) => {
        if (!entity) return

        // diff
        const diff: any = Object();
        for (let i in e) {
            if (!compareObjects(e[i], entity[i])) {
                diff[i] = e[i];
            }
        }

        // nothing changed
        if (compareObjects(diff, {})) {
            toast("info", "Nothing to save", "info")
            return
        };

        // assign id
        diff.id = id;
        loading.on()
        api.post(endpoint + "/update", diff,
            () => {
                reload(true);
                toast("success", "Saved", "success")
                loading.off()
            },
            (error) => {
                toast("error", error.detail, "error")
                reload(true);
                loading.off()

            })
    }, [entity, id, api, reload, loading, endpoint, toast])

    // update entity
    const update = React.useCallback(
        (e: T | null, save: boolean) => {
            setWorkBuffer(
                { ...e } as T
            )
            // save on server?
            if (save) _save(e)
        }, [_save]
    )

    // save entity
    const save = React.useCallback(
        () => {
            _save(workBuffer);
        }, [_save, workBuffer]
    );

    const handleForm = (data: any, field: string) => {
        if (!workBuffer) return
        const _buffer: any = { ...workBuffer }
        _buffer[field] = data
        setWorkBuffer(_buffer)
    }

    // init
    React.useEffect(() => {
        reload();

        // eslint-disable-next-line
    }, [id]);


    const infoElement = React.useMemo(() => {
        if (!modified && saved) return null

        return <>
            {
                modified && <UniFade show>
                    <UT.Text xs color="danger" sx={{ border: "1px solid", borderColor: "danger.500", borderRadius: "5px", p: 1, width: "fit-content", height: "100%", alignContent: "center" }}>
                        {t("data changed on server, please reload")}
                        {/* <UniButton sx={{ml: 1, }} onClick={() => reload(true)} small plain neutral endDecorator={<UniIcons.Refresh />}>&nbsp;</UniButton> */}
                    </UT.Text>
                </UniFade>
            }
            {
                !saved && <UniFade show><UT.Text xs color="danger" sx={{ border: "1px solid", borderColor: "danger.500", borderRadius: "5px", p: 1, width: "fit-content", height: "100%", alignContent: "center" }}>{t("data not saved")}</UT.Text></UniFade>
            }
        </>

    }, [modified, saved, t])

    // return IUniEntity
    return {
        id: id,
        data: entity,
        buffer: workBuffer,
        modified: modified,
        clearModified: clearModified,
        reload: reload,
        updateBuffer: update,
        save: save,
        handleForm,
        endpoint: endpoint,
        loading: loading,
        saved: saved,
        info: infoElement
    }
}


export default useUniEntity