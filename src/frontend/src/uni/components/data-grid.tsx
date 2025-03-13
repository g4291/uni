import React from "react";

import UniFade from "./animations/fade";
import UniBox from "./primitives/box";
import { UniTypography as UT } from "./primitives/typography";
import { useUniTranslator } from "../translator";
import UniButton from "./primitives/button";
import UniStack from "./primitives/stack";
import { Table } from "@mui/joy";
import UniCard from "./primitives/card";
import UniProgress from "./primitives/progress";
import UniIcons from "../icons";
import UniSelect, { UniSelectOption } from "./primitives/select";
import useUniBreakPoint from "../hooks/breakpoint";
import UniTooltip from "./primitives/tooltip";
import UniDivider from "./primitives/divider";
import { UniDatabaseModel } from "../datamodel";
import { datetimeStrFromTimestamp } from "../../utils";
import UniCopyContentButton from "./copy-content";


export const UNI_DATA_GRID_CONFIG = {
    defaultPageSize: 10,
    pageSizes: [10, 20, 50, 100]
} as {
    defaultPageSize: number,
    pageSizes: number[]
}

export type UniDataGridSortDir = "asc" | "desc"

export interface UniDataGridColDef<T> {
    name: string
    renderCell: (e: T) => any
    width: number
    sortKey?: string
    preventClickEvent?: boolean
}

export interface IUniDataGridProps<T> {
    cols: UniDataGridColDef<T>[]
    data: T[]
    height: string
    rowHeight?: number
    loading: boolean
    page?: number
    pageSize?: number
    size: number
    onPageChange?: (page: number) => any
    onRowClick?: (row: T, ctrl: boolean, shift: boolean) => any
    header?: React.ReactNode
    onPageSizeChange?: (pageSize: number) => any
    onSortChange?: (sortKey: string, dir: UniDataGridSortDir) => any
    disablePagination?: boolean
}
/**
 * UniDataGrid is a generic data grid component that displays tabular data with pagination, sorting, and customizable columns.
 * 
 * @template T - The type of data being displayed in the grid.
 * 
 * @param {IUniDataGridProps<T>} props - The properties for the UniDataGrid component.
 * @param {number} props.size - The total number of data items.
 * @param {number} props.page - The current page number.
 * @param {number} props.pageSize - The number of items per page.
 * @param {T[]} props.data - The data to be displayed in the grid.
 * @param {IUniDataGridColumn<T>[]} props.cols - The columns configuration for the grid.
 * @param {number} props.rowHeight - The height of each row in the grid.
 * @param {React.ReactNode} props.header - The header content for the grid.
 * @param {boolean} props.loading - Indicates if the data is currently loading.
 * @param {number} props.height - The height of the grid.
 * @param {(row: T) => void} [props.onRowClick] - Callback function when a row is clicked.
 * @param {(pageSize: number) => void} props.onPageSizeChange - Callback function when the page size changes.
 * @param {(page: number) => void} props.onPageChange - Callback function when the page changes.
 * @param {(sortKey: string, direction: "asc" | "desc") => void} [props.onSortChange] - Callback function when the sort order changes.
 * 
 * @returns {JSX.Element} The rendered UniDataGrid component.
 */
