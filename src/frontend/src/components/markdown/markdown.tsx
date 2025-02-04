import React from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import remarkGfm from 'remark-gfm';


import { useUniThemeMode } from '../../uni/theme'
import { useUniTranslator } from '../../uni/translator'
import useUniTouaster from '../../uni/hooks/toaster';
import './markdown.css'
import { copyToClipboard } from '../../utils';
import { v4 } from 'uuid';

export const loadCSS = (href: string, id: string): Promise<void> => {
    return new Promise((resolve, reject) => {
        let linkElement = document.getElementById(id) as HTMLLinkElement

        if (linkElement) {
            // Update href if link already exists
            linkElement.href = href
            resolve()
        } else {
            // Create new link element
            linkElement = document.createElement('link')
            linkElement.id = id
            linkElement.rel = 'stylesheet'
            linkElement.type = 'text/css'
            linkElement.href = href
            linkElement.onload = () => resolve()
            linkElement.onerror = () => reject(new Error(`Failed to load CSS: ${href}`))
            document.head.appendChild(linkElement)
        }
    })
}

interface ICodeBlockProps {
    node: any
    inline?: boolean
    className?: string
    children: React.ReactNode
    [key: string]: any
}

// Define the CodeBlock component
function CodeBlock({ node, inline, className, children, ...props }: ICodeBlockProps): JSX.Element {
    const [isCopied, setIsCopied] = React.useState(false)
    const t = useUniTranslator()
    const toast = useUniTouaster()

    const id = v4()

    const handleCopy = () => {
        const codeToCopy = document.getElementById(id)?.innerText
        if (!codeToCopy) return
        copyToClipboard(codeToCopy, () =>{
            setIsCopied(true)
            setTimeout(() => setIsCopied(false), 3000)
        }, (e) => {
            setIsCopied(false)
            toast("error", "could not copy text", "error")
        })
    }
    
    const match = /language-(\w+)/.exec(className || '')
    const language = match ? match[1] : ''
    if (language === '') {
        return <><b><i>{children}</i></b></>
        }

    return !inline ? (
        <div className="code-block">
            <button className="copy-button" onClick={handleCopy}>
                {isCopied ? t("copied")+"!" : t("copy")}
            </button>
            <pre>
                <code id={id} className={className} {...props}>
                    {children}
                </code>
            </pre>
        </div>
    ) : (
        <code id={id} className={className} {...props}>
            {children}
        </code>
    )
}

interface MarkdownDisplayProps {
    markdownText: string
}
export function MarkdownDisplay({ markdownText }: MarkdownDisplayProps): JSX.Element {
    const [theme] = useUniThemeMode()
    const toast = useUniTouaster()

    React.useEffect(() => {
        const themeCSS = theme === 'light' ? '/webclient/styles/github.css' : '/webclient/styles/github-dark.css'
        loadCSS(themeCSS, 'syntax-theme').catch((err) => {
            toast("error", "Error loading CSS", "error")
            console.error('Error loading CSS:', err)
        })

        // eslint-disable-next-line
    }, [theme])

    return (
        <div className="markdown-body">
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
                components={{ code: CodeBlock } as any}
            >
                {markdownText}
            </ReactMarkdown>
        </div>
    )
}

export default MarkdownDisplay
