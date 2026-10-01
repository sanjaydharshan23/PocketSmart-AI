// ============================================================
// PocketSmart AI - Frontend JavaScript
// ============================================================

"use strict";


// ============================================================
// API HELPER
// ============================================================

async function api(url, options = {}) {
    const response = await fetch(url, {
        credentials: "include",
        ...options
    });

    let data = null;

    try {
        data = await response.json();
    } catch (error) {
        data = null;
    }

    if (!response.ok) {
        let message = "Something went wrong.";

        if (data) {
            if (typeof data.detail === "string") {
                message = data.detail;
            } else if (data.message) {
                message = data.message;
            }
        }

        throw new Error(message);
    }

    return data;
}


// ============================================================
// HTML ESCAPE HELPER
// ============================================================

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ============================================================
// AUTH FORM
// ============================================================

function bindAuthForm(id, url, redirect) {
    const form = document.getElementById(id);

    if (!form) {
        return;
    }

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const message = document.getElementById("form-message");

        if (message) {
            message.textContent = "";
            message.className = "message";
        }

        try {
            const formData = new FormData(form);

            const body = Object.fromEntries(
                formData.entries()
            );

            await api(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(body)
            });

            if (message) {
                message.className = "message success";
                message.textContent = "Success";
            }

            setTimeout(function () {
                window.location.href = redirect;
            }, 400);

        } catch (error) {
            console.error(error);

            if (message) {
                message.className = "message error";
                message.textContent = error.message;
            }
        }
    });
}


// ============================================================
// PLANNER FORM
// ============================================================

function bindPlanner(id, url, multipart = false) {

    const form = document.getElementById(id);

    if (!form) {
        return;
    }

    form.addEventListener("submit", async function (e) {

        e.preventDefault();

        const message = document.getElementById("form-message");
        const results = document.getElementById("results");

        if (message) {
            message.textContent = "Generating...";
            message.className = "message";
        }

        if (results) {
            results.innerHTML = "";
        }

        try {

            let requestOptions = {
                method: "POST"
            };


            // ==================================================
            // MULTIPART FORM
            // Used mainly for Jewelry image upload
            // ==================================================

            if (multipart) {

                const body = new FormData(form);

                requestOptions.body = body;

            }

            // ==================================================
            // NORMAL JSON FORM
            // Home / Party
            // ==================================================

            else {

                const formData = new FormData(form);

                // IMPORTANT:
                // raw exists ONLY inside this block.
                // Everything that uses raw is also inside this block.
                const raw = Object.fromEntries(
                    formData.entries()
                );


                // ==================================================
                // HOME PLANNER
                // ==================================================

                if (url.includes("home")) {

                    raw.budget = Number(raw.budget);

                    raw.rooms = raw.rooms
                        ? raw.rooms
                            .split(",")
                            .map(function (x) {
                                return x.trim();
                            })
                            .filter(Boolean)
                        : [];


                    // Quantities JSON
                    if (raw.quantities) {

                        try {

                            raw.quantities = JSON.parse(
                                raw.quantities
                            );

                        } catch (error) {

                            throw new Error(
                                "Quantities must be valid JSON"
                            );
                        }

                    } else {

                        raw.quantities = {};
                    }
                }


                // ==================================================
                // PARTY PLANNER
                // ==================================================

                else {

                    raw.budget = Number(raw.budget);

                    if (raw.guests !== undefined) {
                        raw.guests = Number(raw.guests);
                    }
                }


                // ==================================================
                // JSON REQUEST
                // ==================================================

                requestOptions.headers = {
                    "Content-Type": "application/json"
                };

                requestOptions.body = JSON.stringify(raw);
            }


            // ==================================================
            // SEND REQUEST
            // ==================================================

            const data = await api(
                url,
                requestOptions
            );


            // ==================================================
            // SUCCESS
            // ==================================================

            if (message) {
                message.textContent = "";
            }

            if (results) {
                renderResults(results, data);
            }

        } catch (error) {

            console.error(
                "Planner error:",
                error
            );

            if (message) {
                message.className = "message error";
                message.textContent = error.message;
            }
        }
    });
}


// ============================================================
// RENDER AI RESULTS
// ============================================================

