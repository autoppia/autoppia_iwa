/**
 * V2 Data Loading System
 * 
 * Loads different data subsets based on v2 seed.
 */

export {
  dynamicDataProvider,
  initializeRestaurants,
  getRestaurants,
  isDynamicModeEnabled,
} from "./data-provider";
export type { RestaurantData } from "./data-provider";

// Export whenReady function
export const whenReady = () => dynamicDataProvider.whenReady();
