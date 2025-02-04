import React from "react";

import UniFade from "./animations/fade";
import { Avatar } from "@mui/joy";
import UniTooltip from "./primitives/tooltip";
import { IUniUser } from "../api/common";
import { getUniColor, getUniVariant, IUniWithColorProps, IUniWithSizeProps, IUniWithSXProps, IUniWithVariantProps, UniColorProp, UniVariantProp } from "../common";
import { SxProps } from "@mui/joy/styles/types";


export const UNI_USER_AVATAR_CONFIG = {
    defaultSx: {
    },
    defaultVariant: "soft",
    defaultColor: "neutral",
} as {
    defaultMargin: string | number,
    defaultSx: SxProps,
    defaultVariant: UniVariantProp,
    defaultColor: UniColorProp,
}

export interface IUniUserAvatarProps extends IUniWithVariantProps, IUniWithSizeProps, IUniWithColorProps, IUniWithSXProps {
    user: IUniUser
}

/**
 * UniUserAvatar component renders a user's avatar with optional tooltip and fade effects.
 * It displays the user's avatar image if available, otherwise it shows the user's initials.
 *
 * @template T - The type of the props.
 * @param {IUniUserAvatarProps} props - The properties for the UniUserAvatar component.
 * @param {object} props.user - The user object containing user details.
 * @param {string} props.user.email - The email of the user.
 * @param {string} [props.user.first_name] - The first name of the user.
 * @param {string} [props.user.last_name] - The last name of the user.
 * @param {string} [props.user.avatar] - The URL of the user's avatar image.
 * @param {object} [props.sx] - The style object to customize the avatar.
 * @param {boolean} [props.small] - If true, the avatar will be small.
 * @param {boolean} [props.large] - If true, the avatar will be large.
 * @returns {JSX.Element} The rendered UniUserAvatar component.
 */
export default function UniUserAvatar(props: IUniUserAvatarProps): JSX.Element {
    const { sx, small, large } = props;

    const size = small ? "sm" : large ? "lg" : undefined;
    const variant = React.useMemo(() => getUniVariant(props, UNI_USER_AVATAR_CONFIG.defaultVariant), [props])
    const color = React.useMemo(() => getUniColor(props, UNI_USER_AVATAR_CONFIG.defaultColor), [props])
    const _sx: any = { ...UNI_USER_AVATAR_CONFIG.defaultSx, ...sx }

    var name = props.user.email
    if (props.user.first_name) {
        name = props.user.first_name
        if (props.user.last_name) {
            name += " " + props.user.last_name
        }
    }

    const initials = name.split(" ").map((n) => n[0]).join("")
    return <UniFade show>
        <UniTooltip title={name}>
            <Avatar variant={variant} size={size} sx={_sx as SxProps} color={color} alt={name} src={props.user.avatar}>{initials.toUpperCase()}</Avatar>
        </UniTooltip>
    </UniFade>

}
