"use client";

import { useSearchParams, useParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { CalendarIcon, ClockIcon, UserIcon } from "lucide-react";
import React, { useEffect, useState } from "react";
import { EVENT_TYPES, logEvent } from "@/library/events";
import dayjs from "dayjs";
import { countries, initializeRestaurants, getRestaurants } from "@/library/dataset";
import { useSeedVariation, getSeedFromUrl } from "@/library/utils";

const photos = [
  "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=150&h=150",
  "https://images.unsplash.com/photo-1600891964599-f61ba0e24092?w=150&h=150",
  "https://images.unsplash.com/photo-1551218808-94e220e084d2?w=150&h=150",
];

type RestaurantView = {
  id: string;
  name: string;
  image: string;
  rating: number;
  reviews: number;
  bookings: number;
  price: string;
  cuisine: string;
  desc: string;
};

export default function Page() {
  const params = useParams();
  const searchParams = useSearchParams();

  const restaurantId = params.restaurantId as string;
  const reservationTimeParam = decodeURIComponent(params.time as string);
  const reservationPeopleParam = searchParams.get("people");
  const reservationDateParam = searchParams.get("date");

  const [selectedCountry, setSelectedCountry] = useState(countries[0]);
  const [date, setDate] = useState<Date | undefined>();
  const [formattedDate, setFormattedDate] = useState<string | null>(null);
  const [fullDate, setFullDate] = useState<string | null>(null);
  const [time, setTime] = useState(reservationTimeParam || "1:00 PM");
  const [people, setPeople] = useState(
    parseInt(reservationPeopleParam || "2", 10)
  );
  const [reservationTime, setReservationTime] = useState<string | null>(null);
  const [reservationPeople, setReservationPeople] = useState<string | null>(
    null
  );
  const [phoneNumber, setPhoneNumber] = useState("");
  const [occasion, setOccasion] = useState("");
  const [specialRequest, setSpecialRequest] = useState("");
  const [showToast, setShowToast] = useState(false);
  const [phoneError, setPhoneError] = useState(false);
  const [email, setEmail] = useState("user_name@gmail.com");

  const [data, setData] = useState<RestaurantView | null>(null);

  const seed = Number(searchParams?.get("seed") ?? "1");

  // Create layout based on seed
  const layout = {
    wrap: seed % 2 === 0, // Even seeds wrap, odd seeds don't
    justify: ["flex-start", "center", "flex-end", "space-between", "space-around"][seed % 5],
    marginTop: [0, 4, 8, 12, 16][seed % 5],
    marginBottom: [0, 4, 8, 12, 16][seed % 5],
    gap: [2, 3, 4, 5, 6][seed % 5],
  };

  // Use seed-based variations
  const formVariation = useSeedVariation("form");
  const bookButtonVariation = useSeedVariation("bookButton");

  const restaurantInfo = {
    restaurantId,
    restaurantName: data?.name ?? "",
    rating: data?.rating ?? 0,
    reviews: data?.reviews ?? 0,
    bookings: data?.bookings ?? 0,
    price: data?.price ?? "",
    cuisine: data?.cuisine ?? "",
    desc: data?.desc ?? "",
  };

  useEffect(() => {
    initializeRestaurants().then(() => {
      const list = getRestaurants();
      const found = list.find((x) => x.id === restaurantId) || list[0];
      if (found) {
        const mapped: RestaurantView = {
          id: found.id,
          name: found.name,
          image: found.image,
          rating: Number(found.stars ?? 4),
          reviews: Number(found.reviews ?? 0),
          bookings: Number(found.bookings ?? 0),
          price: String(found.price ?? "$$"),
          cuisine: String(found.cuisine ?? "International"),
          desc: `Enjoy a delightful experience at ${found.name}, offering a fusion of flavors in the heart of ${found.area ?? "Downtown"}.`,
        };
        setData(mapped);
      }
    });
  }, [restaurantId]);

  useEffect(() => {
    const computedFullDate = reservationDateParam
      ? dayjs(reservationDateParam).format("YYYY-MM-DD")
      : null;
    if (data) {
      logEvent(EVENT_TYPES.BOOK_RESTAURANT, {
        restaurantId,
        restaurantName: data.name,
        rating: data.rating,
        reviews: data.reviews,
        bookings: data.bookings,
        price: data.price,
        cuisine: data.cuisine,
        desc: data.desc,
        date: computedFullDate,
        time: reservationTime || time,
        people: reservationPeople || people,
      });
    }
  }, [data]);

  useEffect(() => {
    if (reservationDateParam) {
      const d = new Date(reservationDateParam);
      setDate(d);
      setFormattedDate(dayjs(d).format("MMM D"));
      setFullDate(dayjs(d).format("YYYY-MM-DD"));
    }
    if (reservationTimeParam) setReservationTime(reservationTimeParam);
    if (reservationPeopleParam) setReservationPeople(reservationPeopleParam);
  }, [reservationDateParam, reservationTimeParam, reservationPeopleParam]);

  const handleReservation = () => {
    if (!phoneNumber.trim()) {
      setPhoneError(true);
      return;
    }
    setPhoneError(false);
    logEvent(EVENT_TYPES.RESERVATION_COMPLETE, {
      ...restaurantInfo,
      date: fullDate,
      time: reservationTime,
      people: reservationPeople,
      countryCode: selectedCountry.code,
      countryName: selectedCountry.name,
      phoneNumber,
      occasion,
      specialRequest,
      email,
    });
    setShowToast(true);
    setTimeout(() => setShowToast(false), 4000);
    setPhoneNumber("");
    setOccasion("");
    setSpecialRequest("");
    setSelectedCountry(countries[0]);
  };

  return (
    <main suppressHydrationWarning>
      <nav className="w-full border-b bg-white sticky top-0 z-10">
        <div className="max-w-6xl mx-auto flex items-center justify-between h-20 px-4 gap-2">
          <div className="flex items-center gap-3">
            <Link href="/">
              <div className="bg-[#46a758] px-3 py-1 rounded flex items-center h-9">
                <span className="font-bold text-white text-lg">AutoDining</span>
              </div>
            </Link>
          </div>
          <div className="flex-1 flex items-center justify-center">
            <input
              type="text"
              placeholder="Location, Restaurant, or Cuisine"
              className="rounded p-2 min-w-[250px] border border-gray-300"
              disabled
            />
            <button className="ml-2 px-4 py-2 rounded bg-[#46a758] text-white">
              Let's go
            </button>
          </div>
          <div className="flex items-center gap-4">
            <Link
              className="text-sm text-gray-600 hover:text-[#46a758]"
              href="/help"
            >
              Get help
            </Link>
            <Link
              className="text-sm text-gray-600 hover:text-[#46a758]"
              href="/faqs"
            >
              FAQs
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto px-4 pb-10 pt-4">
        <h2 className="font-bold text-lg mt-8 mb-4">You’re almost done!</h2>
        <div className="flex items-center gap-3 mb-6">
            <img
            src={data?.image || "/images/restaurant1.jpg"}
            alt={data?.name || "Restaurant"}
            className="w-16 h-16 rounded-lg object-cover border"
          />
          <div className="flex flex-col gap-[2px]">
            <span className="font-bold text-2xl">{data?.name ?? "Loading..."}</span>
            <div className="flex items-center gap-5 text-gray-700 mt-1 text-[15px]">
              <span className="flex items-center gap-1">
                <CalendarIcon className="w-4 h-4 mr-1" />
                {formattedDate ?? "Select Date"}
              </span>
              <span className="flex items-center gap-1">
                <ClockIcon className="w-4 h-4 mr-1" />
                {reservationTime ?? "Select Time"}
              </span>
              <span className="flex items-center gap-1">
                <UserIcon className="w-4 h-4 mr-1" />
                {reservationPeople ?? "Select"} people
              </span>
            </div>
          </div>
        </div>

        <h3 className="font-semibold text-lg mb-2 mt-4">Diner details</h3>
        <div className={formVariation.className} data-testid={formVariation.dataTestId}>
        {layout.wrap ? (
          <div className="w-full" data-testid={`input-wrapper-${seed}`}>
            <div
              className={`flex ${layout.wrap ? "flex-wrap" : ""} gap-${
                layout.gap
              } mb-${layout.marginBottom}`}
            >
              <div className="flex-1 min-w-[220px]">
                <div className="flex items-center space-x-2">
                  <select
                    id="select-country"
                    className="border px-2 py-2 rounded-l bg-white cursor-pointer text-lg"
                    value={selectedCountry.code}
                    onChange={(e) => {
                      const country = countries.find(
                        (c) => c.code === e.target.value
                      )!;
                      setSelectedCountry(country);
                      logEvent(EVENT_TYPES.COUNTRY_SELECTED, {
                        ...restaurantInfo,
                        countryCode: country.code,
                        countryName: country.name,
                        restaurantName: data?.name ?? "",
                      });
                    }}
                  >
                    {countries.map((c) => (
                      <option key={c.code} value={c.code}>
                        {c.flag} {c.dial}
                      </option>
                    ))}
                  </select>
                  <input
                    type="tel"
                    placeholder="Phone number"
                    className="border border-l-0 px-3 py-2 w-full rounded-r focus:outline-none"
                    value={phoneNumber}
                    onChange={(e) => {
                      setPhoneNumber(e.target.value);
                      if (e.target.value.trim()) setPhoneError(false);
                    }}
                  />
                </div>
                {phoneError && (
                  <p className="text-red-500 text-sm mt-1 ml-1">
                    Phone number is required.
                  </p>
                )}
              </div>

              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex-1 border px-3 py-2 rounded min-w-[220px] bg-gray-100 text-gray-800"
                disabled
              />
            </div>
          </div>
        ) : (
          <div
            className={`flex ${layout.wrap ? "flex-wrap" : ""} gap-${
              layout.gap
            } mb-${layout.marginBottom}`}
          >
            <div className="flex-1 min-w-[220px]">
              <div className="flex items-center space-x-2">
                <select
                id="select-country"
                  className="border px-2 py-2 rounded-l bg-white cursor-pointer text-lg"
                  value={selectedCountry.code}
                  onChange={(e) => {
                    const country = countries.find(
                      (c) => c.code === e.target.value
                    )!;
                    setSelectedCountry(country);
                      logEvent(EVENT_TYPES.COUNTRY_SELECTED, {
                      ...restaurantInfo,
                      countryCode: country.code,
                      countryName: country.name,
                        restaurantName: data?.name ?? "",
                    });
                  }}
                >
                  {countries.map((c) => (
                    <option key={c.code} value={c.code}>
                      {c.flag} {c.dial}
                    </option>
                  ))}
                </select>
                <input
                  type="tel"
                  placeholder="Phone number"
                  className="border border-l-0 px-3 py-2 w-full rounded-r focus:outline-none"
                  value={phoneNumber}
                  onChange={(e) => {
                    setPhoneNumber(e.target.value);
                    if (e.target.value.trim()) setPhoneError(false);
                  }}
                />
              </div>
              {phoneError && (
                <p className="text-red-500 text-sm mt-1 ml-1">
                  Phone number is required.
                </p>
              )}
            </div>

            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1 border px-3 py-2 rounded min-w-[220px] bg-gray-100 text-gray-800"
              disabled
            />
          </div>
        )}

        {layout.wrap ? (
          <div className="w-full" data-testid={`occasion-wrapper-${seed}`}>
            <div
              className={`flex ${layout.wrap ? "flex-wrap" : ""} gap-${
                layout.gap
              } mb-${layout.marginBottom}`}
            >
              <select
                id = "select-occasion"
                className="flex-1 border rounded px-3 py-2 bg-white min-w-[220px]"
                value={occasion}
                onChange={(e) => {
                  setOccasion(e.target.value);
                  logEvent(EVENT_TYPES.OCCASION_SELECTED, {
                    ...restaurantInfo,
                    occasion: e.target.value,
                  });
                }}
              >
                <option value="">Select an occasion (optional)</option>
                <option value="birthday">Birthday</option>
                <option value="anniversary">Anniversary</option>
                <option value="business">Business meal</option>
                <option value="other">Other</option>
              </select>
              <input
                type="text"
                placeholder="Add a special request (optional)"
                className="flex-1 border px-3 py-2 rounded min-w-[220px]"
                value={specialRequest}
                onChange={(e) => setSpecialRequest(e.target.value)}
              />
            </div>
          </div>
        ) : (
          <div
            className={`flex ${layout.wrap ? "flex-wrap" : ""} gap-${
              layout.gap
            } mb-${layout.marginBottom}`}
          >
            <select
            id="select-occasion"
              className="flex-1 border rounded px-3 py-2 bg-white min-w-[220px]"
              value={occasion}
              onChange={(e) => {
                setOccasion(e.target.value);
                logEvent(EVENT_TYPES.OCCASION_SELECTED, {
                  ...restaurantInfo,
                  occasion: e.target.value,
                });
              }}
            >
              <option value="">Select an occasion (optional)</option>
              <option value="birthday">Birthday</option>
              <option value="anniversary">Anniversary</option>
              <option value="business">Business meal</option>
              <option value="other">Other</option>
            </select>
            <input
              type="text"
              placeholder="Add a special request (optional)"
              className="flex-1 border px-3 py-2 rounded min-w-[220px]"
              value={specialRequest}
              onChange={(e) => setSpecialRequest(e.target.value)}
            />
          </div>
        )}
        </div>

        {layout.wrap ? (
          <div
            className="w-full"
            data-testid={`complete-reservation-wrapper-${seed}`}
          >
            <Button
              onClick={handleReservation}
              className={`w-full ${bookButtonVariation.className} py-6 text-lg rounded mt-${layout.marginTop} mb-${layout.marginBottom}`}
              data-testid={bookButtonVariation.dataTestId}
            >
              Complete reservation
            </Button>
          </div>
        ) : (
          <Button
            onClick={handleReservation}
            className={`w-full ${bookButtonVariation.className} py-6 text-lg rounded mt-${layout.marginTop} mb-${layout.marginBottom}`}
            data-testid={bookButtonVariation.dataTestId}
          >
            Complete reservation
          </Button>
        )}

        <div className="text-xs text-gray-600 mt-3">
          By clicking “Complete reservation” you agree to the{" "}
          <Link href="#" className="text-[#46a758] underline">
            OpenDinning Terms of Use
          </Link>{" "}
          and{" "}
          <Link href="#" className="text-[#46a758] underline">
            Privacy Policy
          </Link>
          . Message &amp; data rates may apply. You can opt out of receiving
          text messages at any time in your account settings or by replying
          STOP.
        </div>
      </div>

      {showToast && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 bg-green-600 text-white px-20 py-5 rounded shadow-lg z-50">
          Reservation completed successfully!
        </div>
      )}
    </main>
  );
}