export default function UniDataGrid<T>(props: IUniDataGridProps<T>): JSX.Element {

    const t = useUniTranslator()
    const bp = useUniBreakPoint()
    const boxRef = React.useRef<HTMLDivElement>(null)

    const page = props.page || 1
    const pageSize = props.pageSize || UNI_DATA_GRID_CONFIG.defaultPageSize

    const hasMore = React.useMemo(() => {
        return props.size > page * pageSize
    }, [props.size, page, pageSize])

    const pages = React.useMemo(() => Math.ceil(props.size / pageSize),
        [props.size, pageSize])


    const tableBody = React.useMemo(() => {
        if (props.data.length === 0) {
            return <tbody>
                <tr>
                    <td colSpan={props.cols.length}>
                        <UniBox.VHC fullWidth sx={{ p: 2 }}>
                            <UT.Text xs color="neutral"><UniFade show>{t("no data")}</UniFade></UT.Text>
                        </UniBox.VHC>
                    </td>
                </tr>
            </tbody>
        } else {
            return <tbody>
                {
                    props.data.map((row, ridx) => {
                        return <tr key={ridx} style={{ height: props.rowHeight }} >
                            {
                                props.cols.map((col, cidx) => {
                                    return <td key={ridx + "_" + cidx} style={{ cursor: (props.onRowClick && !col.preventClickEvent) ? "pointer" : "auto" }} onClick={(e) => {
                                        if (props.onRowClick && !col.preventClickEvent) {
                                            props.onRowClick(row, e.ctrlKey, e.shiftKey)
                                        }
                                    }}><UniFade show>{col.renderCell(row)}</UniFade></td>
                                })
                            }
                        </tr>
                    })
                }
            </tbody>
        }

        // eslint-disable-next-line
    }, [props.data, props.cols, props.rowHeight])


    const handleScroll = () => {
        // Scroll the container to a specific position
        if (boxRef.current) {
            boxRef.current.scroll({
                top: 0,
                behavior: 'smooth'
            })
        }
    }

    return <>
        <UniCard
            outlined
            header={

                props.header && <UniBox.Box fullWidth sx={{ p: 1 }}>
                    {props.header}
                </UniBox.Box>

            }
            fullWidth
            contentSx={{ p: 0, m: 0 }}
            sx={{ m: 0, p: 0 }}
            footer={
                <UniBox.HR fullWidth sx={{ p: 1, m: 0, borderTop: "1px solid", borderColor: "divider" }}>
                    <UniStack.Row spacing={0}>
                        <UniBox.VHC sx={{ width: "150px" }}>
                            <UniFade show={props.loading}>
                                <UniProgress.Circular
                                    size="sm"
                                    color="warning"
                                />
                            </UniFade>
                        </UniBox.VHC>
                        {
                            !props.disablePagination && bp !== "xs" && <UniBox.VHC sx={{ p: 1 }}>
                                <UT.Text xs>{t("page size")}</UT.Text>
                            </UniBox.VHC>
                        }
                        {
                            !props.disablePagination
                            && <UniSelect
                                small
                                sx={{ width: "60px" }}
                                value={pageSize}
                                onChange={(v: string) => {
                                    props.onPageSizeChange && props.onPageSizeChange(Number.parseInt(v))
                                }}
                            >
                                {
                                    UNI_DATA_GRID_CONFIG.pageSizes.map((size, idx) => <UniSelectOption key={idx} value={size}>{size}</UniSelectOption>)
                                }
                            </UniSelect>
                        }
                        <UniBox.VHC sx={{ p: 1 }}>
                            <UT.Text xs>{t("total")}: {props.size}</UT.Text>
                        </UniBox.VHC>
                        {
                            !props.disablePagination
                            && <>
                                <UniButton small plain onClick={() => {
                                    props.onPageChange && props.onPageChange(1)
                                    handleScroll()
                                }} disabled={page === 1}>
                                    <UniIcons.LeftDouble />
                                </UniButton>
                                <UniButton small plain onClick={() => {
                                    props.onPageChange && props.onPageChange(page - 1)
                                    handleScroll()
                                }} disabled={page === 1}>
                                    <UniIcons.Left />
                                </UniButton>
                                <UniBox.VHC sx={{ width: bp !== "xs" ? "100px" : "50px" }}>
                                    <UT.Text xs sx={{ textAlign: "center" }}>
                                        {bp !== "xs" && t("page")} {page} / {pages}
                                    </UT.Text>
                                </UniBox.VHC>
                                <UniButton small plain onClick={() => {
                                    props.onPageChange && props.onPageChange(page + 1)
                                    handleScroll()
                                }} disabled={!hasMore}>
                                    <UniIcons.Right />
                                </UniButton>
                                <UniButton small plain onClick={() => {
                                    props.onPageChange && props.onPageChange(pages)
                                    handleScroll()
                                }} disabled={!hasMore}>
                                    <UniIcons.RightDouble />
                                </UniButton>
                            </>
                        }
                    </UniStack.Row>
                </UniBox.HR>
            }
        >
            <UniBox.Box ref={boxRef} fullWidth sx={{ overflow: "auto", height: props.height, m: 0, p: 0, scrollbarWidth: "thin" }}>
                <Table sx={{ m: 0 }} stickyHeader hoverRow>
                    <thead>
                        <tr>
                            {
                                props.cols.map((col, idx) => {
                                    const sortKey = col.sortKey
                                    if (sortKey) {
                                        return <th key={idx} style={{ width: col.width }}>
                                            <UniStack.Row>
                                                <UniBox.VHC fullWidth>
                                                    <UT.Text xs color="neutral">{t(col.name)}</UT.Text>
                                                </UniBox.VHC>
                                                <UniBox.VHC fullWidth>
                                                    <UniStack.Row spacing={0}>
                                                        <UniButton sx={{ p: 0 }} warning plain small onClick={() => {
                                                            if (props.onSortChange) {
                                                                props.onSortChange(sortKey, "asc")
                                                            }
                                                        }}>
                                                            <UniTooltip title={t("sort ascending")}>
                                                                <UniIcons.Up />
                                                            </UniTooltip>
                                                        </UniButton>
                                                        <UniButton sx={{ p: 0 }} plain warning small onClick={() => {
                                                            if (props.onSortChange) {
                                                                props.onSortChange(sortKey, "desc")
                                                            }
                                                        }}>
                                                            <UniTooltip title={t("sort descending")}>
                                                                <UniIcons.Down />
                                                            </UniTooltip>
                                                        </UniButton>
                                                    </UniStack.Row>
                                                </UniBox.VHC>
                                                {
                                                    idx < props.cols.length - 1 && <UniDivider.V />
                                                }
                                            </UniStack.Row>
                                        </th>
                                    }
                                    return <th key={idx} style={{ width: col.width }}>
                                        <UniStack.Row fullWidth>
                                            <UniBox.VHC fullWidth fullHeight sx={{ p: 1 }}>
                                                <UT.Text xs color="neutral">{t(col.name)}</UT.Text>
                                            </UniBox.VHC>
                                            {
                                                idx < props.cols.length - 1 && <UniDivider.V />
                                            }
                                        </UniStack.Row>
                                    </th>
                                })
                            }
                        </tr>
                    </thead>
                    {tableBody}
                </Table>
            </UniBox.Box>
        </UniCard>
    </>
}

