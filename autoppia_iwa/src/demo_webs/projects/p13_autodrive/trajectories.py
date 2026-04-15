from __future__ import annotations

import datetime

from autoppia_iwa.src.data_generation.tests.classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import Trajectory
from autoppia_iwa.src.execution.actions.actions import ClickAction, EvaluateAction, HoldKeyAction, NavigateAction, SendKeysIWAAction, TypeAction, WaitAction
from autoppia_iwa.src.execution.actions.base import BaseAction, Selector, SelectorType

PROJECT_NUMBER = 13
WEB_PROJECT_ID = "autodrive"

BASE = "http://localhost:8012"
DEFAULT_SEED = 1

# Seeds from autodrive_tasks.json (per-task URLs use ?seed=…)
SEED_ENTER_LOCATION = 317
SEED_ENTER_DESTINATION = 462
SEED_SEARCH_LOCATION = 279
SEED_SEARCH_DESTINATION = 992
SEED_SELECT_DATE = 932
SEED_SELECT_TIME = 999
SEED_NEXT_PICKUP = 766
SEED_SEARCH = 410
SEED_SELECT_CAR = 537
SEED_RESERVE_RIDE = 674
SEED_TRIP_DETAILS = 974
SEED_CANCEL_RESERVATION = 854

# Addresses referenced in autodrive_tasks.json (and places.json)
LOC_1HOTEL = "1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA"
LOC_VAN_NESS = "100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA"
LOC_PORTLAND_ZOO = "Portland Maritime Zoo - 674 Second St, Portland, OR 97245, USA"
LOC_CORPORATE_TOWER = "Corporate Tower - 2976 Pine St, Houston, TX 77069, USA"
LOC_PHOENIX_LIBERAL_ARTS = "Phoenix Liberal Arts School - 6551 Jefferson St, Phoenix, AZ 85021, USA"
LOC_LINCOLN_GARDEN_MIAMI = "Lincoln Garden - 7904 Lincoln Ave, Miami, FL 33200, USA"
LOC_SFO = "San Francisco Airport (SFO) - San Francisco, CA 94128, USA"
LOC_CAFE_MAPLE = "Cafe Restaurant - 4629 Maple Dr, Chicago, IL 60608, USA"

_CAL_POP = "//div[@data-testid='date-picker-input-popover']"
# shadcn DayPicker: day cells are ghost buttons with h-8 w-8 (see web_13 DatePickerInput).
_CAL_DAY_BTN = f"{_CAL_POP}//button[contains(@class,'h-8')][contains(@class,'w-8')][not(@disabled)][not(contains(@class,'day-outside'))]"
PICKUP_CARD_ID = "dyn-pickup-card-0-3061"
PICK_DATE_JS = r"""async (params) => {
  const { year, month, day } = params;
  const MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];
  const calendar = document.querySelector('[data-testid="date-picker-input-calendar"]');
  if (!calendar) return { ok: false, error: "no calendar" };

  const parseCaption = () => {
    const el =
      calendar.querySelector(".rdp-caption_start .text-sm.font-medium") ||
      calendar.querySelector('[role="presentation"].text-sm.font-medium');
    const text = el?.textContent?.trim() ?? "";
    const m = text.match(/^(\w+)\s+(\d{4})$/);
    if (!m) return null;
    const mi = MONTHS.indexOf(m[1]);
    if (mi < 0) return null;
    return { monthIndex: mi, year: Number(m[2], 10) };
  };

  const targetKey = year * 12 + (month - 1);
  for (let i = 0; i < 36; i++) {
    const cur = parseCaption();
    if (!cur) return { ok: false, error: "caption" };
    const curKey = cur.year * 12 + cur.monthIndex;
    if (curKey === targetKey) break;
    const btn =
      curKey > targetKey
        ? calendar.querySelector('button[name="previous-month"]')
        : calendar.querySelector('button[name="next-month"]');
    if (!btn || btn.disabled) return { ok: false, error: "nav" };
    btn.click();
    await new Promise((r) => setTimeout(r, 0));
  }

  const dayBtn = [...calendar.querySelectorAll('button[name="day"]')].find(
    (btn) =>
      !btn.classList.contains("day-outside") &&
      !btn.disabled &&
      Number(btn.textContent.trim()) === day
  );
  if (!dayBtn) return { ok: false, error: "day not found" };

  dayBtn.scrollIntoView({ block: "nearest", inline: "nearest" });
  dayBtn.click();
  return { ok: true };
}"""