function renderResults(element, data) {

    if (!element) {
        return;
    }

    const recommendations =
        Array.isArray(data.recommendations)
            ? data.recommendations
            : [];

    const tips =
        Array.isArray(data.tips)
            ? data.tips
            : [];


    const budget =
        Number(data.budget || 0);


    const summary =
        data.summary ||
        "Here are your recommendations.";


    const aiLabel =
        data.ai_generated
            ? "AI generated"
            : "Fallback mode";


    // ============================================================
    // RECOMMENDATION CARDS
    // ============================================================

    const recommendationHtml =
        recommendations.map(function (item) {

            const category =
                item.category || "";

            const platform =
                item.platform || "";

            const title =
                item.title || "Recommendation";

            const description =
                item.description || "";

            const price =
                Number(item.estimated_price || 0);

            const why =
                item.why || "";

            const url =
                item.url || "#";


            return `
                <article class="recommendation">

                    <span class="tag">
                        ${escapeHtml(category)}
                        ·
                        ${escapeHtml(platform)}
                    </span>

                    <h3>
                        ${escapeHtml(title)}
                    </h3>

                    <p>
                        ${escapeHtml(description)}
                    </p>

                    <p class="price">
                        ₹${price.toLocaleString("en-IN")}
                    </p>

                    <p>
                        ${escapeHtml(why)}
                    </p>

                    ${
                        url !== "#"
                            ? `
                                <a
                                    href="${escapeHtml(url)}"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    View search results ↗
                                </a>
                            `
                            : ""
                    }

                </article>
            `;

        }).join("");


    // ============================================================
    // TIPS
    // ============================================================

    const tipsHtml =
        tips.map(function (tip) {

            return `
                <li>
                    ${escapeHtml(tip)}
                </li>
            `;

        }).join("");


    // ============================================================
    // FINAL RESULT
    // ============================================================

    element.innerHTML = `

        <div class="result-head">

            <div>

                <span class="tag">
                    ${escapeHtml(aiLabel)}
                </span>

                <h2>
                    ${escapeHtml(summary)}
                </h2>

            </div>

            <strong>
                Budget ₹${budget.toLocaleString("en-IN")}
            </strong>

        </div>


        <div class="result-grid">

            ${
                recommendationHtml ||
                `
                    <div class="form-card">
                        <p>
                            No recommendations were returned.
                        </p>
                    </div>
                `
            }

        </div>


        ${
            tips.length
                ? `
                    <div class="form-card">

                        <h3>
                            Planning tips
                        </h3>

                        <ul>
                            ${tipsHtml}
                        </ul>

                    </div>
                `
                : ""
        }

    `;
}


// ============================================================
// LOGOUT
// ============================================================

async function logout() {

    try {

        await api("/api/auth/logout", {
            method: "POST"
        });

    } catch (error) {

        console.error(
            "Logout error:",
            error
        );

    } finally {

        window.location.href = "/login";
    }
}


// ============================================================
// PAGE INITIALIZATION
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        // --------------------------------------------------------
        // LOGIN
        // --------------------------------------------------------

        bindAuthForm(
            "login-form",
            "/api/auth/login",
            "/dashboard"
        );


        // --------------------------------------------------------
        // REGISTER
        // --------------------------------------------------------

        bindAuthForm(
            "register-form",
            "/api/auth/register",
            "/login"
        );


        // --------------------------------------------------------
        // HOME PLANNER
        // --------------------------------------------------------

        bindPlanner(
            "home-form",
            "/api/generate-home",
            false
        );


        // --------------------------------------------------------
        // PARTY PLANNER
        // --------------------------------------------------------

        bindPlanner(
            "party-form",
            "/api/generate-party",
            false
        );


        // --------------------------------------------------------
        // JEWELRY PLANNER
        // --------------------------------------------------------

        bindPlanner(
            "jewelry-form",
            "/api/generate-jewelry",
            true
        );


        // --------------------------------------------------------
        // LOGOUT BUTTON
        // --------------------------------------------------------

        const logoutButton =
            document.getElementById("logout-button");

        if (logoutButton) {

            logoutButton.addEventListener(
                "click",
                function (e) {

                    e.preventDefault();

                    logout();
                }
            );
        }

    }
);