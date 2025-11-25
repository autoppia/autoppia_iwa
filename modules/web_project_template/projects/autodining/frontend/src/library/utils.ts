import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { useState, useEffect } from "react";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Seed-based layout and x-path variation utilities
export interface LayoutVariation {
  className?: string;
  style?: React.CSSProperties;
  dataTestId?: string;
  xpath?: string;
  layoutType?: 'grid' | 'flex' | 'block' | 'inline';
  position?: 'relative' | 'absolute' | 'fixed' | 'sticky';
  order?: number;
  hidden?: boolean;
  wrapper?: boolean;
}

export interface SeedVariations {
  [key: string]: LayoutVariation[];
}

// Event-based layout variations
export interface EventLayoutVariation {
  [eventType: string]: {
    [componentType: string]: LayoutVariation;
  };
}

// Centralized seed-based variation system for confusing scraper agents
// 3 completely different layouts that repeat: Layout A (1,4,7,10), Layout B (2,5,8), Layout C (3,6,9)
// Focus on structural layout changes while keeping all elements visible
export class SeedVariationManager {
  private static variations: SeedVariations = {
    // Restaurant card variations - 3 completely different structural layouts
    restaurantCard: [
      // Layout A: Traditional Flexbox Cards (Seeds 1, 4, 7, 10)
      { 
        className: "rounded-xl border shadow-sm bg-white w-[255px] flex-shrink-0 overflow-hidden flex flex-col justify-between", 
        dataTestId: "restaurant-card-layout-a",
        layoutType: 'flex'
      },
      // Layout B: Grid-based Cards (Seeds 2, 5, 8)
      { 
        className: "rounded-lg border-2 shadow-md bg-gray-50 w-[260px] flex-shrink-0 overflow-hidden grid grid-cols-1 gap-2 p-3", 
        dataTestId: "restaurant-card-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Block-based Cards (Seeds 3, 6, 9)
      { 
        className: "rounded-2xl border shadow-lg bg-white w-[250px] flex-shrink-0 overflow-hidden block p-4", 
        dataTestId: "restaurant-card-layout-c",
        layoutType: 'block'
      },
      // Layout A: Traditional Flexbox Cards (Seeds 1, 4, 7, 10)
      { 
        className: "rounded-xl border shadow-sm bg-white w-[255px] flex-shrink-0 overflow-hidden flex flex-col justify-between", 
        dataTestId: "restaurant-card-layout-a",
        layoutType: 'flex'
      },
      // Layout B: Grid-based Cards (Seeds 2, 5, 8)
      { 
        className: "rounded-lg border-2 shadow-md bg-gray-50 w-[260px] flex-shrink-0 overflow-hidden grid grid-cols-1 gap-2 p-3", 
        dataTestId: "restaurant-card-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Block-based Cards (Seeds 3, 6, 9)
      { 
        className: "rounded-2xl border shadow-lg bg-white w-[250px] flex-shrink-0 overflow-hidden block p-4", 
        dataTestId: "restaurant-card-layout-c",
        layoutType: 'block'
      },
      // Layout A: Traditional Flexbox Cards (Seeds 1, 4, 7, 10)
      { 
        className: "rounded-xl border shadow-sm bg-white w-[255px] flex-shrink-0 overflow-hidden flex flex-col justify-between", 
        dataTestId: "restaurant-card-layout-a",
        layoutType: 'flex'
      },
      // Layout B: Grid-based Cards (Seeds 2, 5, 8)
      { 
        className: "rounded-lg border-2 shadow-md bg-gray-50 w-[260px] flex-shrink-0 overflow-hidden grid grid-cols-1 gap-2 p-3", 
        dataTestId: "restaurant-card-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Block-based Cards (Seeds 3, 6, 9)
      { 
        className: "rounded-2xl border shadow-lg bg-white w-[250px] flex-shrink-0 overflow-hidden block p-4", 
        dataTestId: "restaurant-card-layout-c",
        layoutType: 'block'
      },
      // Layout A: Traditional Flexbox Cards (Seeds 1, 4, 7, 10)
      { 
        className: "rounded-xl border shadow-sm bg-white w-[255px] flex-shrink-0 overflow-hidden flex flex-col justify-between", 
        dataTestId: "restaurant-card-layout-a",
        layoutType: 'flex'
      },
    ],
    
    // Search button variations - 3 different structural positioning with left/right variations
    searchButton: [
      // Layout A: Right side positioned buttons (Seeds 1, 4, 7, 10)
      { 
        className: "px-5 py-2 rounded text-lg bg-[#46a758] text-white hover:bg-[#3d8f4a] ml-2", 
        dataTestId: "search-btn-layout-a-right",
        position: 'relative'
      },
      // Layout B: Left side positioned buttons (Seeds 2, 5, 8)
      { 
        className: "px-6 py-3 rounded-lg text-lg bg-[#46a758] text-white hover:bg-[#3d8f4a] mr-2", 
        dataTestId: "search-btn-layout-b-left",
        position: 'relative'
      },
      // Layout C: Right side relative positioned buttons (Seeds 3, 6, 9)
      { 
        className: "px-4 py-2 rounded-full text-lg bg-[#46a758] text-white hover:bg-[#3d8f4a] relative ml-2", 
        dataTestId: "search-btn-layout-c-right",
        position: 'relative'
      },
      // Layout A: Left side positioned buttons (Seeds 1, 4, 7, 10)
      { 
        className: "px-5 py-2 rounded text-lg bg-[#46a758] text-white hover:bg-[#3d8f4a] mr-2", 
        dataTestId: "search-btn-layout-a-left",
        position: 'relative'
      },
      // Layout B: Right side positioned buttons (Seeds 2, 5, 8)
      { 
        className: "px-6 py-3 rounded-lg text-lg bg-[#46a758] text-white hover:bg-[#3d8f4a] ml-2", 
        dataTestId: "search-btn-layout-b-right",
        position: 'relative'
      },
      // Layout C: Left side relative positioned buttons (Seeds 3, 6, 9)
      { 
        className: "px-4 py-2 rounded-full text-lg bg-[#46a758] text-white hover:bg-[#3d8f4a] relative mr-2", 
        dataTestId: "search-btn-layout-c-left",
        position: 'relative'
      },
      // Layout A: Right side positioned buttons (Seeds 1, 4, 7, 10)
      { 
        className: "px-5 py-2 rounded text-lg bg-[#46a758] text-white hover:bg-[#3d8f4a] ml-2", 
        dataTestId: "search-btn-layout-a-right",
        position: 'relative'
      },
      // Layout B: Left side positioned buttons (Seeds 2, 5, 8)
      { 
        className: "px-6 py-3 rounded-lg text-lg bg-[#46a758] text-white hover:bg-[#3d8f4a] mr-2", 
        dataTestId: "search-btn-layout-b-left",
        position: 'relative'
      },
      // Layout C: Right side relative positioned buttons (Seeds 3, 6, 9)
      { 
        className: "px-4 py-2 rounded-full text-lg bg-[#46a758] text-white hover:bg-[#3d8f4a] relative ml-2", 
        dataTestId: "search-btn-layout-c-right",
        position: 'relative'
      },
      // Layout A: Left side positioned buttons (Seeds 1, 4, 7, 10)
      { 
        className: "px-5 py-2 rounded text-lg bg-[#46a758] text-white hover:bg-[#3d8f4a] mr-2", 
        dataTestId: "search-btn-layout-a-left",
        position: 'relative'
      },
    ],
    
    // Button variations - 3 different structural positioning
    bookButton: [
      // Layout A: Normal positioned buttons (Seeds 1, 4, 7, 10)
      { 
        className: "bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-semibold", 
        dataTestId: "book-btn-layout-a",
        position: 'relative'
      },
      // Layout B: Relative positioned buttons with margin (Seeds 2, 5, 8)
      { 
        className: "bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg relative mt-2 ml-auto font-semibold", 
        dataTestId: "book-btn-layout-b",
        position: 'relative'
      },
      // Layout C: Relative positioned buttons with different styling (Seeds 3, 6, 9)
      { 
        className: "bg-purple-600 hover:bg-purple-700 text-white px-3 py-3 rounded-full relative mt-2 font-semibold", 
        dataTestId: "book-btn-layout-c",
        position: 'relative'
      },
      // Layout A: Normal positioned buttons (Seeds 1, 4, 7, 10)
      { 
        className: "bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-semibold", 
        dataTestId: "book-btn-layout-a",
        position: 'relative'
      },
      // Layout B: Relative positioned buttons with margin (Seeds 2, 5, 8)
      { 
        className: "bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg relative mt-2 ml-auto font-semibold", 
        dataTestId: "book-btn-layout-b",
        position: 'relative'
      },
      // Layout C: Relative positioned buttons with different styling (Seeds 3, 6, 9)
      { 
        className: "bg-purple-600 hover:bg-purple-700 text-white px-3 py-3 rounded-full relative mt-2 font-semibold", 
        dataTestId: "book-btn-layout-c",
        position: 'relative'
      },
      // Layout A: Normal positioned buttons (Seeds 1, 4, 7, 10)
      { 
        className: "bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-semibold", 
        dataTestId: "book-btn-layout-a",
        position: 'relative'
      },
      // Layout B: Relative positioned buttons with margin (Seeds 2, 5, 8)
      { 
        className: "bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg relative mt-2 ml-auto font-semibold", 
        dataTestId: "book-btn-layout-b",
        position: 'relative'
      },
      // Layout C: Relative positioned buttons with different styling (Seeds 3, 6, 9)
      { 
        className: "bg-purple-600 hover:bg-purple-700 text-white px-3 py-3 rounded-full relative mt-2 font-semibold", 
        dataTestId: "book-btn-layout-c",
        position: 'relative'
      },
      // Layout A: Normal positioned buttons (Seeds 1, 4, 7, 10)
      { 
        className: "bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-semibold", 
        dataTestId: "book-btn-layout-a",
        position: 'relative'
      },
    ],
    
    // Search bar variations - 3 different structural layouts
    searchBar: [
      // Layout A: Normal search bar (Seeds 1, 4, 7, 10)
      { 
        className: "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500", 
        dataTestId: "search-bar-layout-a",
        position: 'relative'
      },
      // Layout B: Relative positioned search bar with different styling (Seeds 2, 5, 8)
      { 
        className: "w-full px-6 py-3 border-2 rounded-xl relative focus:outline-none focus:ring-2 focus:ring-green-500", 
        dataTestId: "search-bar-layout-b",
        position: 'relative'
      },
      // Layout C: Relative positioned search bar with compact styling (Seeds 3, 6, 9)
      { 
        className: "w-full px-3 py-2 border rounded-md relative focus:outline-none focus:ring-2 focus:ring-purple-500", 
        dataTestId: "search-bar-layout-c",
        position: 'relative'
      },
      // Layout A: Normal search bar (Seeds 1, 4, 7, 10)
      { 
        className: "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500", 
        dataTestId: "search-bar-layout-a",
        position: 'relative'
      },
      // Layout B: Relative positioned search bar with different styling (Seeds 2, 5, 8)
      { 
        className: "w-full px-6 py-3 border-2 rounded-xl relative focus:outline-none focus:ring-2 focus:ring-green-500", 
        dataTestId: "search-bar-layout-b",
        position: 'relative'
      },
      // Layout C: Relative positioned search bar with compact styling (Seeds 3, 6, 9)
      { 
        className: "w-full px-3 py-2 border rounded-md relative focus:outline-none focus:ring-2 focus:ring-purple-500", 
        dataTestId: "search-bar-layout-c",
        position: 'relative'
      },
      // Layout A: Normal search bar (Seeds 1, 4, 7, 10)
      { 
        className: "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500", 
        dataTestId: "search-bar-layout-a",
        position: 'relative'
      },
      // Layout B: Relative positioned search bar with different styling (Seeds 2, 5, 8)
      { 
        className: "w-full px-6 py-3 border-2 rounded-xl relative focus:outline-none focus:ring-2 focus:ring-green-500", 
        dataTestId: "search-bar-layout-b",
        position: 'relative'
      },
      // Layout C: Relative positioned search bar with compact styling (Seeds 3, 6, 9)
      { 
        className: "w-full px-3 py-2 border rounded-md relative focus:outline-none focus:ring-2 focus:ring-purple-500", 
        dataTestId: "search-bar-layout-c",
        position: 'relative'
      },
      // Layout A: Normal search bar (Seeds 1, 4, 7, 10)
      { 
        className: "w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500", 
        dataTestId: "search-bar-layout-a",
        position: 'relative'
      },
    ],
    
    // Dropdown variations - 3 different structural positioning
    dropdown: [
      // Layout A: Normal dropdown (Seeds 1, 4, 7, 10)
      { 
        className: "absolute z-10 bg-white border rounded-lg shadow-lg p-2", 
        dataTestId: "dropdown-layout-a",
        position: 'absolute'
      },
      // Layout B: Relative dropdown with different styling (Seeds 2, 5, 8)
      { 
        className: "relative z-10 bg-gray-50 border-2 rounded-xl shadow-xl p-3", 
        dataTestId: "dropdown-layout-b",
        position: 'relative'
      },
      // Layout C: Sticky dropdown (Seeds 3, 6, 9)
      { 
        className: "sticky z-10 bg-blue-50 border rounded-md shadow-md top-0 p-2", 
        dataTestId: "dropdown-layout-c",
        position: 'sticky'
      },
      // Layout A: Normal dropdown (Seeds 1, 4, 7, 10)
      { 
        className: "absolute z-10 bg-white border rounded-lg shadow-lg p-2", 
        dataTestId: "dropdown-layout-a",
        position: 'absolute'
      },
      // Layout B: Relative dropdown with different styling (Seeds 2, 5, 8)
      { 
        className: "relative z-10 bg-gray-50 border-2 rounded-xl shadow-xl p-3", 
        dataTestId: "dropdown-layout-b",
        position: 'relative'
      },
      // Layout C: Sticky dropdown (Seeds 3, 6, 9)
      { 
        className: "sticky z-10 bg-blue-50 border rounded-md shadow-md top-0 p-2", 
        dataTestId: "dropdown-layout-c",
        position: 'sticky'
      },
      // Layout A: Normal dropdown (Seeds 1, 4, 7, 10)
      { 
        className: "absolute z-10 bg-white border rounded-lg shadow-lg p-2", 
        dataTestId: "dropdown-layout-a",
        position: 'absolute'
      },
      // Layout B: Relative dropdown with different styling (Seeds 2, 5, 8)
      { 
        className: "relative z-10 bg-gray-50 border-2 rounded-xl shadow-xl p-3", 
        dataTestId: "dropdown-layout-b",
        position: 'relative'
      },
      // Layout C: Sticky dropdown (Seeds 3, 6, 9)
      { 
        className: "sticky z-10 bg-blue-50 border rounded-md shadow-md top-0 p-2", 
        dataTestId: "dropdown-layout-c",
        position: 'sticky'
      },
      // Layout A: Normal dropdown (Seeds 1, 4, 7, 10)
      { 
        className: "absolute z-10 bg-white border rounded-lg shadow-lg p-2", 
        dataTestId: "dropdown-layout-a",
        position: 'absolute'
      },
    ],
    
    // Header variations - 3 different structural layouts
    header: [
      // Layout A: Normal header (Seeds 1, 4, 7, 10)
      { 
        className: "bg-white shadow-sm border-b flex items-center justify-between", 
        dataTestId: "header-layout-a",
        layoutType: 'flex'
      },
      // Layout B: Grid header (Seeds 2, 5, 8)
      { 
        className: "bg-gray-50 shadow-md border-b-2 grid grid-cols-2 gap-4", 
        dataTestId: "header-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Block header (Seeds 3, 6, 9)
      { 
        className: "bg-blue-50 shadow-lg border-b block", 
        dataTestId: "header-layout-c",
        layoutType: 'block'
      },
      // Layout A: Normal header (Seeds 1, 4, 7, 10)
      { 
        className: "bg-white shadow-sm border-b flex items-center justify-between", 
        dataTestId: "header-layout-a",
        layoutType: 'flex'
      },
      // Layout B: Grid header (Seeds 2, 5, 8)
      { 
        className: "bg-gray-50 shadow-md border-b-2 grid grid-cols-2 gap-4", 
        dataTestId: "header-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Block header (Seeds 3, 6, 9)
      { 
        className: "bg-blue-50 shadow-lg border-b block", 
        dataTestId: "header-layout-c",
        layoutType: 'block'
      },
      // Layout A: Normal header (Seeds 1, 4, 7, 10)
      { 
        className: "bg-white shadow-sm border-b flex items-center justify-between", 
        dataTestId: "header-layout-a",
        layoutType: 'flex'
      },
      // Layout B: Grid header (Seeds 2, 5, 8)
      { 
        className: "bg-gray-50 shadow-md border-b-2 grid grid-cols-2 gap-4", 
        dataTestId: "header-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Block header (Seeds 3, 6, 9)
      { 
        className: "bg-blue-50 shadow-lg border-b block", 
        dataTestId: "header-layout-c",
        layoutType: 'block'
      },
      // Layout A: Normal header (Seeds 1, 4, 7, 10)
      { 
        className: "bg-white shadow-sm border-b flex items-center justify-between", 
        dataTestId: "header-layout-a",
        layoutType: 'flex'
      },
    ],
    
    // Navigation variations - 3 different structural layouts
    navigation: [
      // Layout A: Horizontal flex (Seeds 1, 4, 7, 10)
      { 
        className: "flex space-x-4 items-center", 
        dataTestId: "nav-layout-a",
        layoutType: 'flex'
      },
      // Layout B: Grid navigation (Seeds 2, 5, 8)
      { 
        className: "grid grid-cols-2 gap-6 items-center", 
        dataTestId: "nav-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Block navigation (Seeds 3, 6, 9)
      { 
        className: "block space-y-2", 
        dataTestId: "nav-layout-c",
        layoutType: 'block'
      },
      // Layout A: Horizontal flex (Seeds 1, 4, 7, 10)
      { 
        className: "flex space-x-4 items-center", 
        dataTestId: "nav-layout-a",
        layoutType: 'flex'
      },
      // Layout B: Grid navigation (Seeds 2, 5, 8)
      { 
        className: "grid grid-cols-2 gap-6 items-center", 
        dataTestId: "nav-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Block navigation (Seeds 3, 6, 9)
      { 
        className: "block space-y-2", 
        dataTestId: "nav-layout-c",
        layoutType: 'block'
      },
      // Layout A: Horizontal flex (Seeds 1, 4, 7, 10)
      { 
        className: "flex space-x-4 items-center", 
        dataTestId: "nav-layout-a",
        layoutType: 'flex'
      },
      // Layout B: Grid navigation (Seeds 2, 5, 8)
      { 
        className: "grid grid-cols-2 gap-6 items-center", 
        dataTestId: "nav-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Block navigation (Seeds 3, 6, 9)
      { 
        className: "block space-y-2", 
        dataTestId: "nav-layout-c",
        layoutType: 'block'
      },
      // Layout A: Horizontal flex (Seeds 1, 4, 7, 10)
      { 
        className: "flex space-x-4 items-center", 
        dataTestId: "nav-layout-a",
        layoutType: 'flex'
      },
    ],
    
    // Form variations - 3 different structural layouts
    form: [
      // Layout A: Vertical stack (Seeds 1, 4, 7, 10)
      { 
        className: "space-y-4", 
        dataTestId: "form-layout-a",
        layoutType: 'block'
      },
      // Layout B: Grid form (Seeds 2, 5, 8)
      { 
        className: "grid grid-cols-2 gap-6", 
        dataTestId: "form-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Horizontal flex (Seeds 3, 6, 9)
      { 
        className: "flex flex-row space-x-3", 
        dataTestId: "form-layout-c",
        layoutType: 'flex'
      },
      // Layout A: Vertical stack (Seeds 1, 4, 7, 10)
      { 
        className: "space-y-4", 
        dataTestId: "form-layout-a",
        layoutType: 'block'
      },
      // Layout B: Grid form (Seeds 2, 5, 8)
      { 
        className: "grid grid-cols-2 gap-6", 
        dataTestId: "form-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Horizontal flex (Seeds 3, 6, 9)
      { 
        className: "flex flex-row space-x-3", 
        dataTestId: "form-layout-c",
        layoutType: 'flex'
      },
      // Layout A: Vertical stack (Seeds 1, 4, 7, 10)
      { 
        className: "space-y-4", 
        dataTestId: "form-layout-a",
        layoutType: 'block'
      },
      // Layout B: Grid form (Seeds 2, 5, 8)
      { 
        className: "grid grid-cols-2 gap-6", 
        dataTestId: "form-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Horizontal flex (Seeds 3, 6, 9)
      { 
        className: "flex flex-row space-x-3", 
        dataTestId: "form-layout-c",
        layoutType: 'flex'
      },
      // Layout A: Vertical stack (Seeds 1, 4, 7, 10)
      { 
        className: "space-y-4", 
        dataTestId: "form-layout-a",
        layoutType: 'block'
      },
    ],

    // Card container variations - 3 different structural layouts
    cardContainer: [
      // Layout A: Horizontal scroll (Seeds 1, 4, 7, 10)
      { 
        className: "flex overflow-x-auto gap-4", 
        dataTestId: "card-container-layout-a",
        layoutType: 'flex'
      },
      // Layout B: Grid container (Seeds 2, 5, 8)
      { 
        className: "grid grid-cols-2 gap-4 overflow-y-auto", 
        dataTestId: "card-container-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Vertical stack (Seeds 3, 6, 9)
      { 
        className: "block space-y-4", 
        dataTestId: "card-container-layout-c",
        layoutType: 'block'
      },
      // Layout A: Horizontal scroll (Seeds 1, 4, 7, 10)
      { 
        className: "flex overflow-x-auto gap-4", 
        dataTestId: "card-container-layout-a",
        layoutType: 'flex'
      },
      // Layout B: Grid container (Seeds 2, 5, 8)
      { 
        className: "grid grid-cols-2 gap-4 overflow-y-auto", 
        dataTestId: "card-container-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Vertical stack (Seeds 3, 6, 9)
      { 
        className: "block space-y-4", 
        dataTestId: "card-container-layout-c",
        layoutType: 'block'
      },
      // Layout A: Horizontal scroll (Seeds 1, 4, 7, 10)
      { 
        className: "flex overflow-x-auto gap-4", 
        dataTestId: "card-container-layout-a",
        layoutType: 'flex'
      },
      // Layout B: Grid container (Seeds 2, 5, 8)
      { 
        className: "grid grid-cols-2 gap-4 overflow-y-auto", 
        dataTestId: "card-container-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Vertical stack (Seeds 3, 6, 9)
      { 
        className: "block space-y-4", 
        dataTestId: "card-container-layout-c",
        layoutType: 'block'
      },
      // Layout A: Horizontal scroll (Seeds 1, 4, 7, 10)
      { 
        className: "flex overflow-x-auto gap-4", 
        dataTestId: "card-container-layout-a",
        layoutType: 'flex'
      },
    ],

    // Image container variations - 3 different structural styles
    imageContainer: [
      // Layout A: Normal images (Seeds 1, 4, 7, 10)
      { 
        className: "w-full h-[140px] object-cover rounded-t-xl border-b cursor-pointer hover:opacity-90 transition", 
        dataTestId: "image-container-layout-a"
      },
      // Layout B: Relative positioned images with different styling (Seeds 2, 5, 8)
      { 
        className: "w-full h-[160px] object-cover rounded-lg border-2 cursor-pointer hover:opacity-90 transition relative", 
        dataTestId: "image-container-layout-b",
        position: 'relative'
      },
      // Layout C: Relative positioned images with compact styling (Seeds 3, 6, 9)
      { 
        className: "w-full h-[120px] object-cover rounded-2xl border cursor-pointer hover:opacity-90 transition relative", 
        dataTestId: "image-container-layout-c",
        position: 'relative'
      },
      // Layout A: Normal images (Seeds 1, 4, 7, 10)
      { 
        className: "w-full h-[140px] object-cover rounded-t-xl border-b cursor-pointer hover:opacity-90 transition", 
        dataTestId: "image-container-layout-a"
      },
      // Layout B: Relative positioned images with different styling (Seeds 2, 5, 8)
      { 
        className: "w-full h-[160px] object-cover rounded-lg border-2 cursor-pointer hover:opacity-90 transition relative", 
        dataTestId: "image-container-layout-b",
        position: 'relative'
      },
      // Layout C: Relative positioned images with compact styling (Seeds 3, 6, 9)
      { 
        className: "w-full h-[120px] object-cover rounded-2xl border cursor-pointer hover:opacity-90 transition relative", 
        dataTestId: "image-container-layout-c",
        position: 'relative'
      },
      // Layout A: Normal images (Seeds 1, 4, 7, 10)
      { 
        className: "w-full h-[140px] object-cover rounded-t-xl border-b cursor-pointer hover:opacity-90 transition", 
        dataTestId: "image-container-layout-a"
      },
      // Layout B: Relative positioned images with different styling (Seeds 2, 5, 8)
      { 
        className: "w-full h-[160px] object-cover rounded-lg border-2 cursor-pointer hover:opacity-90 transition relative", 
        dataTestId: "image-container-layout-b",
        position: 'relative'
      },
      // Layout C: Relative positioned images with compact styling (Seeds 3, 6, 9)
      { 
        className: "w-full h-[120px] object-cover rounded-2xl border cursor-pointer hover:opacity-90 transition relative", 
        dataTestId: "image-container-layout-c",
        position: 'relative'
      },
      // Layout A: Normal images (Seeds 1, 4, 7, 10)
      { 
        className: "w-full h-[140px] object-cover rounded-t-xl border-b cursor-pointer hover:opacity-90 transition", 
        dataTestId: "image-container-layout-a"
      },
    ],

    // Page layout variations - 3 different structural layouts
    pageLayout: [
      // Layout A: Traditional layout (Seeds 1, 4, 7, 10)
      { 
        className: "max-w-6xl mx-auto px-4 py-8", 
        dataTestId: "page-layout-a",
        layoutType: 'block'
      },
      // Layout B: Grid-based layout (Seeds 2, 5, 8)
      { 
        className: "max-w-7xl mx-auto px-6 py-10 grid grid-cols-1 gap-8", 
        dataTestId: "page-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Flex-based layout (Seeds 3, 6, 9)
      { 
        className: "max-w-5xl mx-auto px-3 py-6 flex flex-col space-y-6", 
        dataTestId: "page-layout-c",
        layoutType: 'flex'
      },
      // Layout A: Traditional layout (Seeds 1, 4, 7, 10)
      { 
        className: "max-w-6xl mx-auto px-4 py-8", 
        dataTestId: "page-layout-a",
        layoutType: 'block'
      },
      // Layout B: Grid-based layout (Seeds 2, 5, 8)
      { 
        className: "max-w-7xl mx-auto px-6 py-10 grid grid-cols-1 gap-8", 
        dataTestId: "page-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Flex-based layout (Seeds 3, 6, 9)
      { 
        className: "max-w-5xl mx-auto px-3 py-6 flex flex-col space-y-6", 
        dataTestId: "page-layout-c",
        layoutType: 'flex'
      },
      // Layout A: Traditional layout (Seeds 1, 4, 7, 10)
      { 
        className: "max-w-6xl mx-auto px-4 py-8", 
        dataTestId: "page-layout-a",
        layoutType: 'block'
      },
      // Layout B: Grid-based layout (Seeds 2, 5, 8)
      { 
        className: "max-w-7xl mx-auto px-6 py-10 grid grid-cols-1 gap-8", 
        dataTestId: "page-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Flex-based layout (Seeds 3, 6, 9)
      { 
        className: "max-w-5xl mx-auto px-3 py-6 flex flex-col space-y-6", 
        dataTestId: "page-layout-c",
        layoutType: 'flex'
      },
      // Layout A: Traditional layout (Seeds 1, 4, 7, 10)
      { 
        className: "max-w-6xl mx-auto px-4 py-8", 
        dataTestId: "page-layout-a",
        layoutType: 'block'
      },
    ],

    // Section layout variations - 3 different structural layouts
    sectionLayout: [
      // Layout A: Traditional sections (Seeds 1, 4, 7, 10)
      { 
        className: "mb-8", 
        dataTestId: "section-layout-a",
        layoutType: 'block'
      },
      // Layout B: Grid sections (Seeds 2, 5, 8)
      { 
        className: "grid grid-cols-1 gap-6 mb-10", 
        dataTestId: "section-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Flex sections (Seeds 3, 6, 9)
      { 
        className: "flex flex-col space-y-4 mb-6", 
        dataTestId: "section-layout-c",
        layoutType: 'flex'
      },
      // Layout A: Traditional sections (Seeds 1, 4, 7, 10)
      { 
        className: "mb-8", 
        dataTestId: "section-layout-a",
        layoutType: 'block'
      },
      // Layout B: Grid sections (Seeds 2, 5, 8)
      { 
        className: "grid grid-cols-1 gap-6 mb-10", 
        dataTestId: "section-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Flex sections (Seeds 3, 6, 9)
      { 
        className: "flex flex-col space-y-4 mb-6", 
        dataTestId: "section-layout-c",
        layoutType: 'flex'
      },
      // Layout A: Traditional sections (Seeds 1, 4, 7, 10)
      { 
        className: "mb-8", 
        dataTestId: "section-layout-a",
        layoutType: 'block'
      },
      // Layout B: Grid sections (Seeds 2, 5, 8)
      { 
        className: "grid grid-cols-1 gap-6 mb-10", 
        dataTestId: "section-layout-b",
        layoutType: 'grid'
      },
      // Layout C: Flex sections (Seeds 3, 6, 9)
      { 
        className: "flex flex-col space-y-4 mb-6", 
        dataTestId: "section-layout-c",
        layoutType: 'flex'
      },
      // Layout A: Traditional sections (Seeds 1, 4, 7, 10)
      { 
        className: "mb-8", 
        dataTestId: "section-layout-a",
        layoutType: 'block'
      },
    ],
  };

  // Event-based layout variations - these override seed-based variations when events occur
  // Focus on structural changes rather than visibility changes
  private static eventVariations: EventLayoutVariation = {
    "SEARCH_RESTAURANT": {
      "searchBar": {
        className: "w-full px-6 py-3 border-2 rounded-xl bg-yellow-50 focus:outline-none focus:ring-2 focus:ring-yellow-500",
        dataTestId: "search-bar-event-active",
        position: 'relative'
      },
      "searchButton": {
        className: "px-6 py-3 rounded-xl text-lg bg-yellow-600 text-white hover:bg-yellow-700 animate-pulse",
        dataTestId: "search-btn-event-active",
        position: 'relative'
      },
      "restaurantCard": {
        className: "rounded-xl border-2 shadow-lg bg-yellow-50 w-[255px] flex-shrink-0 overflow-hidden flex flex-col justify-between",
        dataTestId: "restaurant-card-event-active",
        layoutType: 'flex'
      },
      "pageLayout": {
        className: "max-w-6xl mx-auto px-4 py-8 bg-yellow-50",
        dataTestId: "page-layout-search-active",
        layoutType: 'block'
      },
      "cardContainer": {
        className: "flex overflow-x-auto gap-4 bg-yellow-100 p-2 rounded-lg",
        dataTestId: "card-container-search-active",
        layoutType: 'flex'
      }
    },
    "VIEW_RESTAURANT": {
      "restaurantCard": {
        className: "rounded-xl border-2 shadow-xl bg-blue-50 w-[255px] flex-shrink-0 overflow-hidden flex flex-col justify-between",
        dataTestId: "restaurant-card-viewed",
        layoutType: 'flex'
      },
      "bookButton": {
        className: "bg-blue-800 hover:bg-blue-900 text-white px-6 py-3 rounded-lg font-bold",
        dataTestId: "book-btn-viewed",
        position: 'relative'
      },
      "pageLayout": {
        className: "max-w-6xl mx-auto px-4 py-8 bg-blue-50",
        dataTestId: "page-layout-view-active",
        layoutType: 'block'
      },
      "sectionLayout": {
        className: "mb-8 bg-blue-100 p-4 rounded-lg",
        dataTestId: "section-layout-view-active",
        layoutType: 'block'
      }
    },
    "BOOK_RESTAURANT": {
      "bookButton": {
        className: "bg-green-800 hover:bg-green-900 text-white px-8 py-3 rounded-xl font-bold animate-pulse",
        dataTestId: "book-btn-booking",
        position: 'relative'
      },
      "restaurantCard": {
        className: "rounded-xl border-2 shadow-xl bg-green-50 w-[255px] flex-shrink-0 overflow-hidden flex flex-col justify-between",
        dataTestId: "restaurant-card-booking",
        layoutType: 'flex'
      },
      "pageLayout": {
        className: "max-w-6xl mx-auto px-4 py-8 bg-green-50",
        dataTestId: "page-layout-booking-active",
        layoutType: 'block'
      },
      "sectionLayout": {
        className: "mb-8 bg-green-100 p-4 rounded-lg",
        dataTestId: "section-layout-booking-active",
        layoutType: 'block'
      }
    },
    "TIME_DROPDOWN_OPENED": {
      "dropdown": {
        className: "absolute z-20 bg-orange-50 border-2 rounded-xl shadow-xl p-3",
        dataTestId: "dropdown-time-active",
        position: 'absolute'
      },
      "searchBar": {
        className: "w-full px-4 py-2 border-2 rounded-lg bg-orange-50 focus:outline-none focus:ring-2 focus:ring-orange-500",
        dataTestId: "search-bar-time-dropdown-active",
        position: 'relative'
      },
      "searchButton": {
        className: "px-5 py-2 rounded-lg text-lg bg-orange-600 text-white hover:bg-orange-700",
        dataTestId: "search-btn-time-dropdown-active",
        position: 'relative'
      },
      "pageLayout": {
        className: "max-w-6xl mx-auto px-4 py-8 bg-orange-50",
        dataTestId: "page-layout-time-dropdown-active",
        layoutType: 'block'
      }
    },
    "DATE_DROPDOWN_OPENED": {
      "dropdown": {
        className: "absolute z-20 bg-purple-50 border-2 rounded-xl shadow-xl p-3",
        dataTestId: "dropdown-date-active",
        position: 'absolute'
      },
      "searchBar": {
        className: "w-full px-4 py-2 border-2 rounded-lg bg-purple-50 focus:outline-none focus:ring-2 focus:ring-purple-500",
        dataTestId: "search-bar-date-dropdown-active",
        position: 'relative'
      },
      "searchButton": {
        className: "px-5 py-2 rounded-lg text-lg bg-purple-600 text-white hover:bg-purple-700",
        dataTestId: "search-btn-date-dropdown-active",
        position: 'relative'
      },
      "pageLayout": {
        className: "max-w-6xl mx-auto px-4 py-8 bg-purple-50",
        dataTestId: "page-layout-date-dropdown-active",
        layoutType: 'block'
      }
    },
    "PEOPLE_DROPDOWN_OPENED": {
      "dropdown": {
        className: "absolute z-20 bg-pink-50 border-2 rounded-xl shadow-xl p-3",
        dataTestId: "dropdown-people-active",
        position: 'absolute'
      },
      "searchBar": {
        className: "w-full px-4 py-2 border-2 rounded-lg bg-pink-50 focus:outline-none focus:ring-2 focus:ring-pink-500",
        dataTestId: "search-bar-people-dropdown-active",
        position: 'relative'
      },
      "searchButton": {
        className: "px-5 py-2 rounded-lg text-lg bg-pink-600 text-white hover:bg-pink-700",
        dataTestId: "search-btn-people-dropdown-active",
        position: 'relative'
      },
      "pageLayout": {
        className: "max-w-6xl mx-auto px-4 py-8 bg-pink-50",
        dataTestId: "page-layout-people-dropdown-active",
        layoutType: 'block'
      }
    },
    "SCROLL_VIEW": {
      "cardContainer": {
        className: "flex overflow-x-auto gap-4 bg-gray-50 p-2 rounded-lg",
        dataTestId: "card-container-scrolling",
        layoutType: 'flex'
      },
      "restaurantCard": {
        className: "rounded-xl border-2 shadow-lg bg-gray-100 w-[255px] flex-shrink-0 overflow-hidden flex flex-col justify-between",
        dataTestId: "restaurant-card-scrolling",
        layoutType: 'flex'
      },
      "pageLayout": {
        className: "max-w-6xl mx-auto px-4 py-8 bg-gray-50",
        dataTestId: "page-layout-scrolling",
        layoutType: 'block'
      }
    },
    "COUNTRY_SELECTED": {
      "form": {
        className: "space-y-4 bg-blue-50 p-4 rounded-lg",
        dataTestId: "form-country-selected",
        layoutType: 'block'
      },
      "searchBar": {
        className: "w-full px-4 py-2 border-2 rounded-lg bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500",
        dataTestId: "search-bar-country-selected",
        position: 'relative'
      },
      "pageLayout": {
        className: "max-w-6xl mx-auto px-4 py-8 bg-blue-50",
        dataTestId: "page-layout-country-selected",
        layoutType: 'block'
      },
      "sectionLayout": {
        className: "mb-8 bg-blue-100 p-4 rounded-lg",
        dataTestId: "section-layout-country-selected",
        layoutType: 'block'
      }
    },
    "OCCASION_SELECTED": {
      "form": {
        className: "space-y-4 bg-green-50 p-4 rounded-lg",
        dataTestId: "form-occasion-selected",
        layoutType: 'block'
      },
      "searchBar": {
        className: "w-full px-4 py-2 border-2 rounded-lg bg-green-50 focus:outline-none focus:ring-2 focus:ring-green-500",
        dataTestId: "search-bar-occasion-selected",
        position: 'relative'
      },
      "pageLayout": {
        className: "max-w-6xl mx-auto px-4 py-8 bg-green-50",
        dataTestId: "page-layout-occasion-selected",
        layoutType: 'block'
      },
      "sectionLayout": {
        className: "mb-8 bg-green-100 p-4 rounded-lg",
        dataTestId: "section-layout-occasion-selected",
        layoutType: 'block'
      }
    },
    "RESERVATION_COMPLETE": {
      "bookButton": {
        className: "bg-purple-800 hover:bg-purple-900 text-white px-8 py-3 rounded-xl font-bold",
        dataTestId: "book-btn-complete",
        position: 'relative'
      },
      "form": {
        className: "space-y-4 bg-purple-50 p-4 rounded-lg",
        dataTestId: "form-complete",
        layoutType: 'block'
      },
      "restaurantCard": {
        className: "rounded-xl border-2 shadow-xl bg-purple-50 w-[255px] flex-shrink-0 overflow-hidden flex flex-col justify-between",
        dataTestId: "restaurant-card-complete",
        layoutType: 'flex'
      },
      "pageLayout": {
        className: "max-w-6xl mx-auto px-4 py-8 bg-purple-50",
        dataTestId: "page-layout-reservation-complete",
        layoutType: 'block'
      },
      "sectionLayout": {
        className: "mb-8 bg-purple-100 p-4 rounded-lg",
        dataTestId: "section-layout-reservation-complete",
        layoutType: 'block'
      }
    },
    "VIEW_FULL_MENU": {
      "restaurantCard": {
        className: "rounded-xl border-2 shadow-xl bg-indigo-50 w-[255px] flex-shrink-0 overflow-hidden flex flex-col justify-between",
        dataTestId: "restaurant-card-menu-viewed",
        layoutType: 'flex'
      },
      "bookButton": {
        className: "bg-indigo-800 hover:bg-indigo-900 text-white px-6 py-3 rounded-lg font-bold",
        dataTestId: "book-btn-menu-viewed",
        position: 'relative'
      },
      "pageLayout": {
        className: "max-w-6xl mx-auto px-4 py-8 bg-indigo-50",
        dataTestId: "page-layout-menu-viewed",
        layoutType: 'block'
      },
      "sectionLayout": {
        className: "mb-8 bg-indigo-100 p-4 rounded-lg",
        dataTestId: "section-layout-menu-viewed",
        layoutType: 'block'
      }
    },
    "COLLAPSE_MENU": {
      "restaurantCard": {
        className: "rounded-xl border shadow-sm bg-white w-[255px] flex-shrink-0 overflow-hidden flex flex-col justify-between",
        dataTestId: "restaurant-card-menu-collapsed",
        layoutType: 'flex'
      },
      "bookButton": {
        className: "bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded font-semibold",
        dataTestId: "book-btn-menu-collapsed",
        position: 'relative'
      },
      "pageLayout": {
        className: "max-w-6xl mx-auto px-4 py-8 bg-white",
        dataTestId: "page-layout-menu-collapsed",
        layoutType: 'block'
      },
      "sectionLayout": {
        className: "mb-8 bg-white p-4 rounded-lg",
        dataTestId: "section-layout-menu-collapsed",
        layoutType: 'block'
      }
    }
  };

  // Track active events
  private static activeEvents: Set<string> = new Set();

  // Method to register an event
  static registerEvent(eventType: string) {
    this.activeEvents.add(eventType);
    // Auto-remove event after 5 seconds
    setTimeout(() => {
      this.activeEvents.delete(eventType);
    }, 5000);
  }

  // Method to clear all events
  static clearEvents() {
    this.activeEvents.clear();
  }

  // Method to get active events
  static getActiveEvents(): string[] {
    return Array.from(this.activeEvents);
  }

  static getVariation(type: keyof SeedVariations, seed: number, eventType?: string): LayoutVariation {
    // First check if there's an event-based variation
    if (eventType && this.eventVariations[eventType] && this.eventVariations[eventType][type]) {
      return this.eventVariations[eventType][type];
    }

    // Check if any active events should override the layout
    for (const activeEvent of this.activeEvents) {
      if (this.eventVariations[activeEvent] && this.eventVariations[activeEvent][type]) {
        return this.eventVariations[activeEvent][type];
      }
    }

    // Fall back to seed-based variation
    const variations = this.variations[type];
    if (!variations) {
      return {};
    }
    
    // Map seed to layout index (1-4) using ceil(seed/30)
    const layoutIndex = getLayoutIndexFromSeed(seed);
    // Convert to 0-based index and ensure we don't exceed available variations
    const variationIndex = Math.min(layoutIndex - 1, variations.length - 1);
    return variations[variationIndex] || variations[0];
  }

  static getXPath(type: keyof SeedVariations, seed: number, eventType?: string): string {
    const variation = this.getVariation(type, seed, eventType);
    return variation.xpath || `//*[@data-testid="${variation.dataTestId}"]`;
  }

  static getClassName(type: keyof SeedVariations, seed: number, eventType?: string): string {
    const variation = this.getVariation(type, seed, eventType);
    return variation.className || "";
  }

  static getDataTestId(type: keyof SeedVariations, seed: number, eventType?: string): string {
    const variation = this.getVariation(type, seed, eventType);
    return variation.dataTestId || `${type}-${seed}`;
  }

  static getStyle(type: keyof SeedVariations, seed: number, eventType?: string): React.CSSProperties {
    const variation = this.getVariation(type, seed, eventType);
    return variation.style || {};
  }

  static getLayoutType(type: keyof SeedVariations, seed: number, eventType?: string): string {
    const variation = this.getVariation(type, seed, eventType);
    return variation.layoutType || 'flex';
  }

  static getPosition(type: keyof SeedVariations, seed: number, eventType?: string): string {
    const variation = this.getVariation(type, seed, eventType);
    return variation.position || 'relative';
  }
}

// Helper function to check if dynamic HTML is enabled
export function isDynamicModeEnabled(): boolean {
  return process.env.NEXT_PUBLIC_ENABLE_DYNAMIC_HTML === 'true';
}

// Helper function to map seed to layout index (1-10)
export function getLayoutIndexFromSeed(seed: number): number {
  if (seed < 1 || seed > 300) return 1; // fallback
  const bucket = seed % 30 || 30;  // gives 1–30
  const layoutId = ((bucket - 1) % 10) + 1; // cycles into 1–10
  return layoutId;
}

// Helper function to get seed from URL
export function getSeedFromUrl(): number {
  if (typeof window === 'undefined') return 1;
  
  // If dynamic HTML is disabled, always return seed 1 (static mode)
  if (!isDynamicModeEnabled()) {
    return 1;
  }
  
  const urlParams = new URLSearchParams(window.location.search);
  const seedParam = urlParams.get('seed');
  const seed = parseInt(seedParam || '1', 10);
  
  // Ensure seed is between 1-300
  return Math.max(1, Math.min(300, seed));
}

// Helper function to get seed from URL with fallback
export function getSeedFromUrlWithFallback(fallback: number = 1): number {
  if (typeof window === 'undefined') return fallback;
  
  // If dynamic HTML is disabled, always return seed 1 (static mode)
  if (!isDynamicModeEnabled()) {
    return 1;
  }
  
  const urlParams = new URLSearchParams(window.location.search);
  const seedParam = urlParams.get('seed');
  const seed = parseInt(seedParam || fallback.toString(), 10);
  
  // Ensure seed is between 1-300
  return Math.max(1, Math.min(300, seed));
}

// Hook for using seed-based variations with event support
export function useSeedVariation(type: keyof SeedVariations, eventType?: string) {
  const [seed, setSeed] = useState(1);
  
  useEffect(() => {
    setSeed(getSeedFromUrl());
  }, []);
  
  return {
    className: SeedVariationManager.getClassName(type, seed, eventType),
    style: SeedVariationManager.getStyle(type, seed, eventType),
    dataTestId: SeedVariationManager.getDataTestId(type, seed, eventType),
    xpath: SeedVariationManager.getXPath(type, seed, eventType),
    layoutType: SeedVariationManager.getLayoutType(type, seed, eventType),
    position: SeedVariationManager.getPosition(type, seed, eventType),
    seed,
    activeEvents: SeedVariationManager.getActiveEvents(),
    registerEvent: SeedVariationManager.registerEvent.bind(SeedVariationManager),
    clearEvents: SeedVariationManager.clearEvents.bind(SeedVariationManager),
  };
}