def _trip(seed: int = DEFAULT_SEED) -> str:
    return f"{BASE}/ride/trip?seed={seed}"


def _pickupnow(seed: int = DEFAULT_SEED) -> str:
    return f"{BASE}/ride/trip/pickupnow?seed={seed}"


def _trips(seed: int = DEFAULT_SEED) -> str:
    return f"{BASE}/ride/trip/trips?seed={seed}"


def _confirmation(seed: int = DEFAULT_SEED) -> str:
    return f"{BASE}/ride/trip/confirmation?seed={seed}"


def _ph_pickup() -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="placeholder", value="Pickup location")


def _ph_dropoff() -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="placeholder", value="Dropoff location")


def _enter_pickup(text: str) -> list[BaseAction]:
    return [
        ClickAction(selector=_ph_pickup()),
        TypeAction(selector=_ph_pickup(), text=text),
        SendKeysIWAAction(keys="Enter"),
        WaitAction(time_seconds=0.45),
    ]


def _enter_dropoff(text: str) -> list[BaseAction]:
    return [
        ClickAction(selector=_ph_dropoff()),
        TypeAction(selector=_ph_dropoff(), text=text),
        WaitAction(time_seconds=0.25),
        SendKeysIWAAction(keys="Enter"),
        WaitAction(time_seconds=0.55),
    ]


def _type_pickup_for_search(text: str) -> list[BaseAction]:
    """Typing in pickup logs SEARCH_LOCATION with `value` → event.location (per keystroke)."""
    return [
        ClickAction(selector=_ph_pickup()),
        TypeAction(selector=_ph_pickup(), text=text),
        WaitAction(time_seconds=0.35),
    ]


def _type_dropoff_for_search(text: str) -> list[BaseAction]:
    return [
        ClickAction(selector=_ph_dropoff()),
        TypeAction(selector=_ph_dropoff(), text=text),
        WaitAction(time_seconds=0.35),
    ]


def _prime_schedule(date_iso: str, time_hhmm: str, seed: int = DEFAULT_SEED) -> list[BaseAction]:
    return [
        EvaluateAction(
            script=f"""() => {{
                sessionStorage.setItem('ud_pickupdate', {date_iso!r});
                sessionStorage.setItem('ud_pickuptime', {time_hhmm!r});
                return true;
            }}"""
        ),
        NavigateAction(url=_trip(seed)),
        WaitAction(time_seconds=1.15),
    ]


def _open_pickupnow_date_popover() -> list[BaseAction]:
    return [
        ClickAction(
            selector=Selector(
                type=SelectorType.ATTRIBUTE_VALUE_SELECTOR,
                attribute="data-testid",
                value="date-picker-input-trigger",
            )
        ),
        WaitAction(time_seconds=0.45),
    ]


def _pick_calendar_day_index(ordinal: int = 5) -> list[BaseAction]:
    """Pick Nth selectable in-month day (ordinal>=2 avoids relying only on a sparse first row)."""
    return [
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value=f"({_CAL_DAY_BTN})[{ordinal}]",
            )
        ),
        WaitAction(time_seconds=0.4),
    ]


def _close_date_popover() -> list[BaseAction]:
    return [
        SendKeysIWAAction(keys="Escape"),
        WaitAction(time_seconds=0.45),
    ]


