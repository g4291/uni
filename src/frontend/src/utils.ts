
// datetime utils
const DEFAULT_LOCALE = "cs-CZ"

/**
 * Converts a timestamp to a formatted date and time string.
 * 
 * @param ts - The timestamp to convert.
 * @param locale - The locale to use for formatting the date and time string. Default is "cs-CZ".
 * @returns The formatted date and time string.
 */
export function datetimeStrFromTimestamp(ts: number, locale: string = DEFAULT_LOCALE): string {
    const dt = new Date(ts)

    return dt.toLocaleString(locale)
}

/**
 * Copies the specified data to the clipboard.
 * 
 * @param data - The data to be copied to the clipboard.
 * @param onSuccess - Optional callback function to be called when the data is successfully copied.
 * @param onError - Optional callback function to be called when an error occurs while copying the data.
 */
export function copyToClipboard(data: string, onSuccess?: () => void, onError?: (e: any) => void): void {
    navigator.clipboard.writeText(data).then(
        () => {
            if (onSuccess) onSuccess()
        },
        (err) => {
            if (onError) onError(err)
        }
    )
}

/**
 * Calculates the duration between two given dates in hours, minutes, and seconds.
 * 
 * @param startTime - The starting date.
 * @param endTime - The ending date.
 * @returns A string representation of the duration in the format "Xh Ym Zs".
 */
export function timeDuration(startTime: Date, endTime: Date) {
    const difference = Math.abs(endTime.getTime() - startTime.getTime()) / 1000; // convert to seconds
    const hours = Math.floor(difference / 3600);
    const minutes = Math.floor((difference % 3600) / 60);
    const seconds = Math.floor(difference % 60);

    if (difference < 60) {
        return `${seconds}s`;
    } else if (difference < 3600) {
        return `${minutes}m ${seconds}s`;
    } else {
        return `${hours}h ${minutes}m ${seconds}s`;
    }
}

/**
 * Crop a string to a specified maximum length.
 * If the input string length exceeds the maximum length, it will be cropped and "..." will be appended.
 * If the string is shorter than or equal to the maximum length, it will be returned as is.
 * 
 * @param input - The input string to be cropped.
 * @param maxLength - The maximum length of the cropped string.
 * @returns The cropped string.
 */
export function cropString(input: string, maxLength: number): string {
    // Check if the input string length exceeds the maximum length
    if (input.length > maxLength) {
        // Crop the string to the maximum length and append "..."
        return input.substring(0, maxLength) + '...';
    }
    
    // If the string is shorter than or equal to the maximum length, return it as is
    return input;
}




/**
 * Generates a contrasting color in hexadecimal format based on the given index and maximum index.
 *
 * @param index - The current index for which to generate the color.
 * @param maxIndex - The maximum index value, used to normalize the hue calculation.
 * @param reverse - Whether to reverse the hue value before converting it to RGB. Default is false.
 * @returns A string representing the contrasting color in hexadecimal format.
 */
export function getContrastingColor(index: number, maxIndex: number, reverse: boolean = false): string {
    const hue = (index / maxIndex) * 360;
    const saturation = 1;
    const baseLightness = 0.5;

    // Determine the lightness based on whether we are reversing for contrast
    const lightness = reverse ? (baseLightness > 0.5 ? 0.2 : 0.8) : baseLightness;

    const [r, g, b] = hslToRgb(hue, saturation, lightness);
    return rgbToHex(r, g, b);
}

export function getMaxContrastColor(hex: string): string {
    // First, ensure the hex is properly formatted (e.g., #RRGGBB)
    if (hex.startsWith('#')) {
      hex = hex.substring(1);
    }
  
    // Check if the hex color code is a valid length (3 or 6)
    if (hex.length !== 3 && hex.length !== 6) {
      throw new Error('Invalid hex color format');
    }
  
    // Expand shorthand form (e.g., "03F") to full form (e.g., "0033FF")
    if (hex.length === 3) {
      hex = hex.split('').map(char => char + char).join('');
    }
  
    // Parse the r, g, b values from the hex string
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);
  
    // Calculate the relative luminance using the formula:
    // Relative luminance = 0.2126*R + 0.7152*G + 0.0722*B
    const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
  
    // Return the color with maximum contrast
    // A threshold of 128 is commonly used to decide between black and white
    return luminance > 128 ? '#000000' : '#FFFFFF';
  }

function hslToRgb(h: number, s: number, l: number): [number, number, number] {
    const c = (1 - Math.abs(2 * l - 1)) * s;
    const x = c * (1 - Math.abs((h / 60) % 2 - 1));
    const m = l - c / 2;
    let r = 0, g = 0, b = 0;

    if (0 <= h && h < 60) {
        r = c; g = x; b = 0;
    } else if (60 <= h && h < 120) {
        r = x; g = c; b = 0;
    } else if (120 <= h && h < 180) {
        r = 0; g = c; b = x;
    } else if (180 <= h && h < 240) {
        r = 0; g = x; b = c;
    } else if (240 <= h && h < 300) {
        r = x; g = 0; b = c;
    } else if (300 <= h && h < 360) {
        r = c; g = 0; b = x;
    }

    const toRgb = (color: number) => Math.round((color + m) * 255);
    return [toRgb(r), toRgb(g), toRgb(b)];
}

function rgbToHex(r: number, g: number, b: number): string {
    const toHex = (n: number) => n.toString(16).padStart(2, '0');
    return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}