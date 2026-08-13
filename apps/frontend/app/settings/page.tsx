"use client";

import { useState } from "react";

import type { Settings } from "@/lib/settings";

const defaultSettings: Settings = {
    model: {
        provider: "ollama",
        model: "qwen2.5:3b",
        fallback: false,
    },

    agent: {
        max_steps: 5,
        planner_enabled: true,
        repair_enabled: true,
    },

    guardrails: {
        prompt_injection: true,
        tool_validation: true,
        output_validation: true,
    },

    evaluation: {
        auto_run: true,
        store_traces: true,
        retention_days: 30,
    },
};


function loadSettings(): Settings {
    if (typeof window === "undefined") {
        return defaultSettings;
    }

    try {
        const stored = localStorage.getItem("ai-analytics-settings");

        if (!stored) {
            return defaultSettings;
        }

        const parsed = JSON.parse(stored) as Partial<Settings>;

        return {
            ...defaultSettings,
            ...parsed,

            model: {
                ...defaultSettings.model,
                ...(parsed.model ?? {}),
            },

            agent: {
                ...defaultSettings.agent,
                ...(parsed.agent ?? {}),
            },

            guardrails: {
                ...defaultSettings.guardrails,
                ...(parsed.guardrails ?? {}),
            },

            evaluation: {
                ...defaultSettings.evaluation,
                ...(parsed.evaluation ?? {}),
            },
        };
    } catch (error) {
        console.error("Failed to load settings:", error);
        return defaultSettings;
    }
}


export default function SettingsPage() {

    const [settings, setSettings] =
        useState<Settings>(loadSettings);

    const [saved, setSaved] =
        useState(false);


    function update(
        section: keyof Settings,
        key: string,
        value: string | number | boolean
    ) {

        setSettings((current) => ({
            ...current,

            [section]: {
                ...current[section],
                [key]: value,
            },
        }));

        setSaved(false);
    }


    function changeProvider(provider: string) {

        setSettings((current) => {

            let model = current.model.model;

            if (provider === "ollama") {

                model = "qwen2.5:3b";

            } else if (provider === "bedrock") {

                model =
                    "anthropic.claude-3-haiku-20240307-v1:0";

            }

            return {
                ...current,

                model: {
                    ...current.model,
                    provider,
                    model,
                },
            };
        });

        setSaved(false);
    }


    function saveSettings() {

        try {

            localStorage.setItem(
                "ai-analytics-settings",
                JSON.stringify(settings)
            );

            setSaved(true);

            console.log(
                "[SETTINGS] Saved:",
                settings
            );

        } catch (error) {

            console.error(
                "[SETTINGS] Failed to save:",
                error
            );

            setSaved(false);
        }
    }


    return (
        <main className="p-6">

            <h1 className="text-3xl font-bold mb-8">
                Settings
            </h1>


            <section className="space-y-6">


                {/* ================================================= */}
                {/* Model Configuration */}
                {/* ================================================= */}

                <div className="border rounded p-5">

                    <h2 className="font-semibold mb-4">
                        Model Configuration
                    </h2>


                    <div className="space-y-4">


                        {/* Provider */}

                        <label className="block">

                            <span className="block mb-1">
                                Provider
                            </span>

                            <select
                                className="border rounded p-2"
                                value={
                                    settings.model.provider
                                }
                                onChange={(e) =>
                                    changeProvider(
                                        e.target.value
                                    )
                                }
                            >

                                <option value="ollama">
                                    Ollama
                                </option>

                                <option value="bedrock">
                                    AWS Bedrock
                                </option>

                            </select>

                        </label>


                        {/* Model */}

                        <label className="block">

                            <span className="block mb-1">
                                Model
                            </span>

                            <select
                                className="border rounded p-2"
                                value={
                                    settings.model.model
                                }
                                onChange={(e) =>
                                    update(
                                        "model",
                                        "model",
                                        e.target.value
                                    )
                                }
                            >

                                {settings.model.provider ===
                                    "ollama" && (

                                    <option value="qwen2.5:3b">
                                        qwen2.5:3b
                                    </option>

                                )}


                                {settings.model.provider ===
                                    "bedrock" && (

                                    <option value="anthropic.claude-3-haiku-20240307-v1:0">
                                        Claude 3 Haiku
                                    </option>

                                )}

                            </select>

                        </label>


                        {/* Fallback */}

                        <label className="block">

                            <input
                                type="checkbox"
                                checked={
                                    settings.model.fallback
                                }
                                onChange={(e) =>
                                    update(
                                        "model",
                                        "fallback",
                                        e.target.checked
                                    )
                                }
                            />

                            <span className="ml-2">
                                Enable fallback
                            </span>

                        </label>


                    </div>

                </div>


                {/* ================================================= */}
                {/* Agent Configuration */}
                {/* ================================================= */}

                <div className="border rounded p-5">

                    <h2 className="font-semibold mb-4">
                        Agent Configuration
                    </h2>


                    <label>

                        Max Steps

                        <input
                            className="ml-3 border p-1"
                            type="number"
                            min="1"
                            max="100"
                            value={
                                settings.agent.max_steps
                            }
                            onChange={(e) =>
                                update(
                                    "agent",
                                    "max_steps",
                                    Number(
                                        e.target.value
                                    )
                                )
                            }
                        />

                    </label>

                </div>


                {/* ================================================= */}
                {/* Guardrails */}
                {/* ================================================= */}

                <div className="border rounded p-5">

                    <h2 className="font-semibold mb-4">
                        Guardrails
                    </h2>


                    {Object.entries(
                        settings.guardrails
                    ).map(([key, value]) => (

                        <label
                            key={key}
                            className="block"
                        >

                            <input
                                type="checkbox"
                                checked={value}
                                onChange={(e) =>
                                    update(
                                        "guardrails",
                                        key,
                                        e.target.checked
                                    )
                                }
                            />

                            <span className="ml-2">
                                {key}
                            </span>

                        </label>

                    ))}

                </div>


                {/* ================================================= */}
                {/* Evaluation */}
                {/* ================================================= */}

                <div className="border rounded p-5">

                    <h2 className="font-semibold mb-4">
                        Evaluation
                    </h2>


                    <label>

                        Retention Days

                        <input
                            className="ml-3 border p-1"
                            type="number"
                            min="1"
                            max="3650"
                            value={
                                settings.evaluation
                                    .retention_days
                            }
                            onChange={(e) =>
                                update(
                                    "evaluation",
                                    "retention_days",
                                    Number(
                                        e.target.value
                                    )
                                )
                            }
                        />

                    </label>

                </div>


                {/* ================================================= */}
                {/* Save */}
                {/* ================================================= */}

                <div className="flex items-center gap-4">

                    <button
                        className="
                            mt-6
                            px-4
                            py-2
                            rounded
                            bg-blue-600
                            text-white
                            hover:bg-blue-700
                        "
                        onClick={saveSettings}
                    >
                        Save Changes
                    </button>


                    {saved && (

                        <span className="mt-6 text-green-600">
                            Settings saved
                        </span>

                    )}

                </div>


            </section>

        </main>
    );
}