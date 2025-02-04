import React from "react"
import { Accept, useDropzone } from 'react-dropzone'

import { UniColorProp } from "../common"
import UniButton from "./primitives/button"
import { useUniTranslator } from "../translator"
import UniIcons from "../icons"
import useUniTouaster from "../hooks/toaster"
import UniStack from "./primitives/stack"
import UniCard, { IUniCardProps } from "./primitives/card"
import UniTooltip from "./primitives/tooltip"
import UniFade from "./animations/fade"
import { useUniLoading } from "../hooks/loading"
import UniProgress from "./primitives/progress"
import UniBox from "./primitives/box"
import { UniTypography as UT } from "./primitives/typography"
import { fileSize, getId } from "../utils"


export const UNI_FILE_UPLOADER_CONFIG = {
    defaultSx: {

    },
    loaderColor: "warning",
    defaultListMaxHeight: "200px",

} as {
    loaderColor: UniColorProp
    defaultListMaxHeight: string
}

// Define the B64EncodedFile interface
export interface UniB64EncodedFile {
    filename: string
    size: number
    data: string
    mime_type: string
    path?: string
    id: string
}

export type UniAccept = Accept

// Props interface for the UniFileUploader component
export interface IUniFileUploaderProps extends IUniCardProps {
    onChange?: (files: UniB64EncodedFile[]) => void // Function to handle file changes
    accept: UniAccept // Array of allowed MIME types
    maxFiles: number // Maximum number of files allowed
    maxFileSize: number // Maximum file size in bytes
    header?: React.ReactNode
    onUpload?: (files: UniB64EncodedFile[]) => void
    loading?: boolean
}

function UniFileUploader(props: IUniFileUploaderProps): JSX.Element {
    const { onChange, onUpload, accept, maxFiles, maxFileSize, header, loading, ...rest } = props

    const [fileList, setFileList] = React.useState<UniB64EncodedFile[]>([]) // State to hold the list of files
    const toast = useUniTouaster()
    const t = useUniTranslator()
    const _loading = useUniLoading()

    // Handle dropped files
    const onDrop = React.useCallback((acceptedFiles: File[]) => {
        _loading.on()

        if (fileList.length + acceptedFiles.length > maxFiles) {
            toast("error", "uploader: too many files", "error")
            _loading.off()
            return
        }

        // Process accepted files
        for (let file of acceptedFiles) {
            if (file.size > maxFileSize) {
                toast(file.name, "uploader: file too large", "error")
                _loading.off()
                return
            }
            convertFileToB64(file, accept, (file as any).path).then((b64File) => {
                setFileList((prev) => {
                    const updatedList = [...prev, b64File]
                    _loading.off()
                    return updatedList
                })
            })
        }
        _loading.off()
    }, [fileList, maxFiles, maxFileSize, accept, toast, _loading])

    // Handle file deletion
    const handleDelete = (fileToDelete: UniB64EncodedFile) => {
        const updatedFiles = fileList.filter((file) => file.id !== fileToDelete.id)
        setFileList(updatedFiles)
    }

    React.useEffect(() => {
        if (onChange) onChange(fileList)

        // eslint-disable-next-line
    }, [fileList])

    const dropZone = useDropzone({ onDrop, accept: accept })

    return (
        <UniCard
            fullWidth {...rest}
            header={header}
            actions={
                <UniFade show={fileList.length > 0}>
                    <UniStack.Row spacing={1}>
                        <UniButton onClick={() => setFileList([])} small soft error>
                            {t("clear")}
                        </UniButton>
                        <UniButton onClick={() => {
                            if (onUpload) onUpload([...fileList])
                            setFileList([])
                        }} small success soft>
                            {t("upload")}
                        </UniButton>
                    </UniStack.Row>
                </UniFade>
            }
        >
            {
                !_loading.loading && (!loading) && <div {...dropZone.getRootProps()} >
                    <UniBox.VHC fullWidth border sx={{ borderStyle: "dashed", p: "30px" }}>

                        <input {...dropZone.getInputProps()} />
                        {
                            dropZone.isDragActive
                                ? <UT.Text>{t("Drop the files here ...")}</UT.Text>
                                : <>
                                    <UniStack.Column spacing={1}>
                                        <UT.Text color="neutral">{t("Drag 'n' drop some files here, or click to select files")}</UT.Text>
                                        <UT.Text color="neutral" xs>{JSON.stringify(accept, null, 2)}</UT.Text>
                                    </UniStack.Column>
                                </>
                        }
                    </UniBox.VHC>
                </div>
            }
            <UniFade show={fileList.length > 0}>

                <UniStack.Column fullWidth spacing={1} sx={{ mt: 1, maxHeight: "200px", overflowX: "auto", scrollbarWidth: "thin" }}>
                    {fileList.map((file, index) => (
                        <UniCard soft small fullWidth key={index}>
                            <UniStack.Row fullWidth>
                                <UniBox.Box fullWidth>
                                    <UT.Text small>{file.filename}</UT.Text>
                                    <UT.Text xs>{fileSize(file.size)}, {file.mime_type}</UT.Text>
                                </UniBox.Box>
                                <UniBox.Box>
                                    <UniButton onClick={() => handleDelete(file)} small soft error>
                                        <UniTooltip title={t("delete")}>
                                            <UniIcons.Delete />
                                        </UniTooltip>
                                    </UniButton>
                                </UniBox.Box>
                            </UniStack.Row>
                        </UniCard>
                    ))}
                </UniStack.Column>
            </UniFade>
            {
                (_loading.loading || (loading || false)) && <UniBox.VHC fullWidth sx={{ pt: 2 }}>
                    <UniFade show>
                        <UniProgress.Circular color={UNI_FILE_UPLOADER_CONFIG.loaderColor} />
                    </UniFade>
                </UniBox.VHC>
            }

        </UniCard>
    )
}

/**
 * Retrieves the MIME type based on the file extension from the given filename.
 *
 * @param filename - The name of the file from which to extract the extension.
 * @param mime_types - An object where keys are MIME types and values are arrays of file extensions.
 * @returns The MIME type corresponding to the file extension, or an empty string if no match is found.
 */
function getMimeTypeFromFilename(filename: string, mime_types: UniAccept): string {

    const ext = filename.split('.').pop()
    if (!ext) {
        return ""
    }

    for (let key in mime_types) {
        if (mime_types[key].includes("." + ext)) {
            return key
        }
    }

    return ""
}

/**
 * Converts a given file to a base64 encoded string.
 *
 * @param {File} file - The file to be converted.
 * @param {string} [path] - Optional path associated with the file.
 * @returns {Promise<UniB64EncodedFile>} A promise that resolves to an object containing the base64 encoded file data and metadata.
 */
const convertFileToB64 = (file: File, accept: UniAccept, path?: string): Promise<UniB64EncodedFile> => {

    return new Promise<UniB64EncodedFile>((resolve) => {
        const reader = new FileReader()
        reader.onloadend = () => {
            const b64data = reader.result
            if (typeof b64data === 'string') {
                resolve({
                    id: getId(),
                    filename: file.name,
                    path: path,
                    size: file.size,
                    data: b64data,
                    mime_type: getMimeTypeFromFilename(file.name, accept)
                })
            }
        }
        reader.readAsDataURL(file) // Read the file as a data URL
    })
}

export default UniFileUploader
