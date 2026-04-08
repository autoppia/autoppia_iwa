"""
Golden trajectories for Autoppia Lodge (``autolodge``, web_8).

Per-use-case ``prompt`` and ``tests`` are static literals below (no JSON load).
Seeds match ``autolodge_tasks.json`` in this package (``?seed=`` on ``http://localhost:8007``).

Base URL: ``http://localhost:8007``.
"""

from __future__ import annotations

PROJECT_NUMBER = 8
WEB_PROJECT_ID = "autolodge"

from autoppia_iwa.src.data_generation.tests.classes import BaseTaskTest
from autoppia_iwa.src.demo_webs.classes import Trajectory
from autoppia_iwa.src.execution.actions import (
    ClickAction,
    EvaluateAction,
    NavigateAction,
    SelectDropDownOptionAction,
    SendKeysIWAAction,
    TypeAction,
    WaitAction,
)
from autoppia_iwa.src.execution.actions.base import BaseAction, Selector, SelectorType

BASE = "http://localhost:8007"

# Seeds from autolodge_tasks.json (canonical order)
SEED_SEARCH_HOTEL = 230
SEED_VIEW_HOTEL = 897
SEED_EDIT_NUMBER_OF_GUESTS = 154
SEED_RESERVE_HOTEL = 543
SEED_EDIT_CHECK_IN_OUT_DATES = 714
SEED_CONFIRM_AND_PAY = 115
SEED_MESSAGE_HOST = 110
SEED_SHARE_HOTEL = 314
SEED_ADD_TO_WISHLIST = 634
SEED_REMOVE_FROM_WISHLIST = 698
SEED_BACK_TO_ALL_HOTELS = 574
SEED_SUBMIT_REVIEW = 229
SEED_APPLY_FILTERS = 913
SEED_PAYMENT_METHOD_SELECTED = 733
SEED_WISHLIST_OPENED = 772
SEED_BOOK_FROM_WISHLIST = 468
SEED_POPULAR_HOTELS_VIEWED = 672
SEED_HELP_VIEWED = 306
SEED_FAQ_OPENED = 234

# Static hotel IDs aligned with prompts / CheckEventTest criteria (see web_8 ``hotels.json``)
HID_VIEW = 56
HID_EDIT_GUESTS = 50
HID_RESERVE = 59
HID_EDIT_DATES = 179
HID_CONFIRM = 54
HID_MESSAGE = 134
HID_SHARE = 36
HID_ADD_WL = 3
HID_REMOVE_WL = 200
HID_BACK = 39
HID_REVIEW = 91
HID_PAYMENT = 59
HID_BOOK_WL = 18

_MESSAGE_TEXT = "Is there parking available nearby?"
_SHARE_EMAIL = "friend@example.com"
_REVIEW_COMMENT = "Great stay"


_EDIT_STAY_CALENDAR_JS = """async () => {
  const root = document.getElementById('dateRangeCalendar');
  if (!root) return false;
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const monthBlocks = () => {
    const multi = [...root.querySelectorAll('.rdp-caption_start, .rdp-caption_end')];
    return multi.length ? multi : [root];
  };
  const captionOf = (block) => {
    const lab = block.querySelector('.rdp-caption_label') || block.querySelector('[aria-live="polite"]');
    return lab?.textContent?.trim() || '';
  };
  const hasVisibleMonth = (mon, yr) =>
    monthBlocks().some((b) => {
      const t = captionOf(b);
      return t.includes(mon) && t.includes(yr);
    });
  const prevMonth = async () => {
    const btn = root.querySelector('button[name="previous-month"]');
    if (btn && !btn.disabled) btn.click();
    await sleep(150);
  };
  const nextMonth = async () => {
    const btn = root.querySelector('button[name="next-month"]');
    if (btn && !btn.disabled) btn.click();
    await sleep(150);
  };
  for (let i = 0; i < 28; i++) {
    if (hasVisibleMonth('July', '2025')) break;
    await prevMonth();
  }
  const pickDayInMonth = (n, mon, yr) => {
    for (const block of monthBlocks()) {
      const t = captionOf(block);
      if (!t.includes(mon) || !t.includes(yr)) continue;
      const grid = block.querySelector('table[role="grid"]') || block;
      for (const b of grid.querySelectorAll('button[name="day"]')) {
        if (b.textContent?.trim() !== String(n)) continue;
        if (b.disabled) continue;
        if (b.className.includes('day-outside') || b.className.includes('day_outside')) continue;
        b.click();
        return true;
      }
    }
    return false;
  };
  pickDayInMonth(20, 'July', '2025');
  await sleep(200);
  for (let i = 0; i < 28; i++) {
    if (hasVisibleMonth('December', '2025')) break;
    await nextMonth();
  }
  pickDayInMonth(31, 'December', '2025');
  await sleep(200);
  return true;
}"""

