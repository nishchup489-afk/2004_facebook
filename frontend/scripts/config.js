var API_URL =
    "http://127.0.0.1:8000";


function parseFrontendEnv(
    text
) {

    const values = {};


    text
        .split(/\r?\n/)
        .forEach(line => {

            const trimmed =
                line.trim();


            if (
                !trimmed ||
                trimmed.startsWith("#")
            ) {
                return;
            }


            const separator =
                trimmed.indexOf("=");

            if (separator === -1) {
                return;
            }


            const key =
                trimmed
                    .slice(0, separator)
                    .trim();

            const value =
                trimmed
                    .slice(separator + 1)
                    .trim()
                    .replace(/^["']|["']$/g, "");


            values[key] = value;
        });


    return values;
}


async function loadFrontendConfig() {

    try {

        const response = await fetch(
            "/frontend/.env",
            {
                cache: "no-store"
            }
        );


        if (!response.ok) {
            return {
                API_URL
            };
        }


        const values =
            parseFrontendEnv(
                await response.text()
            );

        const configuredApiUrl =
            values.FRONTEND_API_URL ||
            values.API_URL;


        if (configuredApiUrl) {
            API_URL =
                configuredApiUrl;
        }


    } catch (error) {

        console.warn(
            "Could not load frontend .env. Using default API URL.",
            error
        );
    }


    window.API_URL =
        API_URL;


    return {
        API_URL
    };
}


async function ensureFrontendConfig() {

    if (window.FRONTEND_CONFIG_READY) {
        await window.FRONTEND_CONFIG_READY;
    }


    return {
        API_URL
    };
}


window.FRONTEND_CONFIG_READY =
    loadFrontendConfig();
