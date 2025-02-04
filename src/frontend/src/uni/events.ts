

export const UniEventTypes = {
    localStorage: {
        update: "uni.event.storage.update",
        delete: "uni.event.storage.delete"
    }
}

export function dispatchUniEvent(type: string, eventData: any): void {
    const event = new CustomEvent(type, {detail: eventData});
    window.dispatchEvent(event);
}

export const UNI_EVENT_ENTITY_DELETED = "uni.event.entity.deleted"