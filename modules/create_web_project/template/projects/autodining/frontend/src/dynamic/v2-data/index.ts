export {
  dynamicDataProvider,
  getMovies,
  getMovieById,
  getFeaturedMovies,
  getRelatedMovies,
  getMoviesByGenre,
  getAvailableGenres,
  getAvailableYears,
  searchMovies,
  isDynamicModeEnabled,
  getLayoutConfig,
} from "./data-provider";
export type { MovieSearchFilters } from "./data-provider";

// Export whenReady function
export const whenReady = () => dynamicDataProvider.whenReady();
