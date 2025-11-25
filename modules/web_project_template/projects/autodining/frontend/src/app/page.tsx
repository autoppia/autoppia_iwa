"use client";
import { SeedLink } from "@/components/ui/SeedLink";
import { useState, useRef, useEffect, useMemo, Suspense } from "react";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { format } from "date-fns";
import {
  CalendarIcon,
  ClockIcon,
  UserIcon,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import React from "react";
import { useSeed } from "@/context/SeedContext";
import { EVENT_TYPES, logEvent } from "@/library/events";
import { getRestaurants, initializeRestaurants } from "@/library/dataset";
import { useSearchParams } from "next/navigation";
import { useSeedVariation } from "@/library/utils";
import { isDataGenerationEnabled } from "@/shared/data-generator";

// UI restaurant type with required fields
type UiRestaurant = {
  id: string;
  name: string;
  cuisine: string;
  area: string;
  reviews: number;
  stars: number;
  price: string;
  bookings: number;
  image: string;
  times: string[];
};

// List will be populated only after data generation/DB fetch completes

function StarRating({ count }: { count: number }) {
  return (
    <span className="text-[#46a758] text-xl align-middle mr-1">
      {Array.from({ length: 5 }).map((_, i) => (
        <span key={i}>{i < count ? "★" : "☆"}</span>
      ))}
    </span>
  );
}

function StarNumber({ rating }: { rating: number }) {
  return (
    <span className="text-[#46a758] font-bold inline-flex items-center ml-1 mr-1">
      <span className="text-lg">★</span> {rating.toFixed(2)}
    </span>
  );
}

function RestaurantCard({
  r,
  date,
  people,
  time,
}: {
  r: {
    id: string;
    name: string;
    cuisine: string;
    area: string;
    reviews: number;
    stars: number;
    price: string;
    bookings: number;
    image: string;
    times: string[];
  };
  date: Date | undefined;
  people: number;
  time: string;
}) {
  const { seed } = useSeed();

  const formattedDate = date ? format(date, "yyyy-MM-dd") : "2025-05-20";

  // Use seed-based variations with event support
  const restaurantCardVariation = useSeedVariation("restaurantCard");
  const bookButtonVariation = useSeedVariation("bookButton");
  const imageContainerVariation = useSeedVariation("imageContainer");
  const cardContainerVariation = useSeedVariation("cardContainer");
  
  // Create layout based on seed
  const layout = {
    wrap: seed % 2 === 0, // Even seeds wrap, odd seeds don't
    justify: ["flex-start", "center", "flex-end", "space-between", "space-around"][seed % 5],
    marginTop: ["mt-4", "mt-6", "mt-8", "mt-10", "mt-12"][seed % 5],
  };

  return (
    <div
      className={`w-[255px] flex-shrink-0 rounded-xl border shadow-sm bg-white overflow-hidden`}
      data-testid={restaurantCardVariation.dataTestId}
      style={restaurantCardVariation.style}
    >
      <div className="w-full h-40 overflow-hidden">
        <img
          src={r.image}
          alt={r.name}
          className="w-full h-full object-cover"
        />
      </div>
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold text-lg">{r.name}</h3>
          <div className="flex items-center">
            <StarRating count={r.stars} />
            <span className="text-sm text-gray-600">({r.reviews})</span>
          </div>
        </div>
        <p className="text-gray-600 text-sm mb-2">{r.cuisine}</p>
        <p className="text-gray-500 text-xs mb-3">{r.area}</p>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">{r.price}</span>
          <span className="text-xs text-gray-500">{r.bookings} booked today</span>
        </div>
        <div className={`mt-3 flex ${layout.wrap ? 'flex-wrap' : 'flex-nowrap'} ${layout.justify} gap-2`}>
          <SeedLink
            href={`/restaurant/${r.id}`}
            className="text-sm text-blue-600 hover:text-blue-800"
            onClick={() => logEvent(EVENT_TYPES.VIEW_RESTAURANT, { restaurantId: r.id })}
          >
            View details
          </SeedLink>
          <SeedLink
            href={`/booking/${r.id}/${time}?people=${people}&date=${formattedDate}`}
            className={`${bookButtonVariation.className} text-sm`}
            data-testid={bookButtonVariation.dataTestId}
            style={{ position: bookButtonVariation.position as any }}
            onClick={() => logEvent(EVENT_TYPES.BOOK_RESTAURANT, { restaurantId: r.id })}
          >
            Book now
          </SeedLink>
        </div>
      </div>
    </div>
  );
}

function CardScroller({ children, title }: { children: React.ReactNode; title: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const rafIdRef = useRef<number | null>(null);
  const tickingRef = useRef(false);

  const { seed } = useSeed();
  const cardContainerVariation = useSeedVariation("cardContainer");
  const childCount = React.Children.count(children);

  const checkScroll = () => {
    if (ref.current) {
      const { scrollLeft, scrollWidth, clientWidth } = ref.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 1);
    }
  };

  const scheduleCheck = () => {
    if (tickingRef.current) return;
    tickingRef.current = true;
    rafIdRef.current = window.requestAnimationFrame(() => {
      checkScroll();
      tickingRef.current = false;
    });
  };

  useEffect(() => {
    checkScroll();
    let ro: ResizeObserver | null = null;
    if (ref.current && typeof ResizeObserver !== 'undefined') {
      ro = new ResizeObserver(() => scheduleCheck());
      ro.observe(ref.current);
    }
    window.addEventListener("resize", scheduleCheck);
    return () => {
      window.removeEventListener("resize", scheduleCheck);
      if (ro && ref.current) ro.disconnect();
      if (rafIdRef.current !== null) cancelAnimationFrame(rafIdRef.current);
      tickingRef.current = false;
    };
  }, []);

  const scroll = (direction: "left" | "right") => {
    if (ref.current) {
      const scrollAmount = 300;
      const newScrollLeft = ref.current.scrollLeft + (direction === "left" ? -scrollAmount : scrollAmount);
      ref.current.scrollTo({ left: newScrollLeft, behavior: "smooth" });
      
      // Log scroll event
      logEvent(EVENT_TYPES.SCROLL_VIEW, { direction, title });
    }
  };

  if (childCount === 0) {
    return null;
  }

  return (
    <div className="relative overflow-hidden">
      <button
        onClick={() => scroll("left")}
        className={`absolute left-0 top-1/2 transform -translate-y-1/2 z-10 bg-white border rounded-full p-2 shadow-lg hover:bg-gray-50 ${canScrollLeft ? '' : 'opacity-50 cursor-not-allowed'}`}
        data-testid={`scroll-left-${seed}`}
        disabled={!canScrollLeft}
      >
        <ChevronLeft className="w-5 h-5" />
      </button>
      <button
        onClick={() => scroll("right")}
        className={`absolute right-0 top-1/2 transform -translate-y-1/2 z-10 bg-white border rounded-full p-2 shadow-lg hover:bg-gray-50 ${canScrollRight ? '' : 'opacity-50 cursor-not-allowed'}`}
        data-testid={`scroll-right-${seed}`}
        disabled={!canScrollRight}
      >
        <ChevronRight className="w-5 h-5" />
      </button>
      {/* Scrollable Content */}
      <div
        ref={ref}
        className={`flex gap-4 pb-4 scroll-smooth pl-1 pr-10 overflow-x-auto overflow-y-hidden`}
        data-testid={cardContainerVariation.dataTestId}
        onScroll={scheduleCheck}
      >
        {children}
      </div>
    </div>
  );
}

function getLayoutVariant(seed: number) {
  return {
    marginTop: ["mt-4", "mt-6", "mt-8", "mt-10", "mt-12"][seed % 5],
    wrapButton: seed % 3 === 0, // Every 3rd seed wraps the button
  };
}

// Client-only component that uses seed from context
function HomePageContent() {
  const [isReady, setIsReady] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [list, setList] = useState<UiRestaurant[]>([]);
  const [date, setDate] = useState<Date | undefined>(new Date());
  const [time, setTime] = useState("1:00 PM");
  const [people, setPeople] = useState(2);
  const [search, setSearch] = useState("");
  const [dateOpen, setDateOpen] = useState(false);
  const [timeOpen, setTimeOpen] = useState(false);
  const [peopleOpen, setPeopleOpen] = useState(false);

  const { seed } = useSeed();
  const { marginTop, wrapButton } = useMemo(
    () => getLayoutVariant(seed),
    [seed]
  );

  // Use seed-based variations with event support
  const searchBarVariation = useSeedVariation("searchBar");
  const searchButtonVariation = useSeedVariation("searchButton");
  const pageLayoutVariation = useSeedVariation("pageLayout");
  const sectionLayoutVariation = useSeedVariation("sectionLayout");
  


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
      const isoDate = toLocalISO(d);
      logEvent(EVENT_TYPES.DATE_DROPDOWN_OPENED, { date: isoDate });
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearch(value);
    logEvent(EVENT_TYPES.SEARCH_RESTAURANT, { query: value });
  };

  const handleTimeSelect = (t: string) => {
    setTime(t);
    logEvent(EVENT_TYPES.TIME_DROPDOWN_OPENED, { time: t });
  };

  const handlePeopleSelect = (n: number) => {
    setPeople(n);
    logEvent(EVENT_TYPES.PEOPLE_DROPDOWN_OPENED, { people: n });
  };

  function matches(r: UiRestaurant): boolean {
    const q = search.trim().toLowerCase();
    return (
      !q ||
      r.name.toLowerCase().includes(q) ||
      r.cuisine.toLowerCase().includes(q) ||
      r.area.toLowerCase().includes(q)
    );
  }

  const filtered = list.filter(matches);
  const peopleOptions = [1, 2, 3, 4, 5, 6, 7, 8];
  const timeOptions = [
    "12:00 PM",
    "12:30 PM",
    "1:00 PM",
    "1:30 PM",
    "2:00 PM",
    "2:30 PM",
  ];

  useEffect(() => {
    let didRun = false;
    const runOnce = async () => {
      if (didRun) return; // guard
      didRun = true;
      setIsLoading(true);
      const genEnabled = isDataGenerationEnabled();
      if (genEnabled) setIsGenerating(true);
      try {
        await initializeRestaurants(); // waits for DB/gen
        const fresh = getRestaurants().map((r) => ({
          id: r.id,
          name: r.name,
          image: r.image,
          cuisine: r.cuisine ?? "International",
          area: r.area ?? "Downtown",
          reviews: r.reviews ?? 0,
          stars: r.stars ?? 4,
          price: r.price ?? "$$",
          bookings: r.bookings ?? 0,
          times: ["1:00 PM"],
        }));
        setList(fresh);
        setIsReady(true);
      } finally {
        setIsLoading(false);
        setIsGenerating(false);
      }
    };
    runOnce();
  }, []);

  return (
    <main suppressHydrationWarning>
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
      {/* Navigation/Header */}
      <nav className="w-full border-b bg-white sticky top-0 z-10">
        <div className="max-w-6xl mx-auto flex items-center justify-between h-20 px-4 gap-2">
          <div className="flex items-center gap-3">
            <SeedLink href="/">
              <div className="bg-[#46a758] px-3 py-1 rounded flex items-center h-9">
                <span className="font-bold text-white text-lg">AutoDining</span>
              </div>
            </SeedLink>
          </div>

          <div className="flex items-center gap-4">
            <SeedLink
              className="text-sm text-gray-600 hover:text-[#46a758]"
              href="/help"
            >
              Get help
            </SeedLink>
            <SeedLink
              className="text-sm text-gray-600 hover:text-[#46a758]"
              href="/about"
            >
              About
            </SeedLink>
            <SeedLink
              className="text-sm text-gray-600 hover:text-[#46a758]"
              href="/contact"
            >
              Contact
            </SeedLink>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className={pageLayoutVariation.className} data-testid={pageLayoutVariation.dataTestId}>
        {(isLoading || !isReady) && (
          <div className="text-center text-gray-500 mb-4">Loading restaurants...</div>
        )}
        <h1 className="text-4xl font-bold mb-6">Find your table for any occasion</h1>
        
        {/* Search and Filters */}
        <section className="flex flex-wrap gap-4 items-end">
          <Popover open={dateOpen} onOpenChange={setDateOpen}>
            <PopoverTrigger asChild>
              <Button
              id="select-date"
                variant="outline"
                className="w-[200px] justify-start text-left font-normal"
                onClick={() => logEvent(EVENT_TYPES.DATE_DROPDOWN_OPENED, { action: 'open' })}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {date ? format(date, "PPP") : <span>Pick a date</span>}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={date}
                onSelect={handleDateSelect}
                initialFocus
              />
            </PopoverContent>
          </Popover>

          <Popover open={timeOpen} onOpenChange={setTimeOpen}>
            <PopoverTrigger asChild>
              <Button
                id="select-time"
                variant="outline"
                className="w-[150px] justify-start text-left font-normal"
                onClick={() => logEvent(EVENT_TYPES.TIME_DROPDOWN_OPENED, { action: 'open' })}
              >
                <ClockIcon className="mr-2 h-4 w-4" />
                {time}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <div className="p-2">
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
              </div>
            </PopoverContent>
          </Popover>

          <Popover open={peopleOpen} onOpenChange={setPeopleOpen}>
            <PopoverTrigger asChild>
              <Button
                id="select-people"
                variant="outline"
                className="w-[150px] justify-start text-left font-normal"
                onClick={() => logEvent(EVENT_TYPES.PEOPLE_DROPDOWN_OPENED, { action: 'open' })}
              >
                <UserIcon className="mr-2 h-4 w-4" />
                {people} {people === 1 ? "person" : "people"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <div className="p-2">
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
              </div>
            </PopoverContent>
          </Popover>
          {/* Search box & button */}
          <input
            type="text"
            placeholder="Location, Restaurant, or Cuisine"
            className={`${searchBarVariation.className} min-w-[250px] flex-1`}
            data-testid={searchBarVariation.dataTestId}
            value={search}
            onChange={handleSearchChange}
          />
          {wrapButton ? (
            <div data-testid={`wrapper-${seed}`}>
              <button
                className={searchButtonVariation.className}
                data-testid={searchButtonVariation.dataTestId}
                style={{ position: searchButtonVariation.position as any }}
              >
                Let's go
              </button>
            </div>
          ) : (
            <button
              className={searchButtonVariation.className}
              data-testid={searchButtonVariation.dataTestId}
              style={{ position: searchButtonVariation.position as any }}
            >
              Let's go
            </button>
          )}
        </section>

        {/* Main Content - Cards, Sections, etc. */}
        {(isLoading || !isReady || list.length === 0) ? null : wrapButton ? (
          <div data-testid={`section-wrapper-${seed}`}>
            {isReady && list.length > 0 && (
            <section className={`${sectionLayoutVariation.className} px-4 mt-${marginTop}`} data-testid={sectionLayoutVariation.dataTestId}>
              <h2 className="text-2xl font-bold mb-4">Available for lunch now</h2>
              <CardScroller title="Available for lunch now">
                {filtered.map((r) => (
                  <RestaurantCard
                    key={r.id + "-lunch"}
                    r={r}
                    date={date}
                    people={people}
                    time={time}
                  />
                ))}
              </CardScroller>
            </section>
            )}
          </div>
        ) : (
          isLoading || !isReady || list.length === 0 ? null : (
            <section className={`${sectionLayoutVariation.className} px-4 mt-${marginTop}`} data-testid={sectionLayoutVariation.dataTestId}>
              <h2 className="text-2xl font-bold mb-4">Available for lunch now</h2>
              <CardScroller title="Available for lunch now">
                {filtered.map((r) => (
                  <RestaurantCard
                    key={r.id + "-lunch"}
                    r={r}
                    date={date}
                    people={people}
                    time={time}
                  />
                ))}
              </CardScroller>
            </section>
          )
        )}

        {/* Introducing OpenDinning Icons Section */}
        {wrapButton ? (
          <div data-testid={`icon-section-wrapper-${seed}`}>
            <section
              className={`${sectionLayoutVariation.className} mt-${marginTop} rounded-xl bg-[#f7f7f6] border px-4`}
              data-testid={sectionLayoutVariation.dataTestId}
            >
              <div className="flex flex-row justify-between items-center mb-1">
                <div>
                  <h2 className="text-2xl md:text-2xl font-bold">
                    Introducing OpenDinning Icons
                  </h2>
                  <div className="text-base text-gray-600 mt-1 mb-3">
                    Book the city's award-winners, hot newcomers, and hard-to-get
                    tables.
                  </div>
                </div>
                <button className="border px-5 py-2 rounded-md text-base font-semibold hover:bg-gray-100 whitespace-nowrap h-12">
                  Explore Icon restaurants
                </button>
              </div>
              <CardScroller title="Introducing OpenDinning Icons">
                {list.slice(15, 30).map((r) => (
                  <RestaurantCard
                    key={r.id + "-icon"}
                    r={r}
                    date={date}
                    people={people}
                    time={time}
                  />
                ))}
              </CardScroller>
            </section>
          </div>
        ) : (
          <section
            className={`${sectionLayoutVariation.className} mt-${marginTop} rounded-xl bg-[#f7f7f6] border px-4`}
            data-testid={sectionLayoutVariation.dataTestId}
          >
            <div className="flex flex-row justify-between items-center mb-1">
              <div>
                <h2 className="text-2xl md:text-2xl font-bold">
                  Introducing OpenDinning Icons
                </h2>
                <div className="text-base text-gray-600 mt-1 mb-3">
                  Book the city's award-winners, hot newcomers, and hard-to-get
                  tables.
                </div>
              </div>
              <button className="border px-5 py-2 rounded-md text-base font-semibold hover:bg-gray-100 whitespace-nowrap h-12">
                Explore Icon restaurants
              </button>
            </div>
            <CardScroller title="Introducing OpenDinning Icons">
              {list.slice(15, 30).map((r) => (
                <RestaurantCard
                  key={r.id + "-icon"}
                  r={r}
                  date={date}
                  people={people}
                  time={time}
                />
              ))}
            </CardScroller>
          </section>
        )}

        {/* Award Winners Section */}
        {wrapButton ? (
          <div data-testid={`award-section-wrapper-${seed}`}>
            <section className={`${sectionLayoutVariation.className} mt-${marginTop} px-4`} data-testid={sectionLayoutVariation.dataTestId}>
              <h2 className="text-2xl font-bold mb-4">Award Winners</h2>
              <CardScroller title="Award Winners">
                {list.slice(30, 50).map((r) => (
                  <RestaurantCard
                    key={r.id + "-award"}
                    r={r}
                    date={date}
                    people={people}
                    time={time}
                  />
                ))}
              </CardScroller>
            </section>
          </div>
        ) : (
          <section className={`${sectionLayoutVariation.className} mt-${marginTop} px-4`} data-testid={sectionLayoutVariation.dataTestId}>
            <h2 className="text-2xl font-bold mb-4">Award Winners</h2>
            <CardScroller title="Award Winners">
              {list.slice(30, 50).map((r) => (
                <RestaurantCard
                  key={r.id + "-award"}
                  r={r}
                  date={date}
                  people={people}
                  time={time}
                />
              ))}
            </CardScroller>
          </section>
        )}
      </section>
    </main>
  );
}

// Loading component for Suspense fallback
function HomePageLoading() {
  return (
    <main>
      <nav className="w-full border-b bg-white sticky top-0 z-10">
        <div className="max-w-6xl mx-auto flex items-center justify-between h-20 px-4 gap-2">
          <div className="flex items-center gap-3">
            <div className="bg-[#46a758] px-3 py-1 rounded flex items-center h-9">
              <span className="font-bold text-white text-lg">AutoDining</span>
            </div>
          </div>
        </div>
      </nav>
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-10 bg-gray-200 rounded mb-6"></div>
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="h-32 bg-gray-200 rounded mb-4"></div>
          <div className="h-32 bg-gray-200 rounded mb-4"></div>
        </div>
      </div>
    </main>
  );
}

// Main export with Suspense boundary
export default function HomePage() {
  return (
    <Suspense fallback={<HomePageLoading />}>
      <HomePageContent />
    </Suspense>
  );
}
