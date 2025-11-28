import { writeJson, readJson } from "@/shared/storage";

export const countries = [
  { code: "AR", name: "Argentina", dial: "+54", flag: "🇦🇷" },
  { code: "AU", name: "Australia", dial: "+61", flag: "🇦🇺" },
  { code: "BD", name: "Bangladesh", dial: "+880", flag: "🇧🇩" },
  { code: "BR", name: "Brazil", dial: "+55", flag: "🇧🇷" },
  { code: "CA", name: "Canada", dial: "+1", flag: "🇨🇦" },
  { code: "CN", name: "China", dial: "+86", flag: "🇨🇳" },
  { code: "EG", name: "Egypt", dial: "+20", flag: "🇪🇬" },
  { code: "FR", name: "France", dial: "+33", flag: "🇫🇷" },
  { code: "DE", name: "Germany", dial: "+49", flag: "🇩🇪" },
  { code: "IN", name: "India", dial: "+91", flag: "🇮🇳" },
  { code: "ID", name: "Indonesia", dial: "+62", flag: "🇮🇩" },
  { code: "IT", name: "Italy", dial: "+39", flag: "🇮🇹" },
  { code: "JP", name: "Japan", dial: "+81", flag: "🇯🇵" },
  { code: "MX", name: "Mexico", dial: "+52", flag: "🇲🇽" },
  { code: "MY", name: "Malaysia", dial: "+60", flag: "🇲🇾" },
  { code: "NG", name: "Nigeria", dial: "+234", flag: "🇳🇬" },
  { code: "NL", name: "Netherlands", dial: "+31", flag: "🇳🇱" },
  { code: "PK", name: "Pakistan", dial: "+92", flag: "🇵🇰" },
  { code: "PH", name: "Philippines", dial: "+63", flag: "🇵🇭" },
  { code: "PL", name: "Poland", dial: "+48", flag: "🇵🇱" },
  { code: "RU", name: "Russia", dial: "+7", flag: "🇷🇺" },
  { code: "SA", name: "Saudi Arabia", dial: "+966", flag: "🇸🇦" },
  { code: "ZA", name: "South Africa", dial: "+27", flag: "🇿🇦" },
  { code: "KR", name: "South Korea", dial: "+82", flag: "🇰🇷" },
  { code: "ES", name: "Spain", dial: "+34", flag: "🇪🇸" },
  { code: "SE", name: "Sweden", dial: "+46", flag: "🇸🇪" },
  { code: "CH", name: "Switzerland", dial: "+41", flag: "🇨🇭" },
  { code: "TH", name: "Thailand", dial: "+66", flag: "🇹🇭" },
  { code: "TR", name: "Turkey", dial: "+90", flag: "🇹🇷" },
  { code: "AE", name: "United Arab Emirates", dial: "+971", flag: "🇦🇪" },
  { code: "GB", name: "United Kingdom", dial: "+44", flag: "🇬🇧" },
  { code: "US", name: "United States", dial: "+1", flag: "🇺🇸" },
  { code: "VN", name: "Vietnam", dial: "+84", flag: "🇻🇳" },
];