export function uniGridColumnId<T extends UniDatabaseModel>(xs?: boolean): UniDataGridColDef<T> {
    return {
        name: "ID",
        width: 400,
        renderCell: (e) => {
            return <UniCopyContentButton content={e.id} title={<UT.Text>{e.id}</UT.Text>} />
        },
        preventClickEvent: true
    }
}

export function uniGridColumnNo<T extends UniDatabaseModel>(xs?: boolean): UniDataGridColDef<T> {
    return {
        name: "no.",
        width: 150,
        renderCell: (e) => {
            return <UT.Text xs={xs}>{e.seq}</UT.Text>
        },
        sortKey: "seq"
    }
}

export function uniGridColumnName<T extends { name: string }>(xs?: boolean): UniDataGridColDef<T> {
    return {
        name: "name",
        width: 250,
        renderCell: (e) => {
            return <UT.Text xs={xs}>{e.name}</UT.Text>
        },
        sortKey: "name"
    }
}

export function uniGridColumnNote<T extends UniDatabaseModel>(xs?: boolean): UniDataGridColDef<T> {
    return {
        name: "note",
        width: 200,
        renderCell: (e) => {
            return <UT.Text xs={xs}>{e.note}</UT.Text>
        },
        sortKey: "note"
    }
}

export function uniGridColumnCreated<T extends UniDatabaseModel>(xs?: boolean): UniDataGridColDef<T> {
    return {
        name: "created",
        width: 200,
        renderCell: (e) => {
            if (!e.created.timestamp) return <></>
            return <UT.Text xs={xs}>{datetimeStrFromTimestamp(e.created.timestamp)}</UT.Text>
        },
        sortKey: "created.timestamp"
    }
}

export function uniGridColumnUpdated<T extends UniDatabaseModel>(xs?: boolean): UniDataGridColDef<T> {
    return {
        name: "updated",
        width: 200,
        renderCell: (e) => {
            if (!e.created.timestamp) return <></>
            return <UT.Text xs={xs}>{datetimeStrFromTimestamp(e.created.timestamp)}</UT.Text>
        },
        sortKey: "updated.timestamp"
    }
}
