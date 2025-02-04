import React from 'react';
import UniBox from './uni/components/primitives/box';
import UniStack from './uni/components/primitives/stack';
import UniFade from './uni/components/animations/fade';
import { useUniTranslator } from './uni/translator';
import UniPrivateAppBar from './uni/components/private-app-bar';
import { Menu, MenuWrapper } from './components/menu';
import { usePage } from './hooks/page';
import { UniTypography as UT } from './uni/components/primitives/typography';
import { useUniThemeMode } from './uni/theme';
import UniDivider from './uni/components/primitives/divider';
import Dashboard from './components/dashboard/dashboard';
import Help from './components/help';
import Users from './components/users/users';


export default function AppPrivate() {
    const t = useUniTranslator()
    const [showMenu, setShowMenu] = React.useState(true)
    const [page] = usePage()
    const [, setThemeMode] = useUniThemeMode()


    const getPageComponent = (pageId: string) => {
        const component = getComponent(pages, pageId)
        if (component) {
            return component
        }

        return () => <UniBox.VHC fullWidth sx={{ p: 3 }}><UniFade show><UT.H4 color="warning">{t("Page not found")}</UT.H4></UniFade></UniBox.VHC>
    }

    // eslint-disable-next-line
    const PageComponent = React.useMemo(() => getPageComponent(page), [page])

    React.useEffect(() => {
        setThemeMode("dark")

        // eslint-disable-next-line
    }, [])

    return (
        <>
            <UniFade show>
                <UniBox.Box fullWidth sx={{ height: "100dvh" }}>
                    <UniStack.Column
                        fullHeight
                        fullWidth
                        spacing={0}
                    >
                        <UniPrivateAppBar
                        langSelector
                            logo={
                                <UniStack.Row spacing={2} sx={{ alignContent: "center", alignItems: "center" }}>
                                    <UniDivider.V />
                                    <UniBox.VHC fullWidth fullHeight>
                                        <UT.Title large>UNI</UT.Title>
                                    </UniBox.VHC>
                                </UniStack.Row>
                            }
                            menu={
                                <Menu />
                            }
                            onToggleLeft={
                                () => setShowMenu(!showMenu)
                            }
                        />
                        <UniStack.Row
                            fullHeight
                            fullWidth
                            spacing={0}
                        >
                            {
                                showMenu && <MenuWrapper />
                            }
                            <UniBox.Box
                                fullWidth
                                fullHeight
                                sx={{ bgcolor: "background", p: 0, position: "relative", overflow: "none" }}
                            >
                                <UniBox.Box
                                    fullWidth
                                    sx={{
                                        position: "absolute",
                                        top: 0,
                                        bottom: 0,
                                        overflowY: "auto",
                                        overflowX: "auto",
                                        p: 1
                                    }}
                                >
                                    <PageComponent />
                                </UniBox.Box>
                            </UniBox.Box>
                        </UniStack.Row>
                    </UniStack.Column>
                </UniBox.Box>
            </UniFade>
        </>
    )
}


const pages = [
    {
        id: "dashboard",
        component: Dashboard
    },
    {
        id: "users",
        component: Users
    },
    {
        id: "help",
        component: Help
    }
]

function getComponent(pages: { id: string, component: () => JSX.Element }[], pageId: string) {
    return pages.find(p => p.id === pageId)?.component
}

