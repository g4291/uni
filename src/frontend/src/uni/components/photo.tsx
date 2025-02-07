import React from "react";

import UniFade from "./animations/fade";
import UniBox from "./primitives/box";
import { UniTypography as UT } from "./primitives/typography";
import { useUniTranslator } from "../translator";
import useUniTouaster from "../hooks/toaster";
import { SERVER_URL } from "../../data/config";
import { UniFile } from "../datamodel";
import UniCard from "./primitives/card";
import UniGrid from "./primitives/grid";
import { fileSize } from "../utils";
import { cropString } from "../../utils";
import UniCopyContentButton from "./copy-content";
import UniStack from "./primitives/stack";
import UniDeleteEntityWithConfirmButton from "./entity/delete-entity-button";
import UniDivider from "./primitives/divider";
import UniModalDialog from "./primitives/modal-dialog";
import UniProgress from "./primitives/progress";

export const UNI_PHOTO_CONFIG = {

}

export interface IUniSimplePhotoProps {
    photoFile: UniFile
    enableOpen?: boolean
    width?: number
    height?: number
    maxWidth?: number
    maxHeight?: number
}
/**
 * UniSimplePhoto component renders an image with optional width and height parameters.
 * It constructs the image URL using the provided photo file's public link and optional dimensions.
 * 
 * @param {IUniSimplePhotoProps} props - The properties for the UniSimplePhoto component.
 * @param {number} [props.width] - Optional width for the image.
 * @param {number} [props.height] - Optional height for the image.
 * @param {number} [props.maxWidth] - Optional maximum width for the image.
 * @param {number} [props.maxHeight] - Optional maximum height for the image.
 * @param {Object} props.photoFile - The photo file object containing the public link.
 * @param {string} props.photoFile.public_link - The public link to the photo file.
 * 
 * @returns {JSX.Element} The rendered image component.
 */
export function UniSimplePhoto(props: IUniSimplePhotoProps): JSX.Element {
    const t = useUniTranslator()
    const toast = useUniTouaster()
    const [open, setOpen] = React.useState(false)
    const [loaded, setLoaded] = React.useState(false)

    var params = ""
    if (props.width) {
        params += `&w=${props.width}`
    }
    if (props.height) {
        params += `&h=${props.height}`
    }


    const link = SERVER_URL + props.photoFile.public_link + params
    const fullLink = SERVER_URL + props.photoFile.public_link


    const imgElement = <>
        {
            !loaded && <UniBox.VHC fullWidth fullHeight>
                <UniStack.Column>
                    <UT.Text xs color="neutral">{t("loading ...")}</UT.Text>
                    <UniProgress.Circular />

                </UniStack.Column>
            </UniBox.VHC>
        }
        <img
            onLoad={() => { setLoaded(true) }}
            alt=""
            style={{
                borderRadius: "10px",
                maxWidth: props.maxWidth ? props.maxWidth : props.width,
                maxHeight: props.maxHeight ? props.maxHeight : props.height,
                display: loaded ? "block" : "none"
            }}
            src={link}
        />
    </>
    return <>
        <UniFade show>
            <UniBox.Box sx={{ p: 1 }}>
                {
                    props.enableOpen
                        ? <div style={{ cursor: "pointer" }} onClick={() => { setOpen(true) }}>
                            {imgElement}
                        </div>
                        : imgElement
                }
            </UniBox.Box>
            {open && <PhotoFullView filename={props.photoFile.original_name} onClose={() => setOpen(false)} link={fullLink} />}
        </UniFade>
    </>
}

interface IPhotoColumnProps {
    photo_id: string
    album: UniFile[]
    width?: number
    height?: number
    maxWidth?: number
    maxHeight?: number
    enableOpen?: boolean
}
/**
 * UniPhotoFromAlbum component renders a photo from an album based on the provided photo ID.
 * If the photo is not found, it displays a "no image" message.
 *
 * @param {IPhotoColumnProps} props - The properties for the component.
 * @param {Array} props.album - The album containing the photos.
 * @param {string} props.photo_id - The ID of the photo to be displayed.
 * @param {number} [props.width] - The width of the photo.
 * @param {number} [props.height] - The height of the photo.
 * @param {number} [props.maxWidth] - The maximum width of the photo.
 * @param {number} [props.maxHeight] - The maximum height of the photo.
 * @returns {JSX.Element} The rendered photo or a "no image" message.
 */
export function UniPhotoFromAlbum(props: IPhotoColumnProps): JSX.Element {
    const t = useUniTranslator()

    const photo = React.useMemo(() => props.album.find(p => p.id === props.photo_id), [props.album, props.photo_id])

    if (!photo) {
        return <UniFade show>
            <UniBox.VHC sx={{ p: 1 }}>
                <UT.Text xs color="neutral">{t("no image")}</UT.Text>
            </UniBox.VHC>
        </UniFade>
    }

    return <UniSimplePhoto
        photoFile={photo}
        width={props.width}
        height={props.height}
        maxWidth={props.maxWidth}
        maxHeight={props.maxHeight}
        enableOpen={props.enableOpen}
    />
}

export interface IUniPhotoCardProps {
    photo_id: string
    album: UniFile[]

    onDelete?: (id: string) => void
    actions?: React.ReactNode[]
}
const MAX_WIDTH = 150
const MAX_HEIGHT = 150

