/**
 * Universal Data Generation Utility
 * 
 * This utility provides consistent data generation across all web projects.
 * It can generate data for different project types (Django, Next.js, etc.)
 * and handle various data structures.
 */


export interface DataGenerationResponse {
  success: boolean;
  data: any[];
  count: number;
  generationTime: number;
  error?: string;
}

export interface ProjectDataConfig {
  projectName: string;
  dataType: string;
  interfaceDefinition: string;
  examples: any[];
  categories: string[];
  namingRules: Record<string, any>;
  additionalRequirements: string;
}

// Project-specific configurations
export const PROJECT_CONFIGS: Record<string, ProjectDataConfig> = {
  'web_4_autodining': {
    projectName: 'AutoDining Restaurants',
    dataType: 'restaurants',
    interfaceDefinition: `
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
    `,
    examples: [
      {
        id: "restaurant-101",
        name: "Juniper & Ash",
        image: "https://images.unsplash.com/photo-1541542684-4a0b3cd7b2f5?w=640&h=480&fit=crop&auto=format&q=60",
        cuisine: "Italian",
        area: "Downtown",
        reviews: 124,
        stars: 4,
        price: "$$$",
        bookings: 23
      }
    ],
    categories: ["International", "Italian", "Japanese", "Mexican", "American", "French", "Mediterranean", "Café", "Thai", "Indian"],
    namingRules: {
      id: "restaurant-{number}",
      image: "https://images.unsplash.com/photo-{random_food_hash}?w=640&h=480&fit=crop&auto=format&q=60"
    },
    additionalRequirements: "Generate realistic restaurant records suitable for a dining/booking site. Ensure 'image' uses Unsplash images related to restaurants/food/interiors and includes size/quality params. Provide balanced 'stars' (3-5), plausible 'reviews' and 'bookings', and common 'price' symbols ($, $$, $$$, $$$$). Prefer distinct 'name' values."
  }
};

/**
 * Generate data for a specific project
 */
export async function generateProjectData(
  projectKey: string,
  count: number = 10,
  categories?: string[]
): Promise<DataGenerationResponse> {
  const config = PROJECT_CONFIGS[projectKey];
  if (!config) {
    return {
      success: false,
      data: [],
      count: 0,
      generationTime: 0,
      error: `Project configuration not found for: ${projectKey}`
    };
  }

  const startTime = Date.now();
  
  try {
    const baseUrl = getApiBaseUrl();
    const response = await fetch(`${baseUrl}/datasets/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        interface_definition: config.interfaceDefinition,
        examples: config.examples,
        count: Math.max(1, Math.min(200, count)),
        categories: categories || config.categories,
        additional_requirements: config.additionalRequirements,
        naming_rules: config.namingRules,
        project_key: projectKey,
        entity_type: config.dataType,
        save_to_db: true,
      })
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    const result = await response.json();
    const generationTime = (Date.now() - startTime) / 1000;

    return {
      success: true,
      data: result.generated_data,
      count: result.count,
      generationTime,
    };
  } catch (error) {
    const generationTime = (Date.now() - startTime) / 1000;
    return {
      success: false,
      data: [],
      count: 0,
      generationTime,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
}


/**
 * Check if data generation is enabled
 */
export function isDataGenerationEnabled(): boolean {
  const raw = (process.env.NEXT_PUBLIC_DATA_GENERATION ??
               process.env.NEXT_ENABLE_DATA_GENERATION ??
               process.env.ENABLE_DATA_GENERATION ??
               '').toString().toLowerCase();
  return raw === 'true' || raw === '1' || raw === 'yes' || raw === 'on';
}

/**
 * Get API base URL
 */
export function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || 
         process.env.API_URL || 
         'http://localhost:8090';
}