export const RestaurantsData = [
  {
    id: "1",
    country: { code: "AR", name: "Argentina" },
    namepool: "The Royal Dine",
    cuisine: "French",
    area: "Mission District",
    staticReviews: 18,
    staticBookings: 6,
    staticStars: 3,
    staticPrices: "$$",
  },
  {
    id: "2",
    country: { code: "AU", name: "Australia" },
    namepool: "Vintage Bites",
    cuisine: "Italian",
    area: "SOMA",
    staticReviews: 22,
    staticBookings: 12,
    staticStars: 4,
    staticPrices: "$$$",
  },
  {
    id: "3",
    country: { code: "BD", name: "Bangladesh" },
    namepool: "Evening Delight",
    cuisine: "American",
    area: "North Beach",
    staticReviews: 35,
    staticBookings: 17,
    staticStars: 5,
    staticPrices: "$$$$",
  },
  {
    id: "4",
    country: { code: "BR", name: "Brazil" },
    namepool: "River View Café",
    cuisine: "Japanese",
    area: "Downtown",
    staticReviews: 47,
    staticBookings: 23,
    staticStars: 4,
    staticPrices: "$$",
  },
  {
    id: "5",
    country: { code: "CA", name: "Canada" },
    namepool: "Fancy Lights Bistro",
    cuisine: "Mexican",
    area: "Hayes Valley",
    staticReviews: 53,
    staticBookings: 27,
    staticStars: 5,
    staticPrices: "$$$",
  },
  {
    id: "6",
    country: { code: "CN", name: "China" },
    namepool: "Urban Palate",
    cuisine: "Indian",
    area: "Nob Hill",
    staticReviews: 62,
    staticBookings: 32,
    staticStars: 3,
    staticPrices: "$$$$",
  },
  {
    id: "7",
    country: { code: "EG", name: "Egypt" },
    namepool: "Tandoori House",
    cuisine: "Thai",
    area: "Japantown",
    staticReviews: 71,
    staticBookings: 37,
    staticStars: 4,
    staticPrices: "$$",
  },
  {
    id: "8",
    country: { code: "FR", name: "France" },
    namepool: "Zen Sushi",
    cuisine: "Café",
    area: "Embarcadero",
    staticReviews: 28,
    staticBookings: 40,
    staticStars: 5,
    staticPrices: "$$$",
  },
  {
    id: "9",
    country: { code: "DE", name: "Germany" },
    namepool: "El Toro",
    cuisine: "Mediterranean",
    area: "Marina",
    staticReviews: 39,
    staticBookings: 43,
    staticStars: 3,
    staticPrices: "$$$$",
  },
  {
    id: "10",
    country: { code: "IN", name: "India" },
    namepool: "Bella Vita",
    cuisine: "French",
    area: "Mission District",
    staticReviews: 44,
    staticBookings: 50,
    staticStars: 4,
    staticPrices: "$$",
  },
  {
    id: "11",
    country: { code: "ID", name: "Indonesia" },
    namepool: "Coastal Catch",
    cuisine: "Italian",
    area: "SOMA",
    staticReviews: 55,
    staticBookings: 57,
    staticStars: 3,
    staticPrices: "$$$",
  },
  {
    id: "12",
    country: { code: "IT", name: "Italy" },
    namepool: "Harvest Table",
    cuisine: "American",
    area: "North Beach",
    staticReviews: 66,
    staticBookings: 65,
    staticStars: 5,
    staticPrices: "$$$$",
  },
  {
    id: "13",
    country: { code: "JP", name: "Japan" },
    namepool: "Crimson Spoon",
    cuisine: "Japanese",
    area: "Downtown",
    staticReviews: 72,
    staticBookings: 67,
    staticStars: 4,
    staticPrices: "$$",
  },
  {
    id: "14",
    country: { code: "MX", name: "Mexico" },
    namepool: "Golden Lotus",
    cuisine: "Mexican",
    area: "Hayes Valley",
    staticReviews: 80,
    staticBookings: 69,
    staticStars: 5,
    staticPrices: "$$$",
  },
  {
    id: "15",
    country: { code: "MY", name: "Malaysia" },
    namepool: "The Hungry Fork",
    cuisine: "Indian",
    area: "Nob Hill",
    staticReviews: 91,
    staticBookings: 74,
    staticStars: 3,
    staticPrices: "$$$$",
  },
  {
    id: "16",
    country: { code: "NG", name: "Nigeria" },
    namepool: "Ocean's Plate",
    cuisine: "Thai",
    area: "Japantown",
    staticReviews: 24,
    staticBookings: 79,
    staticStars: 4,
    staticPrices: "$$",
  },
  {
    id: "17",
    country: { code: "NL", name: "Netherlands" },
    namepool: "Fire & Spice",
    cuisine: "Café",
    area: "Embarcadero",
    staticReviews: 31,
    staticBookings: 84,
    staticStars: 5,
    staticPrices: "$$$",
  },
  {
    id: "18",
    country: { code: "PK", name: "Pakistan" },
    namepool: "Olive & Vine",
    cuisine: "Mediterranean",
    area: "Marina",
    staticReviews: 42,
    staticBookings: 86,
    staticStars: 3,
    staticPrices: "$$$$",
  },
  {
    id: "19",
    country: { code: "PH", name: "Philippines" },
    namepool: "La Bella Cucina",
    cuisine: "French",
    area: "Mission District",
    staticReviews: 48,
    staticBookings: 89,
    staticStars: 4,
    staticPrices: "$$",
  },
  {
    id: "20",
    country: { code: "PL", name: "Poland" },
    namepool: "Sunset Grill",
    cuisine: "Italian",
    area: "SOMA",
    staticReviews: 60,
    staticBookings: 92,
    staticStars: 5,
    staticPrices: "$$$",
  },
  {
    id: "21",
    country: { code: "RU", name: "Russia" },
    namepool: "Noir Brasserie",
    cuisine: "American",
    area: "North Beach",
    staticReviews: 70,
    staticBookings: 94,
    staticStars: 4,
    staticPrices: "$$$$",
  },
  {
    id: "22",
    country: { code: "SA", name: "Saudi Arabia" },
    namepool: "Blue Orchid",
    cuisine: "Japanese",
    area: "Downtown",
    staticReviews: 15,
    staticBookings: 97,
    staticStars: 5,
    staticPrices: "$$",
  },
  {
    id: "23",
    country: { code: "ZA", name: "South Africa" },
    namepool: "Saffron Garden",
    cuisine: "Mexican",
    area: "Hayes Valley",
    staticReviews: 33,
    staticBookings: 98,
    staticStars: 3,
    staticPrices: "$$$",
  },
  {
    id: "24",
    country: { code: "KR", name: "South Korea" },
    namepool: "Rustic Roots",
    cuisine: "Indian",
    area: "Nob Hill",
    staticReviews: 45,
    staticBookings: 100,
    staticStars: 4,
    staticPrices: "$$$$",
  },
  {
    id: "25",
    country: { code: "ES", name: "Spain" },
    namepool: "Amber Lounge",
    cuisine: "Thai",
    area: "Japantown",
    staticReviews: 59,
    staticBookings: 13,
    staticStars: 5,
    staticPrices: "$$",
  },
  {
    id: "26",
    country: { code: "SE", name: "Sweden" },
    namepool: "Bistro Lumière",
    cuisine: "Café",
    area: "Embarcadero",
    staticReviews: 63,
    staticBookings: 14,
    staticStars: 3,
    staticPrices: "$$$",
  },
  {
    id: "27",
    country: { code: "CH", name: "Switzerland" },
    namepool: "Maple Hearth",
    cuisine: "Mediterranean",
    area: "Marina",
    staticReviews: 76,
    staticBookings: 16,
    staticStars: 4,
    staticPrices: "$$$$",
  },
  {
    id: "28",
    country: { code: "TH", name: "Thailand" },
    namepool: "Oak & Ember",
    cuisine: "French",
    area: "Mission District",
    staticReviews: 81,
    staticBookings: 20,
    staticStars: 5,
    staticPrices: "$$",
  },
  {
    id: "29",
    country: { code: "TR", name: "Turkey" },
    namepool: "Peppercorn Place",
    cuisine: "Italian",
    area: "SOMA",
    staticReviews: 95,
    staticBookings: 21,
    staticStars: 3,
    staticPrices: "$$$",
  },
  {
    id: "30",
    country: { code: "AE", name: "United Arab Emirates" },
    namepool: "The Local Dish",
    cuisine: "American",
    area: "North Beach",
    staticReviews: 38,
    staticBookings: 25,
    staticStars: 4,
    staticPrices: "$$$$",
  },
  {
    id: "31",
    country: { code: "GB", name: "United Kingdom" },
    namepool: "Cedar Grove Café",
    cuisine: "Japanese",
    area: "Downtown",
    staticReviews: 49,
    staticBookings: 30,
    staticStars: 5,
    staticPrices: "$$",
  },
  {
    id: "32",
    country: { code: "US", name: "United States" },
    namepool: "Soleil Bistro",
    cuisine: "Mexican",
    area: "Hayes Valley",
    staticReviews: 51,
    staticBookings: 34,
    staticStars: 4,
    staticPrices: "$$$",
  },
  {
    id: "33",
    country: { code: "VN", name: "Vietnam" },
    namepool: "Brickhouse Eats",
    cuisine: "Indian",
    area: "Nob Hill",
    staticReviews: 58,
    staticBookings: 41,
    staticStars: 5,
    staticPrices: "$$$$",
  },
  {
    id: "34",
    country: { code: "AR", name: "Argentina" },
    namepool: "Wanderlust Grill",
    cuisine: "Thai",
    area: "Japantown",
    staticReviews: 64,
    staticBookings: 52,
    staticStars: 3,
    staticPrices: "$$",
  },
  {
    id: "35",
    country: { code: "AU", name: "Australia" },
    namepool: "The Nest",
    cuisine: "Café",
    area: "Embarcadero",
    staticReviews: 77,
    staticBookings: 56,
    staticStars: 4,
    staticPrices: "$$$",
  },
  {
    id: "36",
    country: { code: "BD", name: "Bangladesh" },
    namepool: "Cafe Verona",
    cuisine: "Mediterranean",
    area: "Marina",
    staticReviews: 82,
    staticBookings: 68,
    staticStars: 5,
    staticPrices: "$$$$",
  },
  {
    id: "37",
    country: { code: "BR", name: "Brazil" },
    namepool: "Midtown Meals",
    cuisine: "French",
    area: "Mission District",
    staticReviews: 87,
    staticBookings: 75,
    staticStars: 3,
    staticPrices: "$$",
  },
  {
    id: "38",
    country: { code: "CA", name: "Canada" },
    namepool: "Ginger & Thyme",
    cuisine: "Italian",
    area: "SOMA",
    staticReviews: 90,
    staticBookings: 78,
    staticStars: 4,
    staticPrices: "$$$",
  },
  {
    id: "39",
    country: { code: "CN", name: "China" },
    namepool: "Lavender & Sage",
    cuisine: "American",
    area: "North Beach",
    staticReviews: 96,
    staticBookings: 83,
    staticStars: 5,
    staticPrices: "$$$$",
  },
  {
    id: "40",
    country: { code: "EG", name: "Egypt" },
    namepool: "Hearthstone Inn",
    cuisine: "Japanese",
    area: "Downtown",
    staticReviews: 99,
    staticBookings: 93,
    staticStars: 4,
    staticPrices: "$$",
  },
  {
    id: "41",
    country: { code: "FR", name: "France" },
    namepool: "Juniper Table",
    cuisine: "Mexican",
    area: "Hayes Valley",
    staticReviews: 19,
    staticBookings: 7,
    staticStars: 3,
    staticPrices: "$$$",
  },
  {
    id: "42",
    country: { code: "DE", name: "Germany" },
    namepool: "The Garden Fork",
    cuisine: "Indian",
    area: "Nob Hill",
    staticReviews: 26,
    staticBookings: 8,
    staticStars: 4,
    staticPrices: "$$$$",
  },
  {
    id: "43",
    country: { code: "IN", name: "India" },
    namepool: "Twilight Tapas",
    cuisine: "Thai",
    area: "Japantown",
    staticReviews: 29,
    staticBookings: 9,
    staticStars: 5,
    staticPrices: "$$",
  },
  {
    id: "44",
    country: { code: "ID", name: "Indonesia" },
    namepool: "Meadow & Moor",
    cuisine: "Café",
    area: "Embarcadero",
    staticReviews: 36,
    staticBookings: 10,
    staticStars: 3,
    staticPrices: "$$$",
  },
  {
    id: "45",
    country: { code: "IT", name: "Italy" },
    namepool: "The Vine",
    cuisine: "Mediterranean",
    area: "Marina",
    staticReviews: 46,
    staticBookings: 11,
    staticStars: 4,
    staticPrices: "$$$$",
  },
  {
    id: "46",
    country: { code: "JP", name: "Japan" },
    namepool: "Ember Flame",
    cuisine: "French",
    area: "Mission District",
    staticReviews: 54,
    staticBookings: 35,
    staticStars: 5,
    staticPrices: "$$",
  },
  {
    id: "47",
    country: { code: "MX", name: "Mexico" },
    namepool: "Miso Modern",
    cuisine: "Italian",
    area: "SOMA",
    staticReviews: 61,
    staticBookings: 38,
    staticStars: 3,
    staticPrices: "$$$",
  },
  {
    id: "48",
    country: { code: "MY", name: "Malaysia" },
    namepool: "The Borough",
    cuisine: "American",
    area: "North Beach",
    staticReviews: 73,
    staticBookings: 60,
    staticStars: 4,
    staticPrices: "$$$$",
  },
  {
    id: "49",
    country: { code: "NG", name: "Nigeria" },
    namepool: "Copper Kitchen",
    cuisine: "Japanese",
    area: "Downtown",
    staticReviews: 85,
    staticBookings: 70,
    staticStars: 5,
    staticPrices: "$$",
  },
  {
    id: "50",
    country: { code: "NL", name: "Netherlands" },
    namepool: "Pine & Poppy",
    cuisine: "Mexican",
    area: "Hayes Valley",
    staticReviews: 88,
    staticBookings: 90,
    staticStars: 4,
    staticPrices: "$$$",
  },
];

