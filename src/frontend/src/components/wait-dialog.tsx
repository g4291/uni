import React from "react";

import UniFade from "../uni/components/animations/fade";
import UniBox from "../uni/components/primitives/box";
import { useUniTranslator } from "../uni/translator";
import UniModalDialog from "../uni/components/primitives/modal-dialog";
import UniProgress from "../uni/components/primitives/progress";

/**
 * A functional component that renders a modal dialog with a loading spinner.
 * This component is used to indicate that the user should wait for a process to complete.
 *
 * @returns {JSX.Element} The rendered WaitDialog component.
 */
export default function WaitDialog(): JSX.Element {
    const t = useUniTranslator()
    
    return <>
        <UniModalDialog
            outlined
            primary
            open
            title={t("Please wait")}
            sx={{ p: 0 }}
        >
            <UniFade show>
                <UniBox.VHC fullWidth fullHeight sx={{p:5}}>
                    <UniProgress.Circular color="warning" size="lg" />
                </UniBox.VHC>
            </UniFade>
        </UniModalDialog>
    </>
}