"use client";
import { useParams } from "next/navigation";
import {
  CalendarIcon,
  Star,
  UserIcon,
  ChevronDownIcon,
  ClockIcon,
} from "lucide-react";
import { Calendar } from "@/components/ui/calendar";
import React, { useEffect, useState } from "react";

import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { format } from "date-fns";
import Image from "next/image";
import { SeedLink } from "@/components/ui/SeedLink";
import { useSeed } from "@/context/SeedContext";
import { EVENT_TYPES, logEvent } from "@/library/events";
import Link from "next/link";
import { initializeRestaurants, getRestaurants } from "@/library/dataset";
import { useSeedVariation } from "@/library/utils";
import { isDataGenerationEnabled } from "@/shared/data-generator";

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
  tags: string[];
  desc: string;
  photos: string[];
};
export default function RestaurantPage() {
  const params = useParams();
  const id = params.restaurantId as string;
  const [r, setR] = useState<RestaurantView | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [people, setPeople] = useState<number | undefined>(undefined);
  const [time, setTime] = useState<string | undefined>(undefined);
  const [showFullMenu, setShowFullMenu] = useState(false);
  const [peopleOpen, setPeopleOpen] = useState(false);
  const [dateOpen, setDateOpen] = useState(false);
  const [timeOpen, setTimeOpen] = useState(false);
  const [date, setDate] = useState<Date | undefined>(undefined);

  const { seed } = useSeed();

  // Use seed-based variations
  const bookButtonVariation = useSeedVariation("bookButton");
  const dropdownVariation = useSeedVariation("dropdown");
  const imageContainerVariation = useSeedVariation("imageContainer");
  
  // Create layout based on seed
  const layout = {
    wrap: seed % 2 === 0, // Even seeds wrap, odd seeds don't
    justify: ["flex-start", "center", "flex-end", "space-between", "space-around"][seed % 5],
    marginTop: [0, 4, 8, 12, 16][seed % 5],
  };

  useEffect(() => {
    // Ensure data is initialized and loaded from DB or generator as configured
    let mounted = true;
    const run = async () => {
      setIsLoading(true);
      const genEnabled = isDataGenerationEnabled();
      if (genEnabled) setIsGenerating(true);
      try {
        await initializeRestaurants();
        if (!mounted) return;
        const list = getRestaurants();
        const found = list.find((x) => x.id === id) || list[0];
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
            tags: ["cozy", "modern", "casual"],
            desc: `Enjoy a delightful experience at ${found.name}, offering a fusion of flavors in the heart of ${found.area ?? "Downtown"}.`,
            photos,
          };
          setR(mapped);
        }
      } finally {
        if (!mounted) return;
        setIsLoading(false);
        setIsGenerating(false);
      }
    };
    run();
    return () => { mounted = false; };
  }, [id]);

  useEffect(() => {
    if (!r) return; // avoid sending until data is ready
    logEvent(EVENT_TYPES.VIEW_RESTAURANT, {
      restaurantId: id,
      restaurantName: r?.name ?? "",
      cuisine: r?.cuisine ?? "",
      desc: r?.desc ?? "",
      area: "test",
      reviews: r?.reviews ?? 0,
      bookings: r?.bookings ?? 0,
      rating: r?.rating ?? 0,
    });
  }, [id, r]);
  const formattedDate = date ? format(date, "yyyy-MM-dd") : "2025-05-20";

  const handleToggleMenu = () => {
    const newState = !showFullMenu;
    setShowFullMenu(newState);

    // Define menu data that should be included in both events
    const menuData = [
      {
        category: "Mains",
        items: [
          { name: "Coq au Vin", price: "$26.00" },
          { name: "Ratatouille", price: "$20.00" },
        ],
      },
    ];

    logEvent(
      newState ? EVENT_TYPES.VIEW_FULL_MENU : EVENT_TYPES.COLLAPSE_MENU,
      {
        restaurantId: id,
        restaurantName: r?.name ?? "",
        cuisine: r?.cuisine ?? "",
        desc: r?.desc ?? "",
        area: "test",
        reviews: r?.reviews ?? 0,
        bookings: r?.bookings ?? 0,
        rating: r?.rating ?? 0,
        action: newState ? "view_full_menu" : "collapse_menu",
        time,
        date: formattedDate,
        people,
        menu: menuData,
      }
    );
  };
  const peopleOptions = [1, 2, 3, 4, 5, 6, 7, 8];
  const handlePeopleSelect = (n: number) => {
    setPeople(n);
    logEvent(EVENT_TYPES.PEOPLE_DROPDOWN_OPENED, { people: n });
  };
  const handleTimeSelect = (t: string) => {
    setTime(t);
    logEvent(EVENT_TYPES.TIME_DROPDOWN_OPENED, { time: t });
  };
  const timeOptions = [
    "12:00 PM",
    "12:30 PM",
    "1:00 PM",
    "1:30 PM",
    "2:00 PM",
    "2:30 PM",
  ];
  function toLocalISO(date: Date): string {
    const pad = (n: number) => String(n).padStart(2, "0");

    const year = date.getFullYear();
    const month = pad(date.getMonth() + 1);
    const day = pad(date.getDate());
    const hours = pad(date.getHours());
    const minutes = pad(date.getMinutes());
    const seconds = pad(date.getSeconds());

    const tzOffset = -date.getTimezoneOffset();
    const sign = tzOffset >= 0 ? "+" : "-";
    const offsetHours = pad(Math.floor(Math.abs(tzOffset) / 60));
    const offsetMinutes = pad(Math.abs(tzOffset) % 60);

    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}${sign}${offsetHours}:${offsetMinutes}`;
  }
  const handleDateSelect = (d: Date | undefined) => {
    setDate(d);
    if (d) {
      // logEvent(EVENT_TYPES.DATE_DROPDOWN_OPENED, { date: d.toISOString() });
      logEvent(EVENT_TYPES.DATE_DROPDOWN_OPENED, { date: toLocalISO(d) });
    }
  };

  const wrapperClass = `flex justify-${layout.justify} mt-${layout.marginTop} mb-7 flex-wrap`;
  return (
    <main>
      {isGenerating && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/90">
          <div className="flex flex-col items-center gap-4">
            <div className="h-12 w-12 rounded-full border-4 border-gray-300 border-t-[#46a758] animate-spin" aria-hidden="true" />
            <div className="text-gray-700 text-base font-medium text-center">
              Data is being generated by AI this may take some time
            </div>
          </div>
        </div>
      )}
      {/* Banner Image */}
      <div className={`w-full h-[340px] bg-gray-200 ${imageContainerVariation.position} ${imageContainerVariation.className}`} data-testid={imageContainerVariation.dataTestId}>
        <div className="relative w-full h-full">
          {r && <Image src={r.image} alt={r.name} fill className="object-cover" />}
        </div>
      </div>
      {/* Info and reservation */}
      <div className="flex flex-col md:flex-row justify-between gap-10 px-8 max-w-screen-2xl mx-auto">
        {/* Info (details section, tags, desc, photos) */}
        <div className="pt-12 pb-10 flex-1 min-w-0">
          {/* Title & details row */}
          <h1 className="text-4xl font-bold mb-2">{r?.name ?? "Loading..."}</h1>
          <div className="flex items-center gap-4 text-lg mb-4">
            <span className="flex items-center text-[#46a758] text-xl font-semibold">
              {Array.from({ length: 4 }).map((_, i) => (
                <span key={i}>★</span>
              ))}
              <span className="text-gray-300">★</span>
            </span>
            <span className="text-base flex items-center gap-2">
              <span className="font-bold">
                {r?.rating?.toFixed?.(2) ?? "4.20"}
              </span>{" "}
              <span className="text-gray-700">{r?.reviews ?? 20} Reviews</span>
            </span>
            <span className="text-base flex items-center gap-2">
              💵 {r?.price ?? "$$"}
            </span>
            <span className="text-base flex items-center gap-2">
              {r?.cuisine ?? "International"}
            </span>
          </div>
          {/* Tags/Pills */}
          <div className="flex gap-2 mb-4">
            {(r?.tags || []).map((tag: string, index: number) => (
              <span
                key={tag}
                className="py-1 px-4 bg-gray-100 rounded-full text-gray-800 font-semibold text-base border"
              >
                {tag}
              </span>
            ))}
          </div>
          {/* Description */}
          {r?.desc && (
            <div className="mb-7 text-[17px] text-gray-700 max-w-2xl">
              {r.desc}
            </div>
          )}
          {/* Photos Grid */}
          {r?.photos && (
            <>
              <h2 className="text-2xl font-bold mb-3">
                {r.photos.length} photos
              </h2>
              <div className="grid grid-cols-3 gap-3 w-full max-w-2xl mb-9">
                {r.photos.map((url: string, i: number) => (
                  <img
                    key={i}
                    src={url}
                    alt=""
                    className="rounded-lg object-cover aspect-square w-full h-[112px] md:h-[140px]"
                  />
                ))}
              </div>
            </>
          )}
          {/* Menu Section */}
          <section className="max-w-2xl w-full mb-10">
            <h2 className="text-2xl font-bold mb-3 mt-8">Menu</h2>
            <div className="flex gap-6 border-b mb-5">
              <button className="border-b-2 border-[#46a758] text-[#46a758] font-semibold px-4 py-2 -mb-px bg-white">
                Main Menu
              </button>
            </div>
            <div className="space-y-6">
              <div>
                <div className="font-bold text-lg mb-3">Starters</div>
                <div className="grid grid-cols-2 gap-y-2">
                  <div>
                    <div className="font-semibold">Cheese Board</div>
                    <div className="text-sm text-gray-600">
                      assorted artisan cheeses
                    </div>
                  </div>
                  <div className="text-right font-bold">$14.00</div>

                  <div>
                    <div className="font-semibold">Smoked Salmon Tartine</div>
                    <div className="text-sm text-gray-600">
                      capers, crème fraîche
                    </div>
                  </div>
                  <div className="text-right font-bold">$12.00</div>

                  <div>
                    <div className="font-semibold">Escargot</div>
                    <div className="text-sm text-gray-600">
                      with garlic butter
                    </div>
                  </div>
                  <div className="text-right font-bold">$16.00</div>
                </div>
              </div>
              {showFullMenu && (
                <div>
                  <div className="font-bold text-lg mb-3">Mains</div>
                  <div className="grid grid-cols-2 gap-y-2">
                    <div className="font-semibold">Coq au Vin</div>
                    <div className="text-right font-bold">$26.00</div>
                    <div className="font-semibold">Ratatouille</div>
                    <div className="text-right font-bold">$20.00</div>
                  </div>
                </div>
              )}
              <div className="flex justify-center my-7">
                {layout.wrap ? (
                  <div className={wrapperClass}>
                    {" "}
                    <Button
                      className="border px-10 py-3 text-lg rounded font-semibold bg-white hover:bg-gray-50 text-black"
                      onClick={handleToggleMenu}
                    >
                      {showFullMenu ? "Collapse menu" : "View full menu"}
                    </Button>
                  </div>
                ) : (
                  <div className={wrapperClass.replace("flex-wrap", "")}>
                    <Button
                      className="border px-10 py-3 text-lg rounded font-semibold bg-white hover:bg-gray-50 text-black"
                      onClick={handleToggleMenu}
                    >
                      {showFullMenu ? "Collapse menu" : "View full menu"}
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </section>
          {/* Reviews Section */}
          <section className="max-w-2xl w-full mb-10">
            <h2 className="text-2xl font-bold mb-5 mt-10">
              What 20 people are saying
            </h2>
            <div className="font-bold mb-2">Overall ratings and reviews</div>
            <div className="mb-4 text-gray-700">
              Reviews can only be made by diners who have booked through
              OpenDinning and dined at this restaurant.
            </div>
            {/* Ratings bar chart (simplified) */}
            <div className="mb-6 space-y-1">
              {[5, 4, 3, 2, 1].map((star) => (
                <div key={star} className="flex items-center gap-2">
                  <span className="w-5 text-right">{star}</span>
                  <span className="w-20 bg-red-200 h-3 rounded">
                    <span
                      className={`block h-3 rounded bg-[#46a758]`}
                      style={{ width: `${star * 12}%` }}
                    />
                  </span>
                </div>
              ))}
            </div>
          </section>
        </div>
        {/* Reservation Box - now more detailed per screenshot */}
        <div className="rounded-xl border bg-white shadow-sm p-6 w-full max-w-sm mt-[-120px] md:mt-16 self-start">
          <h2 className="font-bold text-lg mb-2 text-center">
            Make a reservation
          </h2>
          <div className="flex flex-col gap-3">
            {/* People select (demo, not fully interactive) */}
            <Popover open={peopleOpen} onOpenChange={setPeopleOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className="flex items-center gap-2 min-w-[100px] justify-start"
                >
                  <UserIcon className="h-5 w-5 text-gray-700" />
                  {people ? people : "Pick"}{" "}
                  {people === 1 ? "Person" : "People"}{" "}
                  <ChevronDownIcon className="h-4 w-4 text-gray-400" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-32 p-1">
                {peopleOptions.map((n) => (
                  <Button
                    key={n}
                    variant="ghost"
                    className="w-full justify-start"
                    onClick={() => {
                      handlePeopleSelect(n);
                      setPeopleOpen(false);
                    }}
                  >
                    {n} {n === 1 ? "person" : "people"}
                  </Button>
                ))}
              </PopoverContent>
            </Popover>
            {/* Date/time row */}
            <div className="flex gap-2">
              <Popover open={dateOpen} onOpenChange={setDateOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="flex items-center gap-2 min-w-[120px] justify-start"
                  >
                    <CalendarIcon className="h-5 w-5 text-gray-700" />
                    {date ? format(date, "MMM d") : "Pick date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={date}
                    onSelect={(d) => {
                      handleDateSelect(d);
                      setDateOpen(false);
                    }}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
              <Popover open={timeOpen} onOpenChange={setTimeOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className="flex items-center gap-2 min-w-[120px] justify-start"
                  >
                    <ClockIcon className="h-5 w-5 text-gray-700" />
                    {time ? time : "Pick Time"}
                    <ChevronDownIcon className="h-4 w-4 text-gray-400" />
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-36 p-1">
                  {timeOptions.map((t) => (
                    <Button
                      key={t}
                      variant="ghost"
                      className="w-full justify-start"
                      onClick={() => {
                        handleTimeSelect(t);
                        setTimeOpen(false);
                      }}
                    >
                      {t}
                    </Button>
                  ))}
                </PopoverContent>
              </Popover>
            </div>
            {/* Time slots */}
            <div className="mt-3">
              {time === "3:00 PM" ? (
                <div
                  className="flex gap-1 mt-2"
                  style={{
                    justifyContent: layout.justify,
                    marginTop: layout.marginTop,
                  }}
                >
                  <Button
                    variant="outline"
                    className="text-[#46a758] border-[#46a758] px-4 py-2 text-base flex items-center gap-2"
                  >
                    <span>{time}</span>
                    <span className="ml-2">🔔 Notify me</span>
                  </Button>
                </div>
              ) : time ? (
                layout.wrap ? (
                  <div
                    className="mt-2"
                    style={{ marginTop: layout.marginTop }}
                    data-testid={`book-btn-wrapper-${seed}`}
                  >
                    <div
                      className="flex gap-1"
                      style={{ justifyContent: layout.justify }}
                    >
                      <Link
                        href={`/booking/${id}/${encodeURIComponent(
                          time
                        )}?date=${formattedDate}&people=${people ?? ""}`}
                        onClick={() =>
                          logEvent(EVENT_TYPES.BOOK_RESTAURANT, {
                            restaurantId: id,
                            restaurantName: r?.name ?? "",
                            cuisine: r?.cuisine ?? "",
                            desc: r?.desc ?? "",
                            area: "test",
                            reviews: r?.reviews ?? 0,
                            bookings: r?.bookings ?? 0,
                            rating: r?.rating ?? 0,
                            date: formattedDate,
                            time,
                            people,
                          })
                        }
                        passHref
                      >
                        <Button
                          className={`${bookButtonVariation.className} font-semibold text-sm`}
                          data-testid={bookButtonVariation.dataTestId}
                          asChild
                        >
                          <span>Book Restaurant</span>
                        </Button>
                      </Link>
                    </div>
                  </div>
                ) : (
                  <div
                    className="flex gap-1 mt-2"
                    style={{
                      justifyContent: layout.justify,
                      marginTop: layout.marginTop,
                    }}
                  >
                    <SeedLink
                      href={`/booking/${id}/${encodeURIComponent(
                        time
                      )}?date=${formattedDate}&people=${people ?? ""}`}
                      onClick={() =>
                        logEvent(EVENT_TYPES.BOOK_RESTAURANT, {
                          restaurantId: id,
                          restaurantName: r?.name ?? "",
                          cuisine: r?.cuisine ?? "",
                          desc: r?.desc ?? "",
                          area: "test",
                          reviews: r?.reviews ?? 0,
                          bookings: r?.bookings ?? 0,
                          rating: r?.rating ?? 0,
                          date: formattedDate,
                          time,
                          people,
                        })
                      }
                      passHref
                    >
                      <Button
                        className={`${bookButtonVariation.className} font-semibold text-sm`}
                        data-testid={bookButtonVariation.dataTestId}
                        asChild
                      >
                        <span>Book Restaurant</span>
                      </Button>
                    </SeedLink>
                  </div>
                )
              ) : (
                <div className="text-gray-500 text-sm mt-2">
                  Please select a time
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
