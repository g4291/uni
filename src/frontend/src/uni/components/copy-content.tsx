import React from 'react';

import UniButton from './primitives/button';
import { useUniTranslator } from '../translator';
import UniIcons from '../icons';
import { copyToClipboard } from '../../utils';
import UniTooltip from './primitives/tooltip';
import UniStack from './primitives/stack';


interface IUniCopyContentButtonProps {
    content: string
    title?: React.ReactNode
}


/**
 * UniCopyContentButton is a React functional component that renders a button
 * which copies provided content to the clipboard when clicked. The button is 
 * wrapped in a tooltip displaying a translation for "copy".
 *
 * @param {IUniCopyContentButtonProps} props - The properties for the component.
 * @param {string} props.title - The title to be displayed next to the copy button.
 * @param {string} props.content - The content to be copied to the clipboard.
 * 
 * @returns {JSX.Element} The rendered component.
 */
export default function UniCopyContentButton(props: IUniCopyContentButtonProps): JSX.Element {

    const t = useUniTranslator()
    return <UniTooltip title={t("copy")} arrow>
        <div>
            <UniStack.Row spacing={1} sx={{alignItems: "center"}}>
                {props.title}
                <UniButton small plain onClick={(e) => {
                    copyToClipboard(props.content)
                }}><UniIcons.Copy /></UniButton>

            </UniStack.Row>
        </div>
    </UniTooltip>
}