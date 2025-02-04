import React from "react";

import UniFade from "../uni/components/animations/fade";
import UniBox from "../uni/components/primitives/box";
import { useUniTranslator } from "../uni/translator";
import useUniTouaster from "../uni/hooks/toaster";
import { ACCEPT_IMAGES, MAX_UPLOAD_FILES, MAX_UPLOAD_SIZE } from "../data/config";
import UniModalDialog from "../uni/components/primitives/modal-dialog";
import { useUniLoading } from "../uni/hooks/loading";
import UniFileUploader, { UniB64EncodedFile } from "../uni/components/file-uploader";
import useUniApi from "../uni/api/hooks/api";
import UniButton from "../uni/components/primitives/button";


export interface IUploadPhotoProps {
    onClose: () => any
    onUploaded?: (ids: string[]) => any
}

/**
 * UploadPhoto component allows users to upload photos in base64 encoded format.
 * It handles the upload process, displays a modal dialog for file selection, 
 * and provides feedback on the upload status.
 *
 * @component
 * @param {IUploadPhotoProps} props - The properties for the UploadPhoto component.
 * @param {function} props.onClose - Callback function to handle the closing of the modal dialog.
 * @param {function} [props.onUploaded] - Optional callback function to handle the event when files are successfully uploaded.
 * @returns {JSX.Element} The rendered UploadPhoto component.
 *
 * @example
 * <UploadPhoto onClose={handleClose} onUploaded={handleUploaded} />
 */
export default function UploadPhoto(props: IUploadPhotoProps): JSX.Element {

    const t = useUniTranslator()
    const toast = useUniTouaster()
    const loading = useUniLoading()
    const api = useUniApi()
    const [uploaded, setUploaded] = React.useState<string[]>([])
    const [failed, setFailed] = React.useState<string[]>([])
    const [toUpload, setToUpload] = React.useState<UniB64EncodedFile[]>([])

    const handleClose = () => {
        props.onClose()
    }

    const uploadFiles = (files: UniB64EncodedFile[]) => {
        if (files.length === 0) return

        loading.on()
        setToUpload(files)
        for (let f of files) {
            api.post("/file/create_b64", f,
                () => {
                    setUploaded(prev => [...prev, f.id])
                },
                (e) => {
                    setFailed(prev => [...prev, f.id])
                }
            )
        }
    }

    // check if all files are uploaded
    React.useEffect(() => {
        if (toUpload.length > 0) {
            if (uploaded.length + failed.length === toUpload.length) {

                if (props.onUploaded) {
                    props.onUploaded(uploaded)
                }

                loading.off()
                if (failed.length > 0) {
                    toast("error", "photos upload failed", "error")
                    handleClose()
                    return
                }
                toast("success", "photos uploaded", "success")
                handleClose()
            }
        }
    }, [uploaded, failed, toUpload, loading, handleClose, toast])

    return <>
        <UniModalDialog
            outlined
            primary
            open
            title={t("Upload photo")}
            sx={{ maxWidth: "100%", width: "600px", p: 0 }}
            onClose={handleClose}
            actions={
                <>
                    <UniButton
                        soft
                        onClick={handleClose}
                    >
                        {t("close")}
                    </UniButton>
                </>
            }
        >
            <UniFade show>
                <UniBox.Box fullWidth fullHeight>
                    <UniFileUploader
                        loading={loading.loading}
                        accept={ACCEPT_IMAGES}
                        maxFiles={MAX_UPLOAD_FILES}
                        maxFileSize={MAX_UPLOAD_SIZE}
                        onUpload={uploadFiles}

                    />
                </UniBox.Box>
            </UniFade>
        </UniModalDialog>
    </>
}
