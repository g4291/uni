import { tabClasses } from "@mui/joy"
import { SxProps } from "@mui/joy/styles/types"

export const APP_NAME = "UNI"
export const SERVER_URL = (window.location.port === "3000")
    ? "http://" + window.location.hostname + ":8080/api/v1" // development
    : window.location.origin + "/api/v1"  //production
export const DEBUG = true
export const GOOGLE_OAUTH_CLIENT_ID = ""

// storage keys
export const LIST_PAGE_SIZE_STORAGE_KEY = "uni.listPageSize"


// defaults 
export const DEFAULT_PAGE_SIZE = 10
export const DEFAULT_DETAIL_MAX_WIDTH = "95dvw"

export const LIST_SPACING = "300px"
export const LIST_SPACING_DETAIL = "450px"


export const TAB_SX = {
    [`& .${tabClasses.root}`]: {
      fontSize: 'sm',
      fontWeight: 'lg',
      [`&[aria-selected="true"]`]: {
        color: 'primary.500',
        bgcolor: 'background.surface',
      },
      [`&.${tabClasses.focusVisible}`]: {
        outlineOffset: '-4px',
      },
    },
  } as SxProps


  export const MAX_UPLOAD_SIZE = 1024*1024*20 // 20MB
  export const MAX_UPLOAD_FILES = 1024
  export const ACCEPT_IMAGES = {
    "image/jpeg": [
        ".jpg",
        ".jpeg",

    ],
    "image/png": [
        ".png"
    ],
    "image/gif": [
        ".gif"
    ],
}
  export const ACCEPT_TEXT = {
    "text/plain": [
        ".txt",
        ".bio",

    ]
}

export const LIST_UPDATE_INTERVAL = 1000 * 20
export const DETAIL_UPDATE_INTERVAL = 1000 * 10