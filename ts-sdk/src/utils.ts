export function stripStart(value: string, pattern: string): string {
    if (value.startsWith(pattern)) {
        return value.substring(0, value.lastIndexOf(pattern));
    }
    return value;
}

export function stripEnd(value: string, pattern: string): string {
    if (value.endsWith(pattern)) {
        return value.substring(0, value.lastIndexOf(pattern));
    }
    return value;
}
