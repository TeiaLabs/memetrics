export function trimEnd(value: string, pattern: string): string {
    if (value.endsWith(pattern)) {
        return value.substring(0, value.lastIndexOf(pattern));
    }
    return value;
}
