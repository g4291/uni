// Fade.tsx
import React from 'react';
import './fade.css';

export const UNI_FADE_CONFIG = {
    defaultDuration: 200,
} as {
    defaultDuration: number
}

interface FadeProps {
    show: boolean
    children: React.ReactNode
    duration?: number
    fullWidth?: boolean
}

export function UniFade(props: FadeProps): JSX.Element | null {
    const [shouldRender, setShouldRender] = React.useState<boolean>(props.show);
    const [visible, setVisible] = React.useState<boolean>(false);
    const duration = props.duration || UNI_FADE_CONFIG.defaultDuration;

    React.useEffect(() => {
        let timeoutId: NodeJS.Timeout;

        if (props.show) {
            setShouldRender(true); // Mount the component
            // Delay setting visible to true to trigger transition
            timeoutId = setTimeout(() => {
                setVisible(true);
            }, 0);
        } else {
            setVisible(false); // Start fade-out transition
        }

        return () => {
            clearTimeout(timeoutId);
        };
    }, [props.show]);

    const onTransitionEnd = () => {
        if (!visible) {
            setShouldRender(false); // Unmount after fade-out
        }
    };

    // Inline style to set the CSS variable for duration
    const style = {
        '--uni-animation-fade-duration': `${duration}ms`,
        "width": props.fullWidth ? "100%" : "auto",
    } as React.CSSProperties;

    return shouldRender ? (
        <div
            className={`uni-fade ${visible ? 'show' : ''}`}
            onTransitionEnd={onTransitionEnd}
            style={style}
        >
            {props.children}
        </div>
    ) : null;

}

export default UniFade