def _open_time_slot_panel() -> list[BaseAction]:
    return [
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value=("//section[@data-card-type='pickup-scheduler']//div[contains(@class,'mb-7')]//div[contains(@class,'cursor-pointer')][contains(@class,'border-gray-200')]"),
            )
        ),
        WaitAction(time_seconds=0.4),
    ]


def _click_time_label_contains(substr: str) -> list[BaseAction]:
    return [
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value=(f"//div[contains(@id,'time-slots')]//button[contains(normalize-space(.),{substr!r})][1]"),
            )
        ),
        WaitAction(time_seconds=0.3),
    ]


def _pickupnow_next_button() -> list[BaseAction]:
    return [
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value=(
                    "//section[@data-card-type='pickup-scheduler']"
                    "//button[contains(@class,'text-white')][contains(@class,'font-bold')]"
                    "[contains(@class,'rounded-md') or contains(@class,'rounded-sm') or contains(@class,'rounded-full')]"
                ),
            )
        ),
        WaitAction(time_seconds=0.6),
    ]


def _click_search() -> list[BaseAction]:
    """Trip form CTA: label is seed-variant text (e.g. 'Look for ride'), not always 'Search'."""
    return [
        WaitAction(time_seconds=0.65),
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value=("//button[contains(@class,'rounded-md')][contains(@class,'h-10')][contains(@class,'font-bold')][not(contains(@class,'cursor-not-allowed'))]"),
            )
        ),
        WaitAction(time_seconds=0.75),
    ]


def _wait_ride_list() -> list[BaseAction]:
    return [WaitAction(time_seconds=1.1)]


def _click_first_ride_card() -> list[BaseAction]:
    """First ride row in results (seeded catalog may omit template names like AutoDriverX)."""
    return [
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value=("(//div[contains(@class,'cursor-pointer')][.//span[contains(@class,'font-semibold')][string-length(normalize-space(.))>1]])[1]"),
            )
        ),
        WaitAction(time_seconds=0.45),
    ]


def _click_ride_card_substr(substr: str) -> list[BaseAction]:
    return [
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value=(f"(//div[contains(@class,'cursor-pointer')][.//span[contains(@class,'font-semibold')][contains(normalize-space(.),{substr!r})]])[1]"),
            )
        ),
        WaitAction(time_seconds=0.45),
    ]


def _click_first_ride_not_named(excluded: str) -> list[BaseAction]:
    return [
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value=(f"//div[contains(@class,'cursor-pointer')][.//span[contains(@class,'font-semibold')][normalize-space()!='{excluded}']][1]"),
            )
        ),
        WaitAction(time_seconds=0.4),
    ]


def _click_reserve_ride_bar() -> list[BaseAction]:
    """Bottom bar CTA: label is seed-variant (e.g. 'Reserve trip'), not always 'Reserve ride'."""
    return [
        WaitAction(time_seconds=0.5),
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value=(
                    "//div[contains(@class,'fixed')][contains(@class,'z-50')]"
                    "//button[contains(@class,'rounded-md')][contains(@class,'font-bold')]"
                    "[not(@disabled)][not(contains(@class,'cursor-not-allowed'))]"
                ),
            )
        ),
        WaitAction(time_seconds=2.2),
    ]


# --- Prompts from autodrive_tasks.json; CheckEventTest payloads below (import-time init, no JSON I/O). ---

