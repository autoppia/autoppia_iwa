"use client";

import { useSeed } from "@/context/SeedContext";
import { SeedLink } from "@/components/ui/SeedLink";
import { useDynamicSystem } from "@/dynamic/shared";
import { ID_VARIANTS_MAP } from "@/dynamic/v3";

interface NavbarProps {
  showSearch?: boolean;
  searchInputId?: string;
  searchButtonId?: string;
  onSearchClick?: () => void;
}

export default function Navbar({ 
  showSearch = false,
  searchInputId,
  searchButtonId,
  onSearchClick 
}: NavbarProps) {
  const dyn = useDynamicSystem();

  // V1: Order navigation links dynamically
  const navLinks = [
    { href: "/help", label: "Help", key: "nav-help" },
    { href: "/about", label: "About", key: "nav-about" },
    { href: "/contact", label: "Contact", key: "nav-contact" },
    ...(showSearch ? [{ href: "/faqs", label: "FAQs", key: "nav-faqs" }] : []),
  ];
  const navOrder = dyn.v1.changeOrderElements("navbar-links", navLinks.length);
  const orderedNavLinks = navOrder.map((idx) => navLinks[idx]);

  return (
    <nav 
      className="w-full border-b bg-white sticky top-0 z-10"
      id={dyn.v3.getVariant("navbar", ID_VARIANTS_MAP, "navbar")}
    >
      {dyn.v1.addWrapDecoy("navbar-container", (
        <div className="w-full flex items-center h-20 px-6 gap-6">
          {/* Logo section - always on left */}
          {dyn.v1.addWrapDecoy("navbar-logo", (
            <div className="flex items-center gap-3 ml-0">
              <SeedLink href="/">
                {dyn.v1.addWrapDecoy("navbar-logo-link", (
                  <div 
                    className="bg-[#46a758] px-3 py-1 rounded flex items-center h-9"
                    id={dyn.v3.getVariant("navbar-logo", ID_VARIANTS_MAP, "navbar-logo")}
                  >
                    <span className="font-bold text-white text-lg">
                      {dyn.v3.getVariant("app_title", undefined, "AutoDining")}
                    </span>
                  </div>
                ))}
              </SeedLink>
            </div>
          ), "navbar-logo-wrap")}

          <div className="flex-1" />

          {/* Navigation links - right */}
          {dyn.v1.addWrapDecoy("navbar-links-container", (
            <div 
              className="flex items-center gap-6 mr-0"
              id={dyn.v3.getVariant("navbar-links", ID_VARIANTS_MAP, "navbar-links")}
            >
              {orderedNavLinks.map((link) => (
                <SeedLink
                  key={link.key}
                  className="text-sm text-gray-600 hover:text-[#46a758] transition-colors"
                  href={link.href}
                  id={dyn.v3.getVariant(link.key, ID_VARIANTS_MAP, link.key)}
                >
                  {dyn.v1.addWrapDecoy(link.key, link.label)}
                </SeedLink>
              ))}
            </div>
          ), "navbar-links-wrap")}
        </div>
      ), "navbar-main-wrap")}
    </nav>
  );
}
