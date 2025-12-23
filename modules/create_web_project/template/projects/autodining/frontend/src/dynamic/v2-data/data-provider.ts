/**
 * V2 Data Loading System for web_4_autodining
 * 
 * Loads different data subsets based on v2 seed.
 */

import { initializeRestaurants, getRestaurants } from '@/data/restaurants-enhanced';

export interface RestaurantData {
  id: string;
  name: string;
  image: string;
  cuisine: string;
  area: string;
  reviews: number;
  stars: number;
  price: string;
  bookings: number;
}

export class DynamicDataProvider {
  private static instance: DynamicDataProvider;
  private restaurants: ReturnType<typeof getRestaurants> = [];
  private isEnabled = false;
  private ready = false;
  private readyPromise: Promise<void>;

  private constructor() {
    this.isEnabled = process.env.NEXT_PUBLIC_ENABLE_DYNAMIC_V2 === 'true';
    if (typeof window === "undefined") {
      this.ready = true;
      this.readyPromise = Promise.resolve();
      return;
    }
    this.readyPromise = this.loadRestaurants();
  }

  public static getInstance(): DynamicDataProvider {
    if (!DynamicDataProvider.instance) {
      DynamicDataProvider.instance = new DynamicDataProvider();
    }
    return DynamicDataProvider.instance;
  }

  private async loadRestaurants(): Promise<void> {
    if (!this.isEnabled) {
      this.ready = true;
      return;
    }

    try {
      const v2Seed = undefined;
      await initializeRestaurants(v2Seed);
      this.restaurants = getRestaurants();
      this.ready = true;
    } catch (error) {
      console.error("[DynamicDataProvider] Failed to load restaurants:", error);
      this.ready = true; // Mark as ready even on error
    }
  }

  public async whenReady(): Promise<void> {
    return this.readyPromise;
  }

  public isReady(): boolean {
    return this.ready;
  }

  public getRestaurants(): RestaurantData[] {
    return this.restaurants.map((r) => ({
      id: r.id,
      name: r.name,
      image: r.image,
      cuisine: r.cuisine ?? "International",
      area: r.area ?? "Downtown",
      reviews: r.reviews ?? 0,
      stars: r.stars ?? 4,
      price: r.price ?? "$$",
      bookings: r.bookings ?? 0,
    }));
  }

  public async reload(seed?: number): Promise<void> {
    if (!this.isEnabled) return;
    
    const v2Seed = seed ?? 1;
    await initializeRestaurants(v2Seed);
    this.restaurants = getRestaurants();
  }

  public isDynamicModeEnabled(): boolean {
    return this.isEnabled;
  }


}

export const dynamicDataProvider = DynamicDataProvider.getInstance();

// Re-export for compatibility
export { initializeRestaurants, getRestaurants };

// Export helper functions
export const isDynamicModeEnabled = () => dynamicDataProvider.isDynamicModeEnabled();