_RAW_TESTS: dict[str, list[dict]] = {
    "ENTER_LOCATION": [
        {"type": "CheckEventTest", "event_name": "ENTER_LOCATION", "event_criteria": {"location": {"operator": "not_contains", "value": "vyf"}}, "description": "Check if specific event was triggered"}
    ],
    "ENTER_DESTINATION": [
        {
            "type": "CheckEventTest",
            "event_name": "ENTER_DESTINATION",
            "event_criteria": {"destination": "Portland Maritime Zoo - 674 Second St, Portland, OR 97245, USA"},
            "description": "Check if specific event was triggered",
        }
    ],
    "SEARCH_LOCATION": [
        {
            "type": "CheckEventTest",
            "event_name": "SEARCH_LOCATION",
            "event_criteria": {"destination": "Corporate Tower - 2976 Pine St, Houston, TX 77069, USA"},
            "description": "Check if specific event was triggered",
        }
    ],
    "SEARCH_DESTINATION": [
        {
            "type": "CheckEventTest",
            "event_name": "SEARCH_DESTINATION",
            "event_criteria": {"destination": "Phoenix Liberal Arts School - 6551 Jefferson St, Phoenix, AZ 85021, USA"},
            "description": "Check if specific event was triggered",
        }
    ],
    "SELECT_DATE": [
        {"type": "CheckEventTest", "event_name": "SELECT_DATE", "event_criteria": {"date": {"operator": "greater_than", "value": "2026-04-06"}}, "description": "Check if specific event was triggered"}
    ],
    "SELECT_TIME": [{"type": "CheckEventTest", "event_name": "SELECT_TIME", "event_criteria": {"time": "19:20:00"}, "description": "Check if specific event was triggered"}],
    "NEXT_PICKUP": [
        {
            "type": "CheckEventTest",
            "event_name": "NEXT_PICKUP",
            "event_criteria": {"date": {"operator": "greater_than", "value": "2026-04-06"}, "time": {"operator": "not_equals", "value": "23:10:00"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "SEARCH": [
        {
            "type": "CheckEventTest",
            "event_name": "SEARCH",
            "event_criteria": {
                "location": {"operator": "not_equals", "value": "Park Resort - 4675 Second St, Washington, DC 20076, USA"},
                "destination": {"operator": "not_equals", "value": "Phoenix Community College - 7346 Lincoln Ave, Phoenix, AZ 85034, USA"},
                "scheduled": {"operator": "less_equal", "value": "2026-04-03 22:00:00"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "SELECT_CAR": [
        {
            "type": "CheckEventTest",
            "event_name": "SELECT_CAR",
            "event_criteria": {
                "location": {"operator": "contains", "value": "- Phoenix,"},
                "destination": {"operator": "not_equals", "value": "Atlanta Medical Hospital - 3188 First Ave, Atlanta, GA 30348, USA"},
                "ride_name": {"operator": "not_contains", "value": "pmc"},
                "scheduled": {"operator": "greater_than", "value": "2026-04-05 15:30:00"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "RESERVE_RIDE": [
        {
            "type": "CheckEventTest",
            "event_name": "RESERVE_RIDE",
            "event_criteria": {
                "location": {"operator": "not_contains", "value": "fbs"},
                "destination": {"operator": "not_equals", "value": "Chase Center - 1 Warriors Way, San Francisco, CA 94158, USA"},
                "ride_name": {"operator": "contains", "value": "ed"},
                "scheduled": {"operator": "greater_equal", "value": "2026-04-08 16:30:00"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "TRIP_DETAILS": [
        {
            "type": "CheckEventTest",
            "event_name": "TRIP_DETAILS",
            "event_criteria": {
                "location": "Lincoln Garden - 7904 Lincoln Ave, Miami, FL 33200, USA",
                "destination": {"operator": "contains", "value": "S"},
                "ride_name": {"operator": "contains", "value": "V 14"},
                "scheduled": {"operator": "greater_equal", "value": "2026-04-03 14:20:00"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "CANCEL_RESERVATION": [
        {
            "type": "CheckEventTest",
            "event_name": "CANCEL_RESERVATION",
            "event_criteria": {
                "location": "Cafe Restaurant - 4629 Maple Dr, Chicago, IL 60608, USA",
                "destination": "Cafe Restaurant - 4629 Maple Dr, Chicago, IL 60608, USA",
                "ride_name": {"operator": "not_equals", "value": "Night 64"},
                "scheduled": {"operator": "greater_than", "value": "2026-04-04 15:30:00"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
}

_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _uc(use_case: str, prompt: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(name=use_case, prompt=prompt, actions=actions, tests=_TESTS[use_case])


TODAY = datetime.date.today()


ENTER_LOCATION = _uc(
    "ENTER_LOCATION",
    prompt="Enter and select a location that does NOT contain 'vyf'.",
    actions=[
        NavigateAction(url=_trip(SEED_ENTER_LOCATION)),
        WaitAction(time_seconds=0.85),
        *_enter_pickup(LOC_1HOTEL),
    ],
)

ENTER_DESTINATION = _uc(
    "ENTER_DESTINATION",
    prompt=("Enter destination to retrieve details for the location that equals 'Portland Maritime Zoo - 674 Second St, Portland, OR 97245, USA'."),
    actions=[
        NavigateAction(url=_trip(SEED_ENTER_DESTINATION)),
        WaitAction(time_seconds=0.85),
        *_enter_dropoff(LOC_PORTLAND_ZOO),
    ],
)

SEARCH_LOCATION = _uc(
    "SEARCH_LOCATION",
    prompt="Search location for the destination that equals 'Corporate Tower - 2976 Pine St, Houston, TX 77069, USA'.",
    actions=[
        NavigateAction(url=_trip(SEED_SEARCH_LOCATION)),
        WaitAction(time_seconds=0.85),
        *_type_pickup_for_search(LOC_CORPORATE_TOWER),
    ],
)

SEARCH_DESTINATION = _uc(
    "SEARCH_DESTINATION",
    prompt=("Search destination details for 'Phoenix Liberal Arts School - 6551 Jefferson St, Phoenix, AZ 85021, USA'."),
    actions=[
        NavigateAction(url=_trip(SEED_SEARCH_DESTINATION)),
        WaitAction(time_seconds=0.85),
        *_type_dropoff_for_search(LOC_PHOENIX_LIBERAL_ARTS),
    ],
)

SELECT_DATE = _uc(
    "SELECT_DATE",
    prompt="Select date for your trip that is after '2026-04-06'.",
    actions=[
        NavigateAction(url=_pickupnow(SEED_SELECT_DATE)),
        WaitAction(time_seconds=1.2),
        *_open_pickupnow_date_popover(),
        EvaluateAction(script=PICK_DATE_JS, arg={"year": TODAY.year, "month": TODAY.month, "day": TODAY.day + 1}),
        WaitAction(time_seconds=0.2),
    ],
)

SELECT_TIME = _uc(
    "SELECT_TIME",
    prompt="Select time for my trip at '19:20:00'.",
    actions=[
        NavigateAction(url=_pickupnow(SEED_SELECT_TIME)),
        WaitAction(time_seconds=1.2),
        *_open_time_slot_panel(),
        *_click_time_label_contains("7:20 PM"),
    ],
)

NEXT_PICKUP = _uc(
    "NEXT_PICKUP",
    prompt=("Next pickup, please select a date that is AFTER '2026-04-06' and a time that is NOT '23:10:00'."),
    actions=[
        NavigateAction(url=_pickupnow(SEED_NEXT_PICKUP)),
        WaitAction(time_seconds=1.2),
        *_open_pickupnow_date_popover(),
        EvaluateAction(script=PICK_DATE_JS, arg={"year": TODAY.year, "month": TODAY.month, "day": TODAY.day + 1}),
        *_close_date_popover(),
        *_open_time_slot_panel(),
        *_click_time_label_contains("10:00"),
        *_pickupnow_next_button(),
    ],
)

SEARCH = _uc(
    "SEARCH",
    prompt=(
        "Search ride options where the location is NOT 'Park Resort - 4675 Second St, Washington, DC 20076, USA', "
        "the destination is NOT 'Phoenix Community College - 7346 Lincoln Ave, Phoenix, AZ 85034, USA', "
        "and the scheduled time is less than or equal to '2026-04-03 22:00:00'."
    ),
    actions=[
        NavigateAction(url=_trip(SEED_SEARCH)),
        WaitAction(time_seconds=0.65),
        *_prime_schedule("2026-04-03", "21:30", SEED_SEARCH),
        *_enter_pickup(LOC_1HOTEL),
        *_enter_dropoff(LOC_CORPORATE_TOWER),
        *_click_search(),
    ],
)

SELECT_CAR = _uc(
    "SELECT_CAR",
    prompt=(
        "Select car options for a ride where the location CONTAINS 'Phoenix', the destination is NOT "
        "'Atlanta Medical Hospital - 3188 First Ave, Atlanta, GA 30348, USA', the ride_name does NOT CONTAIN 'pmc', "
        "and the scheduled time is after '2026-04-05 15:30:00'."
    ),
    actions=[
        NavigateAction(url=_trip(SEED_SELECT_CAR)),
        WaitAction(time_seconds=0.65),
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value='//*[@id="layout-main"]/div/div/div[1]/section/div[5]',
            ),
        ),
        ClickAction(
            selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="data-testid", value="date-display"),
        ),
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value="//*[@data-testid='date-picker-input-calendar']//tbody/tr[2]/td[1]/button",
            ),
        ),
        SendKeysIWAAction(keys="Escape"),
        ClickAction(
            selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=PICKUP_CARD_ID),
        ),
        ClickAction(selector=Selector(type=SelectorType.XPATH_SELECTOR, value="//*[@id='slot-picker-div']/span")),
        HoldKeyAction(key="Alt"),
        ClickAction(selector=Selector(type=SelectorType.TAG_CONTAINS_SELECTOR, value="03:30 PM", case_sensitive=True)),
        HoldKeyAction(key="Alt", release=True),
        ClickAction(selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="pickupnow-confirm-button")),
        *_enter_pickup("Phoenix Airport (IAH) - Phoenix, AZ 85023, USA"),
        *_enter_dropoff(LOC_CORPORATE_TOWER),
        *_click_search(),
        *_wait_ride_list(),
        *_click_first_ride_card(),
    ],
)

RESERVE_RIDE = _uc(
    "RESERVE_RIDE",
    prompt=(
        "Reserve ride for a vehicle where the location does NOT contain 'fbs', the destination does NOT equal "
        "'Chase Center - 1 Warriors Way, San Francisco, CA 94158, USA', the ride_name contains 'ed', "
        "and the scheduled time is greater than or equal to '2026-04-08 16:30:00'."
    ),
    actions=[
        NavigateAction(url=_trip(SEED_RESERVE_RIDE)),
        WaitAction(time_seconds=0.65),
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value='//*[@id="layout-main"]/div/div/div[1]/section/div[5]',
            ),
        ),
        ClickAction(
            selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="data-testid", value="date-picker-input-trigger"),
        ),
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value="//*[@data-testid='date-picker-input-calendar']/div/div/table/tbody/tr[2]/td[4]/button",
            ),
        ),
        SendKeysIWAAction(keys="Escape"),
        ClickAction(
            selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="time-select-wrapper"),
        ),
        HoldKeyAction(key="Alt"),
        ClickAction(selector=Selector(type=SelectorType.TAG_CONTAINS_SELECTOR, value="04:30 PM", case_sensitive=True)),
        HoldKeyAction(key="Alt", release=True),
        ClickAction(
            selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="pickupnow-proceed-button"),
        ),
        *_enter_pickup(LOC_1HOTEL),
        *_enter_dropoff(LOC_VAN_NESS),
        *_click_search(),
        *_wait_ride_list(),
        *_click_ride_card_substr("ed"),
        *_click_reserve_ride_bar(),
    ],
)

TRIP_DETAILS = _uc(
    "TRIP_DETAILS",
    prompt=(
        "View trip details for a trip where the location equals 'Lincoln Garden - 7904 Lincoln Ave, Miami, FL 33200, USA', "
        "the destination contains 'S', the ride_name contains 'V 14', and the scheduled time is greater than or equal to "
        "'2026-04-03 14:20:00'."
    ),
    actions=[
        NavigateAction(url=_trip(SEED_TRIP_DETAILS)),
        WaitAction(time_seconds=0.65),
        ClickAction(
            selector=Selector(type=SelectorType.XPATH_SELECTOR, value='//*[@id="layout-main"]/div/div/div[1]/section/div[5]'),
        ),
        ClickAction(
            selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="data-testid", value="date-display"),
        ),
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value="//*[@data-testid='date-picker-input-calendar']/div/div/table/tbody/tr[1]/td[6]",
            ),
        ),
        SendKeysIWAAction(keys="Escape"),
        ClickAction(
            selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="time-picker-div"),
        ),
        HoldKeyAction(key="Alt"),
        ClickAction(selector=Selector(type=SelectorType.TAG_CONTAINS_SELECTOR, value="04:20 PM", case_sensitive=True)),
        HoldKeyAction(key="Alt", release=True),
        ClickAction(selector=Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value="pickupnow-confirm-btn")),
        *_enter_pickup(LOC_LINCOLN_GARDEN_MIAMI),
        *_enter_dropoff(LOC_SFO),
        *_click_search(),
        *_wait_ride_list(),
        *_click_ride_card_substr("V 14"),
        *_click_reserve_ride_bar(),
        NavigateAction(url=_trips(SEED_TRIP_DETAILS)),
        WaitAction(time_seconds=3.0),
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value=(
                    "//div[contains(@class,'text-gray-500') and contains(.,'Lincoln Garden')]/ancestor::div[contains(@class,'rounded-2xl')][1]//button[contains(normalize-space(.),'View Information')]"
                ),
            )
        ),
        WaitAction(time_seconds=0.6),
    ],
)

CANCEL_RESERVATION = _uc(
    "CANCEL_RESERVATION",
    prompt=(
        "Cancel reservation for the trip with ID where the location equals 'Cafe Restaurant - 4629 Maple Dr, Chicago, IL 60608, USA' "
        "and the destination equals 'Cafe Restaurant - 4629 Maple Dr, Chicago, IL 60608, USA' and the ride_name is NOT 'Night 64' "
        "and the scheduled time is AFTER '2026-04-04 15:30:00'."
    ),
    actions=[
        NavigateAction(url=_trip(SEED_CANCEL_RESERVATION)),
        WaitAction(time_seconds=0.65),
        *_prime_schedule("2026-04-05", "11:00", SEED_CANCEL_RESERVATION),
        *_enter_pickup(LOC_CAFE_MAPLE),
        *_enter_dropoff(LOC_CAFE_MAPLE),
        *_click_search(),
        *_click_first_ride_not_named("Night 64"),
        *_click_reserve_ride_bar(),
        NavigateAction(url=_trips(SEED_CANCEL_RESERVATION)),
        WaitAction(time_seconds=3.0),
        ClickAction(
            selector=Selector(
                type=SelectorType.XPATH_SELECTOR,
                value=("//div[contains(.,'Cafe Restaurant - 4629 Maple Dr')]/ancestor::div[contains(@class,'rounded-2xl')][1]//button[contains(normalize-space(.),'Delete')]"),
            )
        ),
        WaitAction(time_seconds=0.6),
    ],
)


def load_autodrive_use_case_completion_flows() -> dict[str, Trajectory]:
    return {
        "ENTER_LOCATION": ENTER_LOCATION,
        "ENTER_DESTINATION": ENTER_DESTINATION,
        "SEARCH_LOCATION": SEARCH_LOCATION,
        "SEARCH_DESTINATION": SEARCH_DESTINATION,
        "SELECT_DATE": SELECT_DATE,
        "SELECT_TIME": SELECT_TIME,
        "NEXT_PICKUP": NEXT_PICKUP,
        "SEARCH": SEARCH,
        "SELECT_CAR": SELECT_CAR,
        "RESERVE_RIDE": RESERVE_RIDE,
        "TRIP_DETAILS": TRIP_DETAILS,
        "CANCEL_RESERVATION": CANCEL_RESERVATION,
    }
