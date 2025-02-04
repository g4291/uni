import React from "react";

import UniFade from "../uni/components/animations/fade";
import UniBox from "../uni/components/primitives/box";
import { useUniLang } from "../uni/translator";
import MarkdownDisplay from "./markdown/markdown";
import UniStack from "../uni/components/primitives/stack";
import ListPageHeader from "./list-header";
import { manual } from "../data/doc/manual";


/**
 * The `Help` component renders a help page with a header and markdown content.
 * It uses the `useUniLang` hook to determine the current language and displays
 * the corresponding manual content.
 *
 * @returns {JSX.Element} The rendered help page component.
 */
export default function Help(): JSX.Element {
    const [lang] = useUniLang()

    return <UniFade show>
        <UniBox.Box fullWidth fullHeight>
            <UniStack.Column spacing={1}>
                <ListPageHeader title="Help" />

            </UniStack.Column>
            <UniBox.Box fullWidth sx={{ p: 2 }}>
                <MarkdownDisplay markdownText={manual[lang as keyof typeof manual]} />
            </UniBox.Box>
        </UniBox.Box>
    </UniFade>


}
