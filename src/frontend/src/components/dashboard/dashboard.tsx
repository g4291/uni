import React from "react";

import UniFade from "../../uni/components/animations/fade";
import UniBox from "../../uni/components/primitives/box";
import UniStack from "../../uni/components/primitives/stack";
import ListPageHeader from "../list-header";

/**
 * The `Dashboard` component renders the main dashboard view.
 *
 * @returns {JSX.Element} The rendered dashboard component.
 */
export default function Dashboard() {

    return <UniFade show>
        <UniBox.Box fullWidth fullHeight>
            <UniStack.Column spacing={1}>
                <ListPageHeader title="dashboard" />
            </UniStack.Column>
        </UniBox.Box>
    </UniFade>
}