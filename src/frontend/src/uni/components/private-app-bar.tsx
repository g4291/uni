import React from 'react';

import UniDivider from './primitives/divider';
import UniBox from './primitives/box';
import { UniTypography as UT } from './primitives/typography';
import UniLogoutButton from './logout-button';
import UniStack from './primitives/stack';
import useUniUser from '../api/hooks/user';
import UniToggleThemeMode from './toggle-theme-mode';
import UniToggleLang from './toggle-language';
import { useUniTranslator } from '../translator';
import useUniBreakPoint from '../hooks/breakpoint';
import UniIcons from '../icons';
import UniButton from './primitives/button';
import { Drawer } from '@mui/joy';
import useEventListener from '../hooks/event-listener';
import { SxProps } from '@mui/joy/styles/types';
import UniUserAvatar from './user-avatar';


export const UNI_EVENT_MENU_CLOSE_LEFT = "uni.event.menu.close.left"
export const UNI_EVENT_MENU_CLOSE_RIGHT = "uni.event.menu.close.right"

export const UNI_PRIVATE_APP_BAR_CONFIG = {
    defaultSx: {

    }
} as {
    defaultSx: SxProps
}

export interface IPrivateAppBarProps {
    menu?: React.ReactNode
    title?: string
    logo?: React.ReactNode
    onToggleLeft?: () => void
    onToggleRight?: () => void
    themeSelector?: boolean
    langSelector?: boolean
}

export default function UniPrivateAppBar(props: IPrivateAppBarProps): JSX.Element {
    const [user] = useUniUser()
    const t = useUniTranslator()
    const bp = useUniBreakPoint()
    const [openRight, setOpenRight] = React.useState(false)
    const [openLeft, setOpenLeft] = React.useState(false)

    const toggleRightDrawer = React.useCallback((inOpen: boolean) => (event: React.KeyboardEvent | React.MouseEvent) => {
        if (_toggleCheck(event)) return;
        setOpenRight(inOpen);
    }, []);

    const toggleLeftDrawer = React.useCallback((inOpen: boolean) => (event: React.KeyboardEvent | React.MouseEvent) => {
        if (_toggleCheck(event)) return;
        setOpenLeft(inOpen);
    }, []);

    useEventListener(UNI_EVENT_MENU_CLOSE_LEFT, () => {
        setOpenLeft(false)
    })

    useEventListener(UNI_EVENT_MENU_CLOSE_LEFT, () => {
        setOpenRight(false)
    })

    const rightElement = React.useMemo(() => {
        if (bp === "xs") {
            return (<>
                <UniBox.HR fullWidth>
                    <UniStack.Row fullHeight sx={{ alignItems: "center" }}>
                        <UniUserAvatar small user={user} />
                        <UniDivider.V />
                        <UniButton small plain onClick={() => {
                            setOpenRight(!openRight)
                            if (props.onToggleRight) props.onToggleRight()
                        }}><UniIcons.HorizontalMenu /></UniButton>

                    </UniStack.Row>
                </UniBox.HR >
                <Drawer open={openRight} onClose={toggleRightDrawer(false)} anchor='right' size="sm">
                    <UniStack.Column fullWidth sx={{ p: 1 }}>
                        {
                            props.langSelector && <>
                                <UniToggleLang small fullWidth label={t("change language")} />
                                <UniDivider.H />

                            </>
                        }
                        {
                            props.themeSelector && <>
                                <UniToggleThemeMode plain small text="toggle theme" fullWidth noTooltip />
                                <UniDivider.H />
                            </>
                        }
                        <UniLogoutButton plain small text="logout" fullWidth noTooltip />
                    </UniStack.Column>
                </Drawer>
            </>)
        }

        return (
            <UniBox.Box fullHeight fullWidth>
                <UniBox.HR fullWidth fullHeight>
                    <UniStack.Row fullHeight sx={{ alignItems: "center" }}>
                        <UniUserAvatar small user={user} />
                        <UniDivider.V />
                        {
                            props.langSelector && <>
                            <UniToggleLang small />
                            <UniDivider.V />
                            </>
                        }
                        {
                            props.themeSelector && <>
                            <UniToggleThemeMode small />
                            <UniDivider.V />
                            </>

                        }
                        {
                            props.langSelector && props.themeSelector && <UniDivider.V />
                        }
                        <UniLogoutButton small />
                    </UniStack.Row>
                </UniBox.HR>
            </UniBox.Box>
        )

        // eslint-disable-next-line
    }, [bp, user, openRight])

    const leftLement = React.useMemo(() => {
        const BtnElement = ({ small }: { small: boolean }) => (
            <>
                <UniButton sx={{ p: 0 }} small plain onClick={() => {
                    if (small) setOpenLeft(!openLeft)
                    if (props.onToggleLeft) props.onToggleLeft()
                }}>
                    <UniIcons.VerticalMenu />
                </UniButton>
            </>
        )
        if (bp === "xs" || bp === "sm") {
            return (
                <>
                    <BtnElement small />
                    <Drawer open={openLeft} onClose={toggleLeftDrawer(false)} anchor='left' size="md">
                        <UniBox.Box fullWidth fullHeight sx={{ p: 1 }}>
                            {props.menu}
                        </UniBox.Box>
                    </Drawer>
                </>
            )
        }
        return <BtnElement small={false} />

        // eslint-disable-next-line
    }, [bp, user, openLeft, props.menu])

    return (
        <>
            <UniBox.Box fullWidth sx={{ borderBottom: "1px solid", borderColor: "divider", pb: 1 }}>
                <UniStack.Row fullWidth fullHeight spacing={0} sx={{ p: 1, pb: 0 }}>
                    <UniBox.VC fullWidth>
                        <UniStack.Row>
                            {leftLement}
                            <UniBox.VC>
                                {
                                    props.logo ? props.logo : <UT.Title large>{props.title}</UT.Title>
                                }
                            </UniBox.VC>
                        </UniStack.Row>
                    </UniBox.VC>
                    {rightElement}

                </UniStack.Row>
            </UniBox.Box>
        </>
    )
}


function _toggleCheck(event: React.KeyboardEvent | React.MouseEvent): boolean {
    if (event.type === 'keydown' && ((event as React.KeyboardEvent).key === 'Tab' || (event as React.KeyboardEvent).key === 'Shift')) return true
    return false
}