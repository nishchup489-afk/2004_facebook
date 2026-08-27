const IS_LOCAL =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1";

const API_URL = IS_LOCAL
    ? "http://127.0.0.1:8000"
    : "https://two004-facebook.onrender.com";

window.API_URL = API_URL;

window.FRONTEND_CONFIG_READY = Promise.resolve({
    API_URL
});

async function ensureFrontendConfig() {
    await window.FRONTEND_CONFIG_READY;

    return {
        API_URL: window.API_URL
    };
}