/**
 * UniPhotoCard component displays a photo card with various details and actions.
 *
 * @param {IUniPhotoCardProps} props - The properties for the UniPhotoCard component.
 * @returns {JSX.Element} The rendered UniPhotoCard component.
 *
 * @remarks
 * This component uses the `useUniTranslator` hook for translations and `React.useMemo` to memoize the photo object.
 * It also uses `React.useState` to manage the resolution state of the photo and `React.useEffect` to load the image and set its resolution.
 *
 * @example
 * ```tsx
 * <UniPhotoCard
 *   album={album}
 *   photo_id={photoId}
 *   actions={actions}
 *   onDelete={handleDelete}
 * />
 * ```
 *
 * @component
 * @name UniPhotoCard
 *
 * @property {IUniPhotoCardProps} props - The properties for the UniPhotoCard component.
 * @property {Array} props.album - The album containing photo objects.
 * @property {string} props.photo_id - The ID of the photo to be displayed.
 * @property {Array} [props.actions] - Optional actions to be displayed on the photo card.
 * @property {Function} [props.onDelete] - Optional callback function to be called when a photo is deleted.
 */
export function UniPhotoCard(props: IUniPhotoCardProps): JSX.Element {

    const t = useUniTranslator()
    const photo = React.useMemo(() => props.album.find(p => p.id === props.photo_id), [props.album, props.photo_id])
    const [resolution, setResolution] = React.useState<{ width: number, height: number } | null>(null);

    const link = SERVER_URL + photo?.public_link

    React.useEffect(() => {
        if (!photo) return
        const img = new Image();
        img.src = link;
        img.onload = () => {
            setResolution({ width: img.width, height: img.height });
        };
    }, []);

    if (!photo) {
        return <UniBox.VHC sx={{ p: 1 }}>
            <UT.Text xs color="neutral">{t("no image")}</UT.Text>
        </UniBox.VHC>
    }

    const _actions = props.actions ? [...props.actions] : []
    _actions.push(
        <UniDeleteEntityWithConfirmButton
            id={photo.id}
            endpoint="/file"
            name={t("photo") + ": " + photo.original_name}
            onSuccess={() => {
                props.onDelete && props.onDelete(photo.id)
            }}
            soft
            error
            small
        >
            {t("delete")}
        </UniDeleteEntityWithConfirmButton>
    )

    return <UniFade show>
        <UniCard
            fullWidth
            soft
            neutral
            header={
                <UniBox.VHC fullWidth>
                    <UniSimplePhoto
                        photoFile={photo}
                        width={MAX_WIDTH}
                        maxHeight={MAX_HEIGHT}
                        enableOpen
                    />
                </UniBox.VHC>
            }
            actions={
                <UniBox.HR fullWidth>
                    <UniStack.Row>
                        {
                            _actions.map((a, i) => <UniBox.Box key={i}>{a}</UniBox.Box>)
                        }
                    </UniStack.Row>
                </UniBox.HR>
            }
        >
            <UniGrid.Container spacing={1}>
                <UniGrid.Item xs={12}>
                    <UniDivider.H />
                </UniGrid.Item>
                <UniGrid.Item xs={12}>
                    <UT.Text xs>{t("name")}: {photo.original_name}</UT.Text>
                </UniGrid.Item>
                <UniGrid.Item xs={12}>
                    <UT.Text xs>{t("size")}: {fileSize(photo.size)}</UT.Text>
                </UniGrid.Item>
                {
                    resolution && <UniGrid.Item xs={12}>
                        <UT.Text xs>{t("resolution")}: {resolution.width}x{resolution.height}</UT.Text>
                    </UniGrid.Item>
                }
                <UniGrid.Item xs={12}>
                    <UniStack.Row fullHeight>
                        <UT.Text xs>{t("link")}: {cropString(link, 100)}</UT.Text>
                        <UniBox.VHC fullHeight>
                            <UT.Text xs><UniCopyContentButton content={link} /></UT.Text>
                        </UniBox.VHC>

                    </UniStack.Row>
                </UniGrid.Item>
            </UniGrid.Container>

        </UniCard>
    </UniFade>
}

export interface IPhotoFullView {
    onClose: () => any
    link: string
    filename?: string
}

/**
 * A component that displays a full view of a photo inside a modal dialog.
 *
 * @param {IPhotoFullView} props - The properties for the PhotoFullView component.
 * @param {string} props.link - The URL of the photo to display.
 * @param {string} [props.filename] - The filename of the photo.
 * @param {() => void} props.onClose - The function to call when the modal is closed.
 *
 * @returns {JSX.Element} The rendered PhotoFullView component.
 *
 * @component
 * @example
 * const photoProps = {
 *   link: 'https://example.com/photo.jpg',
 *   filename: 'photo.jpg',
 *   onClose: () => console.log('Modal closed')
 * };
 * 
 * <PhotoFullView {...photoProps} />
 */
export default function PhotoFullView(props: IPhotoFullView): JSX.Element {

    const t = useUniTranslator()
    const [resolution, setResolution] = React.useState<{ width: number, height: number } | null>(null);
    const [loaded, setLoaded] = React.useState(false)

    const handleClose = () => {
        props.onClose()
    }

    // get resolution of the image
    React.useEffect(() => {
        const img = new Image();
        img.src = props.link;
        img.onload = () => {
            setResolution({ width: img.width, height: img.height });
        };
    }, [props.link]);
    const resolutionString = resolution ? `${resolution.width}x${resolution.height}` : ""

    return <>
        <UniModalDialog
            outlined
            primary
            open
            title={t((props.filename || "") + " " + resolutionString)}
            bodySx={{ width: "95%", height: "95dvh" }}
            onClose={handleClose}
        >
            <UniFade show>
                <UniBox.VHC fullWidth fullHeight>
                    <div onClick={props.onClose} style={{ cursor: "pointer", width: "100%", height: "100%" }}>
                        <img onLoad={() => { setLoaded(true) }} src={props.link} alt="" style={{ width: "100%", maxHeight: "100%", display: loaded ? "block" : "none" }} />
                    </div>
                </UniBox.VHC>
            </UniFade>
        </UniModalDialog>
    </>
}
