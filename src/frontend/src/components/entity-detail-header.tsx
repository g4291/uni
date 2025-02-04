import React from "react";

import { IUniEntity } from "../uni/api/hooks/entity";
import { useUniTranslator } from "../uni/translator";
import UniBox from "../uni/components/primitives/box";
import UniGrid from "../uni/components/primitives/grid";
import UniStack from "../uni/components/primitives/stack";
import UniButton from "../uni/components/primitives/button";
import UniIcons from "../uni/icons";


interface IWithEntityProps {
    entity: IUniEntity<any>
    title: string
}

export default function EntityDetailHeader(props: IWithEntityProps): JSX.Element {
    const t = useUniTranslator()

    return <>
        <UniBox.Box fullWidth>
            <UniGrid.Container spacing={1}>
                <UniGrid.Item xs={12} md={6}>
                    {props.title}
                </UniGrid.Item>
                <UniGrid.Item xs={12} md={6} sx={{ minHeight: "60px" }}>
                    <UniBox.HR fullWidth>
                        <UniStack.Row spacing={1}>
                            {props.entity.info}
                            <UniButton small plain onClick={() => { props.entity.reload(true) }} startDecorator={<UniIcons.Refresh />}>{t("refresh")}</UniButton>
                        </UniStack.Row>
                    </UniBox.HR>
                </UniGrid.Item>
            </UniGrid.Container>
        </UniBox.Box>
    </>

}