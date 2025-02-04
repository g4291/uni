import React from "react";

import UniBox from "../uni/components/primitives/box";
import { UniTypography as UT } from "../uni/components/primitives/typography";
import { useUniTranslator } from "../uni/translator";
import UniStack from "../uni/components/primitives/stack";
import UniGrid from "../uni/components/primitives/grid";
import UniFade from "../uni/components/animations/fade";

export interface IListHeaderProps {
    title: string
    actions?: React.ReactNode
}

/**
 * ListPageHeader component renders a header section for a list page.
 * It includes a title and a set of actions.
 *
 * @param {IListHeaderProps} props - The properties for the ListPageHeader component.
 * @param {string} props.title - The title to be displayed in the header.
 * @param {React.ReactNode} props.actions - The actions to be displayed in the header.
 *
 * @returns {JSX.Element} The rendered ListPageHeader component.
 */
export default function ListPageHeader(props: IListHeaderProps): JSX.Element {

    const t = useUniTranslator()

    return <UniFade show>
        <UniGrid.Container spacing={1}>
            <UniGrid.Item xs={12} md={4}>
                <UniBox.Box sx={{ p: 2 }}>
                    <UT.H3 color="neutral">
                        {t(t(props.title))}
                    </UT.H3>
                </UniBox.Box>
            </UniGrid.Item>
            
            <UniGrid.Item xs={12} md={8}>
                <UniBox.HR fullWidth fullHeight>
                    <UniBox.VC fullHeight sx={{ overflowY: "auto", scrollbarWidth: "thin" }}>
                        <UniStack.Row  >
                            {props.actions}
                        </UniStack.Row>
                    </UniBox.VC>
                </UniBox.HR>
            </UniGrid.Item>
        </UniGrid.Container>
    </UniFade>
}