export interface RestaurantGenerated {
  id: string;
  name: string;
  image: string;
  cuisine?: string;
  area?: string;
  reviews?: number;
  stars?: number;
  price?: string;
  bookings?: number;
}

// Cache helpers
function readCachedRestaurants(): RestaurantGenerated[] | null {
  if (typeof window === "undefined") return null;
  try {
    const parsed = readJson("autodining_generated_restaurants_v1");
    return Array.isArray(parsed) ? (parsed as RestaurantGenerated[]) : null;
  } catch {
    return null;
  }
}

function writeCachedRestaurants(items: RestaurantGenerated[]): void {
  if (typeof window === "undefined") return;
  writeJson("autodining_generated_restaurants_v1", items);
}

// Normalization
function normalizeRestaurants(items: RestaurantGenerated[]): RestaurantGenerated[] {
  return items.map((r, index) => ({
    id: r.id || `gen-${index + 1}`,
    name: r.name || `Restaurant ${index + 1}`,
    image: r.image?.startsWith("/images/") ? r.image : `/images/restaurant${(index % 19) + 1}.jpg`,
    cuisine: r.cuisine || "International",
    area: r.area || "Downtown",
    reviews: r.reviews ?? 0,
    stars: r.stars ?? 4,
    price: r.price || "$$",
    bookings: r.bookings ?? 0,
  }));
}

