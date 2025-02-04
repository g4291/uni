import React from "react";

import UniFade from "../../uni/components/animations/fade";
import UniBox from "../../uni/components/primitives/box";
import { UniTypography as UT } from "../../uni/components/primitives/typography";
import { useUniTranslator } from "../../uni/translator";
import useUniEntityList, { UniFindQuery, UniSort } from "../../uni/api/hooks/entity-list";
import UniSearchBox from "../../uni/components/search-box";
import UniStack from "../../uni/components/primitives/stack";
import useUniLocalStorage from "../../uni/hooks/local-storage";
import { DEFAULT_PAGE_SIZE, LIST_PAGE_SIZE_STORAGE_KEY, LIST_SPACING, LIST_UPDATE_INTERVAL } from "../../data/config";
import useUniScheduler from "../../uni/hooks/scheduler";
import UniDataGrid, { UniDataGridColDef } from "../../uni/components/data-grid";
import UserDetail from "./user-detail";
import UniButton from "../../uni/components/primitives/button";
import ListPageHeader from "../list-header";
import UniIcons from "../../uni/icons";
import UserNew from "./user-new";
import UniUserAvatar from "../../uni/components/user-avatar";
import { IUniUser } from "../../uni/api/common";

const ROW_HEIGHT = 100

const SEARCH_FIELDS: string[] = [
    "first_name",
    "last_name",
    "email",
]

export default function Users() {
    const t = useUniTranslator()
    const [openUserId, setOpenUserId] = React.useState<string>("")
    const [openNew, setOpenNew] = React.useState<boolean>(false)


    const [listPage, setListPage] = React.useState(1)
    const [pageSize, setPageSize] = useUniLocalStorage(LIST_PAGE_SIZE_STORAGE_KEY, DEFAULT_PAGE_SIZE)
    const [filter, setFilter] = React.useState<any>([])
    const [sort, setSort] = React.useState<UniSort | null>(null)
    const [query, setQuery] = React.useState<UniFindQuery>({
        filters: [],
        limit_from: (listPage - 1) * pageSize,
        limit_to: listPage * pageSize,
        sort_key: sort?.key,
        sort_order: sort?.order
    })
    const users = useUniEntityList<any>("/user", query)

    useUniScheduler(users.reload, LIST_UPDATE_INTERVAL, openUserId !== "" || openNew)

    const cols: UniDataGridColDef<IUniUser>[] = React.useMemo(() => [
        {
            name: "no.",
            width: 80,
            renderCell: (e) => {
                return <UT.Text xs>{e.seq}</UT.Text>
            },
            sortKey: "seq"
        },
        {
            name: "avatar",
            width: 100,
            renderCell: (e) => (
                <UniUserAvatar user={e} />
            )
        },
        {
            name: "email",
            width: 150,
            renderCell: (e) => <UT.Text small >{e.email}</UT.Text>,
            sortKey: "email"
        },
        {
            name: "first name",
            width: 100,
            renderCell: (e) => <UT.Title small color="warning">{e.first_name}</UT.Title>,
            sortKey: "first_name"
        },
        {
            name: "last name",
            width: 100,
            renderCell: (e) => <UT.Title small color="warning">{e.last_name}</UT.Title>,
            sortKey: "first_name"
        },
        {
            name: "note",
            renderCell: (e) => <UT.Text xs>{e.note}</UT.Text>,
            width: 200,
        }
    ], [])

    // effect for query reload
    // delayed 50ms to prevent multiple reloads when any query parameter changes
    // not sure if this is necessary
    React.useEffect(() => {
        const to = setTimeout(() => {
            setQuery(
                {
                    filters: filter,
                    limit_from: (listPage - 1) * pageSize,
                    limit_to: listPage * pageSize,
                    sort_key: sort?.key,
                    sort_order: sort?.order
                }
            )
        }, 50)

        return () => {
            clearTimeout(to)
        }

    }, [filter, listPage, pageSize, sort])


    return <>
        <UniFade show>
            <UniBox.Box fullWidth fullHeight>
                <UniStack.Column spacing={1}>
                    <ListPageHeader title="users" actions={
                        <>
                            <UniButton
                                small
                                outlined
                                onClick={() => {
                                    setOpenNew(true)
                                }}
                                startDecorator={<UniIcons.Create />}
                            >
                                {t("new user")}
                            </UniButton>
                            <UniButton
                                small
                                outlined
                                onClick={() => {
                                    users.reload()
                                }}
                                startDecorator={<UniIcons.Refresh />}
                            >
                                {t("refresh")}
                            </UniButton>
                        </>

                    } />

                    <UniBox.Box fullWidth>
                        <UniDataGrid
                            header={
                                <>
                                    <UniSearchBox fields={SEARCH_FIELDS} onChange={
                                        (filters) => {
                                            setFilter(filters)
                                            setListPage(1)
                                        }
                                    } />
                                </>
                            }
                            rowHeight={ROW_HEIGHT}
                            loading={users.loading}
                            cols={cols}
                            data={users.data}
                            height={`calc(100dvh - ${LIST_SPACING})`}
                            page={listPage}
                            pageSize={pageSize}
                            size={users.count}
                            onPageChange={setListPage}
                            onRowClick={(row) => {
                                setOpenUserId(row.id)
                            }}
                            onPageSizeChange={(size) => {
                                setPageSize(size)
                                setListPage(1)
                            }}
                            onSortChange={(sortKey, dir) => {
                                const order = dir === "asc" ? 0 : 1
                                setSort({ key: sortKey, order: order })
                                setListPage(1)
                            }}
                        />
                    </UniBox.Box>

                </UniStack.Column>
            </UniBox.Box>
            {
                openUserId !== "" && <UserDetail productId={openUserId} onClose={
                    () => {
                        setOpenUserId("")
                        users.reload()
                    }
                } />
            }
            {
                openNew && <UserNew onClose={
                    () => {
                        setOpenNew(false)
                        users.reload()
                    }
                } onCreated={(id: string) => { setOpenUserId(id) }} />
            }
        </UniFade>
    </>
}
