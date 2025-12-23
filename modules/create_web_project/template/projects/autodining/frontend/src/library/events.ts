// src/lib/logger.ts

export const EVENT_TYPES = {
  SEARCH_RESTAURANT: "SEARCH_RESTAURANT",
  TIME_DROPDOWN_OPENED: "TIME_DROPDOWN_OPENED",
  DATE_DROPDOWN_OPENED: "DATE_DROPDOWN_OPENED",
  PEOPLE_DROPDOWN_OPENED: "PEOPLE_DROPDOWN_OPENED",
  SCROLL_VIEW: "SCROLL_VIEW",
  VIEW_RESTAURANT: "VIEW_RESTAURANT",
  BOOK_RESTAURANT: "BOOK_RESTAURANT",
  COUNTRY_SELECTED: "COUNTRY_SELECTED",
  OCCASION_SELECTED: "OCCASION_SELECTED",
  RESERVATION_COMPLETE: "RESERVATION_COMPLETE",
  VIEW_FULL_MENU: "VIEW_FULL_MENU",
  COLLAPSE_MENU: "COLLAPSE_MENU",
  ABOUT_PAGE_VIEW: "ABOUT_PAGE_VIEW",
  ABOUT_FEATURE_CLICK: "ABOUT_FEATURE_CLICK",
  CONTACT_PAGE_VIEW: "CONTACT_PAGE_VIEW",
  CONTACT_CARD_CLICK: "CONTACT_CARD_CLICK",
  CONTACT_FORM_SUBMIT: "CONTACT_FORM_SUBMIT",
  HELP_PAGE_VIEW: "HELP_PAGE_VIEW",
  HELP_CATEGORY_SELECTED: "HELP_CATEGORY_SELECTED",
  HELP_FAQ_TOGGLED: "HELP_FAQ_TOGGLED",
} as const;

export type EventType = (typeof EVENT_TYPES)[keyof typeof EVENT_TYPES];

// Import the SeedVariationManager for event registration
import { SeedVariationManager } from "./utils";

export function logEvent(
  eventType: EventType,
  data: any = {},
  extra_headers: Record<string, string> = {}
) {
  if (typeof window === "undefined") return;

  let user = localStorage.getItem("user");
  if (user === "null") {
    user = null;
  }
  const webAgentId = localStorage.getItem("web_agent_id");
  const validatorId = localStorage.getItem("validator_id");
  const resolvedWebAgentId = webAgentId && webAgentId !== "null" ? webAgentId : "1";
  const resolvedValidatorId = validatorId && validatorId !== "null" ? validatorId : "1";

  // Register the event with the SeedVariationManager to trigger layout changes
  try {
    SeedVariationManager.registerEvent(eventType);
  } catch (err) {
    // Ignorar errores en el registro de eventos - no debe romper la página
    if (process.env.NODE_ENV === "development") {
      console.warn("⚠️ Error registering event:", err);
    }
  }

  // Construir el payload completo que espera el backend
  const eventData = {
    event_name: eventType,
    web_agent_id: resolvedWebAgentId,
    user_id: user,
    data,
    timestamp: new Date().toISOString(),
    validator_id: resolvedValidatorId,
  };

  const backendPayload = {
    web_agent_id: resolvedWebAgentId,
    web_url: window.location.origin,
    validator_id: resolvedValidatorId,
    data: eventData,
  };

  console.log("📦 Logging Event:", backendPayload);

  fetch("/api/log-event", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-WebAgent-Id": resolvedWebAgentId,
      "X-Validator-Id": resolvedValidatorId,
      ...extra_headers,
    },
    body: JSON.stringify(backendPayload),
  }).catch((error) => {
    console.error("❌ Failed to log event:", error);
    throw error;
  });
}
