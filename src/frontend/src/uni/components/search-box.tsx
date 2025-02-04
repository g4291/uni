import React from 'react';
import { IUniLoading } from '../hooks/loading';
import { useUniTranslator } from '../translator';
import useDelay from '../api/hooks/delay';
import UniInput from './primitives/input';
import UniIcons from '../icons';
import { UniTypography as UT } from './primitives/typography';
import UniStack from './primitives/stack';
import useUniLocalStorage from '../hooks/local-storage';
import UniButton from './primitives/button';


export const UNI_SEARCH_BOX_CONFIG = {
    delay: 400,
    startDecorator: <UniIcons.Search />,
    fullWidth: true,
    small: true,
} as {
    delay: number,
    startDecorator: JSX.Element | undefined,
    fullWidth: boolean | undefined,
    small: boolean | undefined,
}

interface IUniSearchBoxProps {
    fields: any[];
    loading?: IUniLoading
    onChange: (filters: any) => any
    localStorageKey?: string
}

export function UniSearchBox({ fields, loading, onChange, localStorageKey = "uni.searchbox" }: IUniSearchBoxProps): JSX.Element {
    const t = useUniTranslator();
    const [search, setSearch] = useUniLocalStorage(localStorageKey, "")


    const handlesearch = () => {
        const filters = []
        if (search && fields.length) {
            for (let s of split(search)) {
                const _filter = { "OR": [] as any }
                for (let f of fields) {
                    const _int = parseInt(s)
                    const _float = parseFloat(s)
                    // int
                    if (!isNaN(_int)) {
                        _filter["OR"].push(
                            [f, "==", _int]
                        )
                    }
                    // float
                    if (!isNaN(_float)) {
                        _filter["OR"].push(
                            [f, "==", _float]
                        )
                    }
                    // string
                    _filter["OR"].push(
                        [f, "regex", s.toUpperCase()]
                    )
                }
                filters.push(_filter)
            }
        }
        onChange(filters);
        loading && loading.off();

    }

    // use delayed effect
    useDelay(handlesearch, [search], 400, false);

    React.useEffect(() => {
        if (search !== "") handlesearch()

        // eslint-disable-next-line
    }, [])

    return (
        <>
            <UniInput
                primary
                startDecorator={UNI_SEARCH_BOX_CONFIG.startDecorator}
                fullWidth={UNI_SEARCH_BOX_CONFIG.fullWidth}
                small={UNI_SEARCH_BOX_CONFIG.small}
                placeholder={t("search")}
                value={search}
                onChange={setSearch}
                helperText={<>
                    <UniStack.Row spacing={1}>
                        <UT.Text xs>{t("filter")}:</UT.Text>
                        {
                            split(search).map((s, i) => {
                                return <UT.Text key={i} xs sx={{ bgcolor: "background.level2", color: "text.icon", pl: 1, pr: 1, borderRadius: "5px" }}>{s}</UT.Text>
                            })
                        }
                    </UniStack.Row>
                </>}
                endDecorator={
                    <>
                        <UniButton
                            small
                            plain
                            error
                            disabled={search === ""}
                            onClick={() => {
                                setSearch("")
                            }}
                        >
                            <UniIcons.Clear />
                        </UniButton>
                    </>
                }
            />
        </>
    )
}

export default UniSearchBox

function split(input: string): string[] {
    return input.split(/  +/).map((s) => s.trim()).filter((s) => s.length > 0);
}