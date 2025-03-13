import React from "react";

import { IUniWithChildrenProps, } from "../common";
import useUniUser from "../api/hooks/user";


export interface IUniUserPermissionProps extends IUniWithChildrenProps {
    permission: string
    write?: boolean
}

export default function UniUserPermission(props: IUniUserPermissionProps): JSX.Element {
    const [user, , getPermission] = useUniUser()
    const [hasPerm, setHasPerm] = React.useState(false)

    React.useEffect(() => {
        setHasPerm(getPermission(props.permission, props.write))

        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [user, props.permission, props.write])

    if (hasPerm) return <>{props.children}</>

    return <></>

}
