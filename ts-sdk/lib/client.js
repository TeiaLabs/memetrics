"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Client = void 0;
const utils_1 = require("./utils");
const node_fetch_1 = __importDefault(require("node-fetch"));
class Client {
    static apiKey;
    static apiUrl;
    static appName;
    static setup(appName, apiKey = process.env["MEMETRICS_API_KEY"], apiUrl = process.env["MEMETRICS_URL"]) {
        if (apiKey === undefined)
            throw Error("API Key not found.");
        this.apiKey = apiKey;
        if (apiUrl === undefined)
            throw Error("MeMetrics URL not found.");
        this.apiUrl = `${(0, utils_1.trimEnd)(apiUrl, "/")}/events`;
        this.appName = appName;
    }
    static saveEvent(event) {
        let payload = event;
        payload.app = this.appName;
        return (0, node_fetch_1.default)(this.apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authentication: this.apiKey,
                "X-User-Email": event["actor"]["email"],
            },
            body: JSON.stringify(payload),
        });
    }
    static saveBatch(events) {
        const promises = events.map((event) => {
            return this.saveEvent(event);
        });
        return Promise.all(promises);
    }
}
exports.Client = Client;
