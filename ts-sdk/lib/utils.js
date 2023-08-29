"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.stripEnd = exports.stripStart = void 0;
function stripStart(value, pattern) {
    if (value.startsWith(pattern)) {
        return value.substring(0, value.lastIndexOf(pattern));
    }
    return value;
}
exports.stripStart = stripStart;
function stripEnd(value, pattern) {
    if (value.endsWith(pattern)) {
        return value.substring(0, value.lastIndexOf(pattern));
    }
    return value;
}
exports.stripEnd = stripEnd;
