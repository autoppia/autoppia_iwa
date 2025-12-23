"use client";

import { useSearchParams, useParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { CalendarIcon, ClockIcon, UserIcon } from "lucide-react";
import React, { useEffect, useMemo, useState } from "react";
import { EVENT_TYPES, logEvent } from "@/library/events";
import dayjs from "dayjs";
import { countries } from "@/library/dataset";
import { initializeRestaurants, getRestaurants } from "@/dynamic/v2-data";
import { useDynamicSystem } from "@/dynamic/shared";
import { ID_VARIANTS_MAP, CLASS_VARIANTS_MAP, TEXT_VARIANTS_MAP } from "@/dynamic/v3";
import { SeedLink } from "@/components/ui/SeedLink";
import { useSeed } from "@/context/SeedContext";
import Navbar from "@/components/Navbar";
import Image from "next/image";

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
  const { seed: baseSeed, resolvedSeeds } = useSeed();
  const v2Seed = resolvedSeeds.v2 ?? resolvedSeeds.base;

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
  const [name, setName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [occasion, setOccasion] = useState("");
  const [specialRequest, setSpecialRequest] = useState("");
  const [showToast, setShowToast] = useState(false);
  const [phoneError, setPhoneError] = useState(false);
  const [email, setEmail] = useState("user_name@gmail.com");
  const dyn = useDynamicSystem();

  const [data, setData] = useState<RestaurantView | null>(null);

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
    initializeRestaurants(v2Seed ?? undefined).then(() => {
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
          desc: `Enjoy a delightful experience at ${
            found.name
          }, offering a fusion of flavors in the heart of ${
            found.area ?? "Downtown"
          }.`,
        };
        setData(mapped);
      }
    });
  }, [restaurantId, v2Seed]);

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
      name,
      phoneNumber,
      occasion,
      specialRequest,
      email,
    });
    setShowToast(true);
    setTimeout(() => setShowToast(false), 4000);
    setName("");
    setPhoneNumber("");
    setOccasion("");
    setSpecialRequest("");
    setSelectedCountry(countries[0]);
  };

  return (
    dyn.v1.addWrapDecoy("booking-page", (
      <main suppressHydrationWarning id={dyn.v3.getVariant("booking-page", ID_VARIANTS_MAP, "booking-page")}>
        <Navbar />

      {/* Hero Banner - Restaurant Image */}
      {dyn.v1.addWrapDecoy("booking-banner", (
        <div className="w-full h-[340px] bg-gray-200 mb-10" id={dyn.v3.getVariant("booking-banner", ID_VARIANTS_MAP, "booking-banner")}>
          <div className="relative w-full h-full">
            {data?.image && (
              <Image
                src={data.image}
                alt={data.name || "Restaurant"}
                fill
                className="object-cover"
                id={dyn.v3.getVariant("booking-banner-image", ID_VARIANTS_MAP, "booking-banner-image")}
              />
            )}
          </div>
        </div>
      ), "booking-banner-wrap")}

      <div className="max-w-2xl mx-auto px-4 pb-10">
        <h2 className="font-bold text-lg mt-8 mb-4">
          {dyn.v3.getVariant("you_almost_done", undefined, "You're almost done!")}
        </h2>
        <div className="flex items-center gap-3 mb-6">
          <img
            src={data?.image || "/images/restaurant1.jpg"}
            alt={data?.name || "Restaurant"}
            className="w-16 h-16 rounded-lg object-cover border"
          />
          <div className="flex flex-col gap-[2px]">
            <span className="font-bold text-2xl">
              {data?.name ?? "Loading..."}
            </span>
            <div className="flex items-center gap-5 text-gray-700 mt-1 text-[15px]">
              <span className="flex items-center gap-1">
                <CalendarIcon className="w-4 h-4 mr-1" />
                {formattedDate ?? dyn.v3.getVariant("select_date", undefined, "Select date")}
              </span>
              <span className="flex items-center gap-1">
                <ClockIcon className="w-4 h-4 mr-1" />
                {reservationTime ?? dyn.v3.getVariant("select_time", undefined, "Select time")}
              </span>
              <span className="flex items-center gap-1">
                <UserIcon className="w-4 h-4 mr-1" />
                {reservationPeople ?? dyn.v3.getVariant("select_people", undefined, "Select people")}{" "}
                {dyn.v3.getVariant("people", undefined, "people")}
              </span>
            </div>
          </div>
        </div>

        <h3 className="font-semibold text-lg mb-4 mt-6">
          {dyn.v3.getVariant("diner_details", undefined, "Your Details")}
        </h3>
        <div className="space-y-4">
          {/* Name Field */}
          {dyn.v1.addWrapDecoy("full-name-field", (
            <div id={dyn.v3.getVariant("full-name-field-container", ID_VARIANTS_MAP, "full-name-field-container")}>
              <label 
                className="block text-sm font-medium text-gray-700 mb-1"
                htmlFor={dyn.v3.getVariant("full-name-input", ID_VARIANTS_MAP, "full-name-input")}
                id={dyn.v3.getVariant("full-name-label", ID_VARIANTS_MAP, "full-name-label")}
              >
                {dyn.v3.getVariant("full_name", TEXT_VARIANTS_MAP, "Full Name")}
              </label>
              <input
                type="text"
                id={dyn.v3.getVariant("full-name-input", ID_VARIANTS_MAP, "full-name-input")}
                placeholder={dyn.v3.getVariant("full_name_placeholder", TEXT_VARIANTS_MAP, "Enter your full name")}
                className={dyn.v3.getVariant("input-text", CLASS_VARIANTS_MAP, "w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-[#46a758] focus:border-[#46a758]")}
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
          ), "full-name-field-wrap")}

          {/* Phone Field */}
          {dyn.v1.addWrapDecoy("phone-field", (
            <div id={dyn.v3.getVariant("phone-field-container", ID_VARIANTS_MAP, "phone-field-container")}>
              <label 
                className="block text-sm font-medium text-gray-700 mb-1"
                htmlFor={dyn.v3.getVariant("phone-number-input", ID_VARIANTS_MAP, "phone-number-input")}
                id={dyn.v3.getVariant("phone-number-label", ID_VARIANTS_MAP, "phone-number-label")}
              >
                {dyn.v3.getVariant("phone_number", TEXT_VARIANTS_MAP, "Phone Number")}
              </label>
              <div className="flex">
                <select
                  id={dyn.v3.getVariant("country-select", ID_VARIANTS_MAP, "country-select")}
                  className={dyn.v3.getVariant("select-dropdown", CLASS_VARIANTS_MAP, "border border-gray-300 border-r-0 rounded-l-lg px-3 py-2.5 bg-white cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#46a758]")}
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
                  id={dyn.v3.getVariant("phone-number-input", ID_VARIANTS_MAP, "phone-number-input")}
                  placeholder={dyn.v3.getVariant("phone_number_placeholder", TEXT_VARIANTS_MAP, "Phone number")}
                  className={dyn.v3.getVariant("input-text", CLASS_VARIANTS_MAP, "flex-1 border border-gray-300 rounded-r-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-[#46a758] focus:border-[#46a758]")}
                  value={phoneNumber}
                  onChange={(e) => {
                    setPhoneNumber(e.target.value);
                    if (e.target.value.trim()) setPhoneError(false);
                  }}
                />
              </div>
              {phoneError && (
                <p className="text-red-500 text-sm mt-1" id={dyn.v3.getVariant("phone-error", ID_VARIANTS_MAP, "phone-error")}>
                  {dyn.v3.getVariant("phone_required", TEXT_VARIANTS_MAP, "Phone number is required")}
                </p>
              )}
            </div>
          ), "phone-field-wrap")}

          {/* Email Field */}
          {dyn.v1.addWrapDecoy("email-field", (
            <div id={dyn.v3.getVariant("email-field-container", ID_VARIANTS_MAP, "email-field-container")}>
              <label 
                className="block text-sm font-medium text-gray-700 mb-1"
                htmlFor={dyn.v3.getVariant("email-input", ID_VARIANTS_MAP, "email-input")}
                id={dyn.v3.getVariant("email-label", ID_VARIANTS_MAP, "email-label")}
              >
                {dyn.v3.getVariant("email", TEXT_VARIANTS_MAP, "Email")}
              </label>
              <input
                type="email"
                id={dyn.v3.getVariant("email-input", ID_VARIANTS_MAP, "email-input")}
                placeholder={dyn.v3.getVariant("email_placeholder", TEXT_VARIANTS_MAP, "your.email@example.com")}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={dyn.v3.getVariant("input-text", CLASS_VARIANTS_MAP, "w-full border border-gray-300 rounded-lg px-4 py-2.5 bg-gray-50 text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#46a758] focus:border-[#46a758]")}
              />
            </div>
          ), "email-field-wrap")}

          {/* Occasion Field */}
          {dyn.v1.addWrapDecoy("occasion-field", (
            <div id={dyn.v3.getVariant("occasion-field-container", ID_VARIANTS_MAP, "occasion-field-container")}>
              <label 
                className="block text-sm font-medium text-gray-700 mb-1"
                htmlFor={dyn.v3.getVariant("occasion-select", ID_VARIANTS_MAP, "occasion-select")}
                id={dyn.v3.getVariant("occasion-label", ID_VARIANTS_MAP, "occasion-label")}
              >
                {dyn.v3.getVariant("select_occasion", TEXT_VARIANTS_MAP, "Occasion (Optional)")}
              </label>
              <select
                id={dyn.v3.getVariant("occasion-select", ID_VARIANTS_MAP, "occasion-select")}
                className={dyn.v3.getVariant("select-dropdown", CLASS_VARIANTS_MAP, "w-full border border-gray-300 rounded-lg px-4 py-2.5 bg-white focus:outline-none focus:ring-2 focus:ring-[#46a758] focus:border-[#46a758]")}
                value={occasion}
                onChange={(e) => {
                  setOccasion(e.target.value);
                  logEvent(EVENT_TYPES.OCCASION_SELECTED, {
                    ...restaurantInfo,
                    occasion: e.target.value,
                  });
                }}
              >
                <option value="">{dyn.v3.getVariant("select_occasion_placeholder", TEXT_VARIANTS_MAP, "Select an occasion (optional)")}</option>
                <option value="birthday">
                  {dyn.v3.getVariant("birthday", TEXT_VARIANTS_MAP, "Birthday")}
                </option>
                <option value="anniversary">
                  {dyn.v3.getVariant("anniversary", TEXT_VARIANTS_MAP, "Anniversary")}
                </option>
                <option value="business">
                  {dyn.v3.getVariant("business_meal", TEXT_VARIANTS_MAP, "Business Meal")}
                </option>
                <option value="other">{dyn.v3.getVariant("other", TEXT_VARIANTS_MAP, "Other")}</option>
              </select>
            </div>
          ), "occasion-field-wrap")}

          {/* Special Request Field */}
          {dyn.v1.addWrapDecoy("special-request-field", (
            <div id={dyn.v3.getVariant("special-request-field-container", ID_VARIANTS_MAP, "special-request-field-container")}>
              <label 
                className="block text-sm font-medium text-gray-700 mb-1"
                htmlFor={dyn.v3.getVariant("special-requests-textarea", ID_VARIANTS_MAP, "special-requests-textarea")}
                id={dyn.v3.getVariant("special-requests-label", ID_VARIANTS_MAP, "special-requests-label")}
              >
                {dyn.v3.getVariant("special_request", TEXT_VARIANTS_MAP, "Special Requests (Optional)")}
              </label>
              <textarea
                id={dyn.v3.getVariant("special-requests-textarea", ID_VARIANTS_MAP, "special-requests-textarea")}
                placeholder={dyn.v3.getVariant("special_request_placeholder", TEXT_VARIANTS_MAP, "Any special requests or dietary requirements?")}
                className={dyn.v3.getVariant("textarea-text", CLASS_VARIANTS_MAP, "w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-[#46a758] focus:border-[#46a758] resize-none")}
                rows={3}
                value={specialRequest}
                onChange={(e) => setSpecialRequest(e.target.value)}
              />
            </div>
          ), "special-request-field-wrap")}
        </div>

        {dyn.v1.addWrapDecoy("confirm-booking-button", (
          <Button
            id={dyn.v3.getVariant("confirm_button", ID_VARIANTS_MAP, "confirm_button")}
            onClick={handleReservation}
            className={dyn.v3.getVariant("button-primary", CLASS_VARIANTS_MAP, "w-full bg-[#46a758] hover:bg-[#3d8f4a] text-white py-6 text-lg rounded-lg font-semibold mt-6 transition-colors shadow-sm")}
          >
            {dyn.v3.getVariant("confirm_booking", TEXT_VARIANTS_MAP, "Complete Reservation")}
          </Button>
        ), "confirm-booking-button-wrap")}

        <p className="text-xs text-gray-600 mt-3 text-center">
          By completing this reservation, you agree to our{" "}
          <Link href="#" className="text-[#46a758] underline">
            {dyn.v3.getVariant("terms_of_use", undefined, "Terms of Use")}
          </Link>{" "}
          and{" "}
          <Link href="#" className="text-[#46a758] underline">
            {dyn.v3.getVariant("privacy_policy", undefined, "Privacy Policy")}
          </Link>
          . {dyn.v3.getVariant("message_rates", undefined, "Message and data rates may apply.")}
        </p>
      </div>

      {showToast && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 bg-green-600 text-white px-20 py-5 rounded shadow-lg z-50">
          {dyn.v3.getVariant("confirmation_message", TEXT_VARIANTS_MAP, "Reservation confirmed!")}
        </div>
      )}
      </main>
    ), "booking-page-wrap")
  );
}