export let dynamicRestaurants: RestaurantGenerated[] = [];

export function getRestaurants(): RestaurantGenerated[] {
  return dynamicRestaurants.length > 0
    ? dynamicRestaurants
    : RestaurantsData.map((item, index) => ({
      id: `restaurant-${item.id}`,
      name: item.namepool,
      image: `/images/restaurant${(index % 19) + 1}.jpg`,
      stars: item.staticStars,
      reviews: item.staticReviews,
      cuisine: item.cuisine,
      price: item.staticPrices,
      bookings: item.staticBookings,
      area: item.area,
    }));
}

export async function initializeRestaurants(): Promise<RestaurantGenerated[]> {
  // If DB mode is enabled, skip the local cache so changes take effect immediately
  let skipCache = false;
  try {
    const { isDbLoadModeEnabled } = await import("@/shared/seeded-loader");
    skipCache = isDbLoadModeEnabled();
  } catch {}

  if (!skipCache) {
    // Prefer cache first on client
    const cached = readCachedRestaurants();
    if (cached && cached.length > 0) {
      dynamicRestaurants = normalizeRestaurants(cached);
      return dynamicRestaurants;
    }
  }
  // DB mode check and fetch
  try {
    const { isDbLoadModeEnabled, fetchPoolInfo, fetchSeededSelection, getSeedValueFromEnv } = await import("@/shared/seeded-loader");
    console.log("isDbLoadModeEnabled: ", isDbLoadModeEnabled());
    if (isDbLoadModeEnabled()) {
      const info = await fetchPoolInfo("web_4_autodining", "restaurants");
      let poolSize = info?.pool_size ?? 0;
      // If pool is missing or too small, and DB mode is on, try to auto-generate and save to DB
      if (!info || poolSize < 50) {
        try {
          const { generateProjectData } = await import("@/shared/data-generator");
          const gen = await generateProjectData("web_4_autodining", 100, ["International", "Italian", "Japanese", "Mexican", "American"]);
          console.log("Auto-generated for DB mode:", gen);
        } catch (e) {
          console.warn("[autodining] Auto-generation for DB mode failed:", e);
        }
      }

      // Attempt to load from DB regardless; after possible generation above
      const seed = getSeedValueFromEnv(1);
      const fromDb = await fetchSeededSelection<RestaurantGenerated>({
        projectKey: "web_4_autodining",
        entityType: "restaurants",
        seedValue: seed,
        limit: 100,
        method: "shuffle",
      });
      console.log("Fetched from DB:", fromDb);
      if (fromDb && fromDb.length > 0) {
        dynamicRestaurants = normalizeRestaurants(fromDb);
        writeCachedRestaurants(dynamicRestaurants);
        return dynamicRestaurants;
      }
    }
  } catch (err) {
    console.warn("[autodining] DB load attempt failed:", err);
  }
  // Generation fallback
  try {
    const { isDataGenerationEnabled, generateProjectData } = await import("@/shared/data-generator");
    console.log("isDataGenerationEnabled: ", isDataGenerationEnabled());
    if (isDataGenerationEnabled()) {
      const result = await generateProjectData("web_4_autodining", 60, ["International", "Italian", "Japanese", "Mexican", "American"]);
      console.log("Generated restaurants:", result);
      if (result.success && result.data.length > 0) {
        dynamicRestaurants = normalizeRestaurants(result.data as RestaurantGenerated[]);
        writeCachedRestaurants(dynamicRestaurants);
        return dynamicRestaurants;
      } else {
        console.warn("[autodining] Data generation returned empty or failed; falling back to static dataset.");
        dynamicRestaurants = normalizeRestaurants(
          RestaurantsData.map((item, index) => ({
            id: `restaurant-${item.id}`,
            name: item.namepool,
            image: `/images/restaurant${(index % 19) + 1}.jpg`,
            stars: item.staticStars,
            reviews: item.staticReviews,
            cuisine: item.cuisine,
            price: item.staticPrices,
            bookings: item.staticBookings,
            area: item.area,
          })) as unknown as RestaurantGenerated[]
        );
        writeCachedRestaurants(dynamicRestaurants);
        return dynamicRestaurants;
      }
    }
  } catch (err) {
    console.warn("[autodining] Data generation request failed:", err);
  }
  dynamicRestaurants = [];
  return dynamicRestaurants;
}
