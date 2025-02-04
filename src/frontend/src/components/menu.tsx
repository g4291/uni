import UniDivider from '../uni/components/primitives/divider';
import UniBox from '../uni/components/primitives/box';
import { UniTypography as UT } from '../uni/components/primitives/typography';
import UniStack from '../uni/components/primitives/stack';
import UniFade from '../uni/components/animations/fade';
import { useUniTranslator } from '../uni/translator';
import useUniBreakPoint from '../uni/hooks/breakpoint';
import { usePage } from '../hooks/page';
import UniButton from '../uni/components/primitives/button';
import UniIcons from '../uni/icons';
import { dispatchUniEvent } from '../uni/events';
import { UNI_EVENT_MENU_CLOSE_LEFT } from '../uni/components/private-app-bar';
import { APP_NAME } from '../data/config';


/**
 * A wrapper component for the Menu component that conditionally renders based on the current breakpoint.
 * 
 * This component uses the `useUniBreakPoint` hook to determine the current breakpoint.
 * If the breakpoint is "xs" (extra small) or "sm" (small), the component returns `null` and does not render anything.
 * For other breakpoints, it renders the `Menu` component inside a styled `UniBox.Box` component with a border.
 * 
 * @returns {JSX.Element | null} The rendered Menu component or null based on the breakpoint.
 */
export function MenuWrapper(): JSX.Element | null {

    const bp = useUniBreakPoint()

    if (bp === "xs" || bp === "sm") return null
    return (
        <>
            <UniFade show>
                <UniBox.Box fullHeight sx={{ borderRight: "1px solid", borderColor: "divider" }}>
                    <UniBox.Box fullHeight sx={{ width: "300px" }}>
                        <Menu />
                    </UniBox.Box>
                </UniBox.Box>
            </UniFade>
        </>
    )
}

interface IMenuProps {
}
export function Menu(props: IMenuProps): JSX.Element {
    const t = useUniTranslator()
    const [, setPage] = usePage()

    return (
        <>
            <UniStack.Column fullHeight fullWidth >
                <UniBox.Box fullWidth fullHeight sx={{ position: "relative" }}>
                    <UniBox.Box fullWidth sx={{ position: "absolute", top: 0, bottom: 0, overflowY: "auto", scrollbarWidth: "thin", p: 2, }}>
                        <UniStack.Column fullWidth spacing={1}>

                            <UniDivider.H>{t("main menu")}</UniDivider.H>
                            {
                                primaryMenuItems.map((item, index) => {
                                    return (
                                        <UniButton
                                            small
                                            left
                                            plain

                                            fullWidth
                                            key={index}
                                            onClick={() => {
                                                setPage(item.name.toLowerCase())
                                                dispatchUniEvent(UNI_EVENT_MENU_CLOSE_LEFT, {})
                                            }}
                                            startDecorator={<item.icon color="primary" sx={{ mr: 1 }} />}
                                        >
                                            {t(item.name)}

                                        </UniButton>
                                    )
                                })
                            }

                            <UniDivider.H >{t("system")}</UniDivider.H>
                            {
                                systemMenuItems.map((item, index) => {
                                    return (
                                        <UniButton
                                            small
                                            left
                                            plain
                                            primary
                                            fullWidth
                                            key={index}
                                            onClick={() => {
                                                setPage(item.name.toLowerCase())
                                                dispatchUniEvent(UNI_EVENT_MENU_CLOSE_LEFT, {})
                                            }}
                                            startDecorator={<item.icon />}
                                        >
                                            {t(item.name)}
                                        </UniButton>
                                    )
                                })
                            }
                            <UniDivider.H >{t("other")}</UniDivider.H>
                            {
                                otherMenuItems.map((item, index) => {
                                    return (
                                        <UniButton
                                            small
                                            left
                                            plain
                                            warning
                                            fullWidth
                                            key={index}
                                            onClick={() => {
                                                setPage(item.name.toLowerCase())
                                                dispatchUniEvent(UNI_EVENT_MENU_CLOSE_LEFT, {})
                                            }}
                                            startDecorator={<item.icon />}
                                        >
                                            {t(item.name)}
                                        </UniButton>
                                    )
                                })
                            }

                        </UniStack.Column>
                    </UniBox.Box>
                </UniBox.Box>
                <UniBox.Box>
                    <UniBox.Box sx={{ height: "120px", p: 2, borderTop: "1px solid", borderColor: "divider" }}>
                        <UniBox.VHC fullWidth>
                            <UT.Text xs>{APP_NAME} v{process.env.REACT_APP_VERSION}</UT.Text>
                        </UniBox.VHC>
                    </UniBox.Box>
                </UniBox.Box>
            </UniStack.Column>
        </>
    )
}

const primaryMenuItems = [
    {
        name: "Dashboard",
        icon: UniIcons.Dashboard
    },
]

const systemMenuItems = [
    {
        name: "Settings",
        icon: UniIcons.Settings
    },
    {
        name: "Users",
        icon: UniIcons.People
    }
]

const otherMenuItems = [
    {
        name: "Help",
        icon: UniIcons.Help
    }
]
