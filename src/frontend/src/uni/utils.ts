import { v4 } from "uuid";

/**
 * compare two objects
 * 
 * @param a object to compare
 * @param b object to compare
 * @returns true if objects are equal
 */
export function compareObjects(a: any, b: any): boolean {
    return (JSON.stringify(a) === JSON.stringify(b))
}

export function copyObject(a: any): any {
    return JSON.parse(
        JSON.stringify(a)
    )
}

/**
 * decode data(object, array, ...) to string
 * @param data data to decode
 * @returns decoded data
 */
export function objToString(data: any): string {
    if (typeof data === "string") return data;

    try {
        return JSON.stringify(data);
    }
    catch (error) {
        console.error(error);
    }

    return "";
}

export function queryFindByArray(value: any, field: string = "id") {
    const filter: any = { "OR": [] }

    for (let v of value) {
        filter.OR.push(
            [field, "==", v]
        )
    }

    if (filter.OR.length) {
        if (filter.OR.length === 1) return [filter.OR[0]]

        return [filter]
    }
    return []
}

export function queryFindNotInArray(values: any, field: string = "id") {
    const filter: any = { "AND": [] }

    for (let v of values) {
        filter.AND.push(
            [field, "!=", v]
        )
    }

    if (filter.AND.length) {
        if (filter.AND.length === 1) return [filter.AND[0]]

        return [filter]
    }
    return []
}

export function getTextField(field: any[], lang: string): string {
    return field.find((v: { data: any, lang: string }) => (v.lang.toLowerCase() === lang.toLowerCase()))?.data || ""
}

/**
 * 
 * @param {object} data data to download
 * @param {string} filename filename, default download
 * @param {string} ext filename extension, default .json
 */
export async function downloadAsJson(data: any, filename = "download", ext = ".json") {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const href = await URL.createObjectURL(blob);
    const link = document.createElement('a');

    link.href = href;
    link.download = filename + ext;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

}

/**
 * 
 * @param {object} data data to download
 * @param {string} filename filename, default download
 * @param {string} ext filename extension, default .json
 */
export async function downloadBlob(data: Blob, filename: string, ext: string) {
    const href = await URL.createObjectURL(data);
    const link = document.createElement('a');

    link.href = href;
    link.download = filename + ext;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

}


export function getId(): string {
    return v4();
}

export function deleteNullValuesFromQuery(src: any, target: any) {
    if (Array.isArray(src)) {
        for (let e of src) {
            if (e === null || e === undefined) continue

            if (e?.AND) {
                const t = { AND: [] }
                deleteNullValuesFromQuery(e.AND, t.AND)
                target.push(t)
                continue
            }

            if (e?.OR) {
                const t = { OR: [] }
                deleteNullValuesFromQuery(e.OR, t.OR)
                target.push(t)
                continue
            }

            if (Array.isArray(e)) {
                const t: any[] = []
                deleteNullValuesFromQuery(e, t)
                target.push(t)
                continue
            }
            target.push(e)
        }
    }
}

export const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));


/**
 * Converts a file size from bytes to a human-readable string with appropriate units.
 *
 * @param size - The size of the file in bytes.
 * @returns A string representing the file size in a human-readable format with two decimal places.
 *
 * @example
 * ```typescript
 * fileSize(1024); // "1.00 KB"
 * fileSize(1048576); // "1.00 MB"
 * fileSize(1073741824); // "1.00 GB"
 * fileSize(1099511627776); // "1.00 TB"
 * ```
 */
export function fileSize(size: number): string {

    var unit = "b"
    var _size = size

    if(_size > 1024) {
        _size = _size / 1024
        unit = "KB"
    }
    if(_size > 1024) {
        _size = _size / 1024
        unit = "MB"
    }
    if(_size > 1024) {
        _size = _size / 1024
        unit = "GB"
    }
    if(_size > 1024) {
        _size = _size / 1024
        unit = "TB"
    }

    return `${_size.toFixed(2)} ${unit}`
}

/**
 * Calculates the byte size of a given Base64 encoded string.
 *
 * @param base64String - The Base64 encoded string to calculate the byte size for.
 * @returns The byte size of the given Base64 encoded string.
 */
export function getBase64ByteSize(base64String: string): number {

    const binaryData = window.atob(base64String);
    const bytes = new Uint8Array(binaryData.length);
    for (let i = 0; i < binaryData.length; i++) {
      bytes[i] = binaryData.charCodeAt(i);
    }
  
    return bytes.length
  }