_PROMPTS: dict[str, str] = {
    "SEARCH_HOTEL": "Search for hotels where the search term equals 'Bali, Indonesia'",
    "VIEW_HOTEL": "Show details for a hotel where the title does NOT contain 'unh', the number of reviews equals '2200', the rating is less than '5.92', and the amenities include 'Pool access'.",
    "EDIT_NUMBER_OF_GUESTS": "Set the number of guests to 2 where guests_to equals '2', rating is "
    "greater equal '4.8', host_name equals 'Steven', title contains 'rce', "
    "price is less than '703', amenities not contains 'hif', reviews equals "
    "'4800', and location not equals 'Singapore, Singapore'.",
    "RESERVE_HOTEL": "Reserve the hotel for a stay with guests greater equal '1' at a location that "
    "contains 'arsaw, Polan' AND rating equals '4.7' AND reviews greater than '2098' "
    "AND host_name not contains 'koq' AND amenities is not one of ['Washer & dryer', "
    "'Climate control', 'Scenic views']",
    "EDIT_CHECK_IN_OUT_DATES": "Edit checkin checkout dates where checkin date greater than "
    "'2025-06-19 00:00:00', and checkout date equals '2025-12-31 "
    "00:00:00', and guests_set equals '1', and reviews equals '3100', and "
    "price equals '750', and title contains 'z-Carlton Residences Moscow', "
    "and rating equals '4.8', and location not equals 'Portofino, Italy', "
    "and host_name not equals 'Kevin'",
    "CONFIRM_AND_PAY": "Please confirm the booking details for a stay where guests_set equals '2' AND "
    "host_name not contains 'znf' AND location not equals 'Bali, Indonesia' AND "
    "title not contains 'rjk' AND amenities is one of ['Washer & dryer', "
    "'Fireplace'] AND price equals '500' AND card_number not equals "
    "'4111111111111111' AND expiration not equals '01/27' AND cvv equals '456' AND "
    "zipcode equals '54321' AND country not equals 'Canada'",
    "MESSAGE_HOST": "Message the host where message equals 'Is there parking available nearby?' AND "
    "host_name contains 'Al' AND guests NOT equals '1' AND amenities contains 'Gym "
    "access' AND host_name not contains 'yjd' AND title contains 'ton Marrak' AND "
    "rating less equal '4.8' AND reviews less equal '3100' AND price equals '600'",
    "SHARE_HOTEL": "Share the hotel listing with someone whose email is NOT "
    "'ava.wilson@healthcare.org', ensuring that the amenities do NOT contain 'Pool "
    "access', the rating is GREATER THAN OR EQUAL TO 4.8, the number of guests is LESS "
    "THAN 3, and the location is 'Palm Beach, United States'.",
    "ADD_TO_WISHLIST": "Add to wishlist a hotel with a price of 270 or less, for more than 1 guest, "
    "with reviews of 185 or less, whose title contains 'oastal Breeze', where the "
    "host_name does NOT contain 'sfm', with a rating of less than 6.12, and where "
    "the location does NOT contain 'jfj', and the amenities do NOT contain "
    "'Breakfast included'.",
    "REMOVE_FROM_WISHLIST": "Remove the hotel from my wishlist where the amenities is one of ['Great "
    "location', 'Balcony views'] AND the host_name equals 'Victoria' AND the "
    "title not equals 'Burj Al Arab Jumeirah' AND the price equals '750' AND "
    "the rating equals '4.8'.",
    "BACK_TO_ALL_HOTELS": "Go back to all hotels where the number of guests_set is LESS than 2, the "
    "number of reviews is LESS than 6402, the amenities are NOT one of "
    "['Climate control', 'Pet friendly', 'Great location'], the title is NOT "
    "'The Ritz-Carlton Copenhagen', the location does NOT contain 'ykm', the "
    "rating equals '4.9', and the host_name contains 'atali'.",
    "SUBMIT_REVIEW": "Submit a review saying 'Great stay' with a rating greater equal 3, where the "
    "host_name contains 'Steve', guests are greater equal 1, title is NOT 'The "
    "Ritz-Carlton Residences Barcelona', amenities contains 'Hot tub', location is "
    "NOT 'Rome, Italy', price is greater equal 850, reviews are greater than 5098, "
    "and rating is greater equal 3.",
    "APPLY_FILTERS": "Show details for hotels with a rating of 4.5 or less that are NOT located in 'Indonesia'",
    "PAYMENT_METHOD_SELECTED": "Select 'card' as the payment method for the booking with hotel_id greater than '14' and where the title is NOT 'Mount'.",
    "WISHLIST_OPENED": "Open my wishlist to view saved hotels.",
    "BOOK_FROM_WISHLIST": "Please book the hotel with hotel_id less equal '182' and title that does NOT contain 'The R' from my wishlist.",
    "POPULAR_HOTELS_VIEWED": "Show me popular hotels where the rating is greater than or equal to '4.5'",
    "HELP_VIEWED": "Open the help page for 'HELP_VIEWED' questions.",
    "FAQ_OPENED": "Open the FAQ item where the question is NOT 'How do'",
}

