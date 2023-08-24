"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.trimEnd = void 0;
function trimEnd(value, pattern) {
    if (value.endsWith(pattern)) {
        return value.substring(0, value.lastIndexOf(pattern));
    }
    return value;
}
exports.trimEnd = trimEnd;
