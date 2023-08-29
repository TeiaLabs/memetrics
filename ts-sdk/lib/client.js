"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Client = void 0;
const utils_1 = require("./utils");
const axios_1 = __importDefault(require("axios"));
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
    static async saveEvent(event) {
        let payload = event;
        payload.app = this.appName;
        try {
            await axios_1.default.post(this.apiUrl, payload, {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: this.apiKey,
                    "X-User-Email": event["actor"]["email"],
                },
            });
        }
        catch (e) {
            const error = e;
            let status, message, extra;
            if (error.response) {
                status = error.response.status;
                message = `MeMetrics API responded with ${error.response.status} ${error.response.statusText}`;
                extra = error.response.data;
            }
            else {
                status = 500;
                message = `MeMetrics API responded with ${error.message}`;
            }
            return { status, message, extra };
        }
    }
    static saveBatch(events) {
        const promises = events.map((event) => {
            return this.saveEvent(event);
        });
        return Promise.all(promises);
    }
}
exports.Client = Client;