_RAW_TESTS: dict[str, list[dict]] = {
    "SEARCH_HOTEL": [{"type": "CheckEventTest", "event_name": "SEARCH_HOTEL", "event_criteria": {"search_term": "Bali, Indonesia"}, "description": "Check if specific event was triggered"}],
    "VIEW_HOTEL": [
        {
            "type": "CheckEventTest",
            "event_name": "VIEW_HOTEL",
            "event_criteria": {
                "title": {"operator": "not_contains", "value": "unh"},
                "reviews": 2200,
                "rating": {"operator": "less_than", "value": 5.92},
                "amenities": {"operator": "contains", "value": "Pool access"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "EDIT_NUMBER_OF_GUESTS": [
        {
            "type": "CheckEventTest",
            "event_name": "EDIT_NUMBER_OF_GUESTS",
            "event_criteria": {
                "guests_to": 2,
                "rating": {"operator": "greater_equal", "value": 4.8},
                "host_name": "Steven",
                "title": {"operator": "contains", "value": "rce"},
                "price": {"operator": "less_than", "value": 703},
                "amenities": {"operator": "not_contains", "value": "hif"},
                "reviews": 4800,
                "location": {"operator": "not_equals", "value": "Singapore, Singapore"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "RESERVE_HOTEL": [
        {
            "type": "CheckEventTest",
            "event_name": "RESERVE_HOTEL",
            "event_criteria": {
                "guests_set": {"operator": "greater_equal", "value": 1},
                "location": {"operator": "contains", "value": "arsaw, Polan"},
                "rating": 4.7,
                "reviews": {"operator": "greater_than", "value": 2098},
                "host_name": {"operator": "not_contains", "value": "koq"},
                "amenities": {"operator": "not_in_list", "value": ["Washer & dryer", "Climate control", "Scenic views"]},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "EDIT_CHECK_IN_OUT_DATES": [
        {
            "type": "CheckEventTest",
            "event_name": "EDIT_CHECK_IN_OUT_DATES",
            "event_criteria": {
                "checkin": {"operator": "greater_than", "value": "2025-06-19 00:00:00"},
                "checkout": "2025-12-31 00:00:00",
                "guests_set": 1,
                "reviews": 3100,
                "price": 750,
                "title": {"operator": "contains", "value": "z-Carlton Residences Moscow"},
                "rating": 4.8,
                "location": {"operator": "not_equals", "value": "Portofino, Italy"},
                "host_name": {"operator": "not_equals", "value": "Kevin"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "CONFIRM_AND_PAY": [
        {
            "type": "CheckEventTest",
            "event_name": "CONFIRM_AND_PAY",
            "event_criteria": {
                "guests_set": 2,
                "host_name": {"operator": "not_contains", "value": "znf"},
                "location": {"operator": "not_equals", "value": "Bali, Indonesia"},
                "title": {"operator": "not_contains", "value": "rjk"},
                "amenities": {"operator": "in_list", "value": ["Washer & dryer", "Fireplace"]},
                "price": 500,
                "card_number": {"operator": "not_equals", "value": "4111111111111111"},
                "expiration": {"operator": "not_equals", "value": "01/27"},
                "cvv": "456",
                "zipcode": "54321",
                "country": {"operator": "not_equals", "value": "Canada"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "MESSAGE_HOST": [
        {
            "type": "CheckEventTest",
            "event_name": "MESSAGE_HOST",
            "event_criteria": {
                "message": "Is there parking available nearby?",
                "host_name": {"operator": "not_contains", "value": "yjd"},
                "guests": {"operator": "not_equals", "value": 1},
                "amenities": {"operator": "contains", "value": "Gym access"},
                "title": {"operator": "contains", "value": "ton Marrak"},
                "rating": {"operator": "less_equal", "value": 4.8},
                "reviews": {"operator": "less_equal", "value": 3100},
                "price": 600,
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "SHARE_HOTEL": [
        {
            "type": "CheckEventTest",
            "event_name": "SHARE_HOTEL",
            "event_criteria": {
                "email": {"operator": "not_equals", "value": "ava.wilson@healthcare.org"},
                "amenities": {"operator": "not_contains", "value": "Pool access"},
                "rating": {"operator": "greater_equal", "value": 4.8},
                "guests": {"operator": "less_than", "value": 3},
                "location": "Palm Beach, United States",
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "ADD_TO_WISHLIST": [
        {
            "type": "CheckEventTest",
            "event_name": "ADD_TO_WISHLIST",
            "event_criteria": {
                "price": {"operator": "less_equal", "value": 270},
                "guests": {"operator": "greater_than", "value": 1},
                "reviews": {"operator": "less_equal", "value": 185},
                "title": {"operator": "contains", "value": "oastal Breeze "},
                "host_name": {"operator": "not_contains", "value": "sfm"},
                "rating": {"operator": "less_than", "value": 6.12},
                "location": {"operator": "not_contains", "value": "jfj"},
                "amenities": {"operator": "not_contains", "value": "Breakfast included"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "REMOVE_FROM_WISHLIST": [
        {
            "type": "CheckEventTest",
            "event_name": "REMOVE_FROM_WISHLIST",
            "event_criteria": {
                "amenities": {"operator": "in_list", "value": ["Great location", "Balcony views"]},
                "host_name": "Victoria",
                "title": {"operator": "not_equals", "value": "Burj Al Arab Jumeirah"},
                "price": 750,
                "rating": 4.8,
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "BACK_TO_ALL_HOTELS": [
        {
            "type": "CheckEventTest",
            "event_name": "BACK_TO_ALL_HOTELS",
            "event_criteria": {
                "guests_set": {"operator": "less_than", "value": 2},
                "reviews": {"operator": "less_than", "value": 6402},
                "amenities": {"operator": "not_in_list", "value": ["Climate control", "Pet friendly", "Great location"]},
                "title": {"operator": "not_equals", "value": "The Ritz-Carlton Copenhagen"},
                "location": {"operator": "not_contains", "value": "ykm"},
                "rating": 4.9,
                "host_name": {"operator": "contains", "value": "atali"},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "SUBMIT_REVIEW": [
        {
            "type": "CheckEventTest",
            "event_name": "SUBMIT_REVIEW",
            "event_criteria": {
                "host_name": {"operator": "contains", "value": "Steve"},
                "guests": {"operator": "greater_equal", "value": 1},
                "title": {"operator": "not_equals", "value": "The Ritz-Carlton Residences Barcelona"},
                "amenities": {"operator": "contains", "value": "Hot tub"},
                "location": {"operator": "not_equals", "value": "Rome, Italy"},
                "price": {"operator": "greater_equal", "value": 850},
                "reviews": {"operator": "greater_than", "value": 5098},
                "rating": {"operator": "greater_equal", "value": 3},
            },
            "description": "Check if specific event was triggered",
        }
    ],
    "APPLY_FILTERS": [
        {
            "type": "CheckEventTest",
            "event_name": "APPLY_FILTERS",
            "event_criteria": {"rating": {"operator": "less_equal", "value": 4.5}, "region": {"operator": "not_equals", "value": "Indonesia"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "PAYMENT_METHOD_SELECTED": [
        {
            "type": "CheckEventTest",
            "event_name": "PAYMENT_METHOD_SELECTED",
            "event_criteria": {"method": "card", "hotel_id": {"operator": "greater_than", "value": 14}, "title": {"operator": "not_equals", "value": "Mount"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "WISHLIST_OPENED": [{"type": "CheckEventTest", "event_name": "WISHLIST_OPENED", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "BOOK_FROM_WISHLIST": [
        {
            "type": "CheckEventTest",
            "event_name": "BOOK_FROM_WISHLIST",
            "event_criteria": {"title": {"operator": "not_contains", "value": "The R"}},
            "description": "Check if specific event was triggered",
        }
    ],
    "POPULAR_HOTELS_VIEWED": [{"type": "CheckEventTest", "event_name": "POPULAR_HOTELS_VIEWED", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "HELP_VIEWED": [{"type": "CheckEventTest", "event_name": "HELP_VIEWED", "event_criteria": {}, "description": "Check if specific event was triggered"}],
    "FAQ_OPENED": [
        {"type": "CheckEventTest", "event_name": "FAQ_OPENED", "event_criteria": {"question": {"operator": "not_equals", "value": "How do"}}, "description": "Check if specific event was triggered"}
    ],
}

_TESTS: dict[str, list[BaseTaskTest]] = {uc: [BaseTaskTest.deserialize(p) for p in pl] for uc, pl in _RAW_TESTS.items()}


def _xp(expr: str) -> Selector:
    return Selector(type=SelectorType.XPATH_SELECTOR, value=expr)


def _id(element_id: str) -> Selector:
    return Selector(type=SelectorType.ATTRIBUTE_VALUE_SELECTOR, attribute="id", value=element_id)


def _home(seed: int) -> str:
    return f"{BASE}/?seed={seed}"


def _stay(hid: int, seed: int, extra: str = "") -> str:
    q = f"?seed={seed}" + (f"&{extra}" if extra else "")
    return f"{BASE}/stay/{hid}{q}"


def _confirm(hid: int, seed: int, extra: str = "") -> str:
    q = f"?seed={seed}" + (f"&{extra}" if extra else "")
    return f"{BASE}/stay/{hid}/confirm{q}"


def _uc(use_case: str, actions: list[BaseAction]) -> Trajectory:
    return Trajectory(
        name=use_case,
        prompt=_PROMPTS[use_case],
        actions=actions,
        tests=_TESTS[use_case],
    )


SEARCH_HOTEL = _uc(
    "SEARCH_HOTEL",
    [
        NavigateAction(url=_home(SEED_SEARCH_HOTEL)),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("find-movie")),
        WaitAction(time_seconds=0.2),
        TypeAction(selector=_id("destination-input"), text="Bali, Indonesia"),
        SendKeysIWAAction(keys="Enter"),
        ClickAction(selector=_id("find-button")),
    ],
)

VIEW_HOTEL = _uc(
    "VIEW_HOTEL",
    [
        NavigateAction(url=_stay(HID_VIEW, SEED_VIEW_HOTEL)),
        WaitAction(time_seconds=0.6),
    ],
)

EDIT_NUMBER_OF_GUESTS = _uc(
    "EDIT_NUMBER_OF_GUESTS",
    [
        NavigateAction(url=_stay(HID_EDIT_GUESTS, SEED_EDIT_NUMBER_OF_GUESTS)),
        WaitAction(time_seconds=0.6),
        ClickAction(selector=_xp('*[@id="people-count" or @id="guests-count"]')),
        SendKeysIWAAction(keys="Backspace"),
        TypeAction(selector=_xp('*[@id="people-count" or @id="guests-count"]'), text="12"),
        WaitAction(time_seconds=0.7),
    ],
)

RESERVE_HOTEL = _uc(
    "RESERVE_HOTEL",
    [
        NavigateAction(url=_stay(HID_RESERVE, SEED_RESERVE_HOTEL)),
        WaitAction(time_seconds=0.4),
        ClickAction(selector=_id("book-button")),
        WaitAction(time_seconds=0.6),
    ],
)

EDIT_CHECK_IN_OUT_DATES = _uc(
    "EDIT_CHECK_IN_OUT_DATES",
    [
        NavigateAction(url=_confirm(HID_EDIT_DATES, SEED_EDIT_CHECK_IN_OUT_DATES, "guests=1")),
        WaitAction(time_seconds=1.0),
        ClickAction(selector=_id("dates-edit")),
        WaitAction(time_seconds=0.4),
        EvaluateAction(script=_EDIT_STAY_CALENDAR_JS),
        WaitAction(time_seconds=2),
    ],
)

CONFIRM_AND_PAY = _uc(
    "CONFIRM_AND_PAY",
    [
        NavigateAction(url=_confirm(HID_CONFIRM, SEED_CONFIRM_AND_PAY, "guests=2")),
        WaitAction(time_seconds=1.0),
        TypeAction(selector=_id("payment-number"), text="4242424242424242"),
        TypeAction(selector=_id("card-exp"), text="12 / 28"),
        TypeAction(selector=_id("cvv-input"), text="456"),
        TypeAction(selector=_id("zip-code-input"), text="54321"),
        SelectDropDownOptionAction(selector=_id("region-select"), text="United States"),
        ClickAction(selector=_id("pay-confirm")),
        WaitAction(time_seconds=0.5),
    ],
)

MESSAGE_HOST = _uc(
    "MESSAGE_HOST",
    [
        NavigateAction(url=_confirm(HID_MESSAGE, SEED_MESSAGE_HOST, "guests=2")),
        WaitAction(time_seconds=1.0),
        TypeAction(selector=_id("contact-host"), text=_MESSAGE_TEXT),
        ClickAction(selector=_id("host-message-button")),
        WaitAction(time_seconds=0.5),
    ],
)

SHARE_HOTEL = _uc(
    "SHARE_HOTEL",
    [
        NavigateAction(url=_stay(HID_SHARE, SEED_SHARE_HOTEL)),
        WaitAction(time_seconds=0.7),
        ClickAction(selector=_id("share-listing")),
        WaitAction(time_seconds=0.2),
        TypeAction(
            selector=_xp("html/body/main/div/div/div[1]/div/input"),
            text="friend@example.com",
        ),
        ClickAction(selector=_id("share-confirm")),
        WaitAction(time_seconds=0.5),
    ],
)

ADD_TO_WISHLIST = _uc(
    "ADD_TO_WISHLIST",
    [
        NavigateAction(url=_stay(HID_ADD_WL, SEED_ADD_TO_WISHLIST)),
        WaitAction(time_seconds=0.7),
        ClickAction(selector=_xp("html/body/main/div/span[1]/div/div[1]/div[2]/button[1]")),
    ],
)

REMOVE_FROM_WISHLIST = _uc(
    "REMOVE_FROM_WISHLIST",
    [
        NavigateAction(url=_stay(HID_REMOVE_WL, SEED_REMOVE_FROM_WISHLIST)),
        WaitAction(time_seconds=0.5),
        ClickAction(selector=_xp("//html/body/main/div/span/div/div[1]/div[2]/button[1]")),
        WaitAction(time_seconds=0.3),
        ClickAction(selector=_xp("//html/body/main/div/span/div/div[1]/div[2]/button[1]")),
        WaitAction(time_seconds=0.3),
    ],
)

BACK_TO_ALL_HOTELS = _uc(
    "BACK_TO_ALL_HOTELS",
    [
        NavigateAction(url=_confirm(HID_BACK, SEED_BACK_TO_ALL_HOTELS, "guests=1")),
        WaitAction(time_seconds=0.9),
        ClickAction(
            selector=_xp('//button[contains(., "Back to all hotels") or contains(., "Back to stays") or contains(., "Return to listings")]'),
        ),
    ],
)

SUBMIT_REVIEW = _uc(
    "SUBMIT_REVIEW",
    [
        NavigateAction(url=_stay(HID_REVIEW, SEED_SUBMIT_REVIEW)),
        WaitAction(time_seconds=0.7),
        TypeAction(
            selector=_xp('//form[.//button[contains(.,"Submit review") or contains(.,"Send review")]]//textarea'),
            text=_REVIEW_COMMENT,
        ),
        SelectDropDownOptionAction(
            selector=_xp('//form[.//button[contains(.,"Submit review") or contains(.,"Send review")]]//select'),
            text="3 ★",
        ),
        ClickAction(selector=_xp('//form[.//button[contains(.,"Submit review") or contains(.,"Send review")]]//button[@type="submit"]')),
    ],
)

APPLY_FILTERS = _uc(
    "APPLY_FILTERS",
    [
        NavigateAction(url=_home(SEED_APPLY_FILTERS)),
        WaitAction(time_seconds=0.5),
        SelectDropDownOptionAction(selector=_xp('//*[@id="score-filter" or contains(@id,"rating_filter")]'), text="4.5+"),
        SelectDropDownOptionAction(selector=_xp('//*[@id="region-select" or contains(@id,"region_filter")]'), text="United States"),
        ClickAction(selector=_xp('//button[contains(., "Go") or contains(., "apply_filters")]')),
        WaitAction(time_seconds=0.5),
    ],
)

PAYMENT_METHOD_SELECTED = _uc(
    "PAYMENT_METHOD_SELECTED",
    [
        NavigateAction(url=_confirm(HID_PAYMENT, SEED_PAYMENT_METHOD_SELECTED, "guests=1")),
        WaitAction(time_seconds=1.0),
        ClickAction(selector=_xp('//label[.//span[contains(.,"cash") or contains(.,"Cash") or contains(.,"arrival")]]//input[@type="radio"]')),
        WaitAction(time_seconds=0.15),
        ClickAction(selector=_xp('//label[.//span[contains(.,"card") or contains(.,"Card") or contains(.,"debit")]]//input[@type="radio"]')),
    ],
)

WISHLIST_OPENED = _uc(
    "WISHLIST_OPENED",
    [
        NavigateAction(url=f"{BASE}/?seed={SEED_WISHLIST_OPENED}"),
        ClickAction(selector=_id("wishlist-link")),
        WaitAction(time_seconds=0.6),
    ],
)

BOOK_FROM_WISHLIST = _uc(
    "BOOK_FROM_WISHLIST",
    [
        NavigateAction(url=_stay(HID_BOOK_WL, SEED_BOOK_FROM_WISHLIST)),
        WaitAction(time_seconds=0.6),
        ClickAction(selector=_xp("//html/body/main/div/div/div[1]/div[2]/button[1]")),
        WaitAction(time_seconds=0.4),
        NavigateAction(url=f"{BASE}/wishlist?seed={SEED_BOOK_FROM_WISHLIST}"),
        WaitAction(time_seconds=0.6),
        ClickAction(selector=_id("reserve-stay")),
        WaitAction(time_seconds=0.6),
    ],
)

POPULAR_HOTELS_VIEWED = _uc(
    "POPULAR_HOTELS_VIEWED",
    [
        NavigateAction(url=f"{BASE}/?seed={SEED_POPULAR_HOTELS_VIEWED}"),
        ClickAction(selector=_id("nav-popular")),
        WaitAction(time_seconds=0.6),
    ],
)

HELP_VIEWED = _uc(
    "HELP_VIEWED",
    [
        NavigateAction(url=f"{BASE}/?seed={SEED_HELP_VIEWED}"),
        ClickAction(selector=_id("help-link")),
        WaitAction(time_seconds=0.5),
    ],
)

FAQ_OPENED = _uc(
    "FAQ_OPENED",
    [
        NavigateAction(url=f"{BASE}/help?seed={SEED_FAQ_OPENED}"),
        WaitAction(time_seconds=0.4),
        ClickAction(
            selector=_xp('//button[contains(., "payment options") or contains(., "Payment options")]'),
        ),
    ],
)


def load_autolodge_use_case_completion_flows() -> dict[str, Trajectory]:
    return {
        "SEARCH_HOTEL": SEARCH_HOTEL,
        "VIEW_HOTEL": VIEW_HOTEL,
        "EDIT_NUMBER_OF_GUESTS": EDIT_NUMBER_OF_GUESTS,
        "RESERVE_HOTEL": RESERVE_HOTEL,
        "EDIT_CHECK_IN_OUT_DATES": EDIT_CHECK_IN_OUT_DATES,
        "CONFIRM_AND_PAY": CONFIRM_AND_PAY,
        "MESSAGE_HOST": MESSAGE_HOST,
        "SHARE_HOTEL": SHARE_HOTEL,
        "ADD_TO_WISHLIST": ADD_TO_WISHLIST,
        "REMOVE_FROM_WISHLIST": REMOVE_FROM_WISHLIST,
        "BACK_TO_ALL_HOTELS": BACK_TO_ALL_HOTELS,
        "SUBMIT_REVIEW": SUBMIT_REVIEW,
        "APPLY_FILTERS": APPLY_FILTERS,
        "PAYMENT_METHOD_SELECTED": PAYMENT_METHOD_SELECTED,
        "WISHLIST_OPENED": WISHLIST_OPENED,
        "BOOK_FROM_WISHLIST": BOOK_FROM_WISHLIST,
        "POPULAR_HOTELS_VIEWED": POPULAR_HOTELS_VIEWED,
        "HELP_VIEWED": HELP_VIEWED,
        "FAQ_OPENED": FAQ_OPENED,
    }
