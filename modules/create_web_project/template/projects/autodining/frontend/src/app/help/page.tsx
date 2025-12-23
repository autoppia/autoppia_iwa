"use client";

import { useSeed } from "@/context/SeedContext";
import { useDynamicSystem } from "@/dynamic/shared";
import { ID_VARIANTS_MAP, CLASS_VARIANTS_MAP, TEXT_VARIANTS_MAP } from "@/dynamic/v3";
import Navbar from "@/components/Navbar";
import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { ChevronDown, ChevronUp, Search, BookOpen, HelpCircle, MessageCircle, Calendar } from "lucide-react";
import { EVENT_TYPES, logEvent } from "@/library/events";

interface FAQItem {
  question: string;
  answer: string;
  category: string;
}

export default function HelpPage() {
  const { seed, resolvedSeeds } = useSeed();
  const dyn = useDynamicSystem();
  const searchParams = useSearchParams();
  const hasSeedParam = Boolean(searchParams?.get("seed"));
  const [openIndex, setOpenIndex] = useState<number | null>(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  const faqs: FAQItem[] = [
    {
      category: "Getting Started",
      question: "How do I create an account?",
      answer: "Creating an account is easy! Click on the 'Sign Up' button in the top right corner, enter your email and password, and you're all set. You can also sign up using your Google or Facebook account for faster access.",
    },
    {
      category: "Getting Started",
      question: "How do I search for restaurants?",
      answer: "Use the search bar on the homepage to search by restaurant name, cuisine type, or location. You can also filter results by price range, ratings, and availability.",
    },
    {
      category: "Bookings",
      question: "How do I make a reservation?",
      answer: "Browse our restaurant listings, select a restaurant, choose your preferred date and time, specify the number of guests, and complete the booking. You'll receive a confirmation email with all the details.",
    },
    {
      category: "Bookings",
      question: "Can I modify my reservation?",
      answer: "Yes! You can modify your reservation by accessing your booking history. Click on 'My Reservations' in your account, select the booking you want to modify, and make the necessary changes. Note that modifications depend on restaurant availability.",
    },
    {
      category: "Bookings",
      question: "What is your cancellation policy?",
      answer: "You can cancel your reservation free of charge up to 24 hours before your booking time. Cancellations made less than 24 hours in advance may be subject to the restaurant's cancellation policy.",
    },
    {
      category: "Payments",
      question: "Is there a booking fee?",
      answer: "No, our service is completely free for customers. We don't charge any booking fees. The only charges you'll see are from the restaurant itself for your meal.",
    },
    {
      category: "Payments",
      question: "Do I pay through AutoDining?",
      answer: "No, payment is handled directly by the restaurant. You'll pay for your meal at the restaurant when you dine. We simply facilitate the reservation process.",
    },
    {
      category: "Account",
      question: "How do I update my profile information?",
      answer: "Go to 'My Account' in the top menu, then click on 'Profile Settings'. From there, you can update your personal information, contact details, and preferences.",
    },
    {
      category: "Account",
      question: "How do I view my reservation history?",
      answer: "Click on 'My Reservations' in your account dashboard. You'll see a list of all your past, current, and upcoming reservations with details about each booking.",
    },
    {
      category: "Restaurants",
      question: "How are restaurants selected?",
      answer: "We carefully curate our restaurant listings based on quality, customer reviews, and dining experience. All restaurants go through a vetting process to ensure they meet our standards.",
    },
    {
      category: "Restaurants",
      question: "Can I leave a review?",
      answer: "Yes! After dining at a restaurant, you can leave a review and rating. Reviews help other diners make informed decisions and help restaurants improve their service.",
    },
    {
      category: "Technical",
      question: "The website is not loading properly",
      answer: "Try clearing your browser cache and cookies, or try using a different browser. If the issue persists, please contact our support team with details about your browser and device.",
    },
    {
      category: "Technical",
      question: "I didn't receive a confirmation email",
      answer: "Check your spam or junk folder. If you still don't see it, verify that the email address in your account is correct. You can also view your reservations directly in your account dashboard.",
    },
  ];

  const categories = ["all", ...Array.from(new Set(faqs.map((faq) => faq.category)))];

  const filteredFAQs = faqs.filter((faq) => {
    const matchesSearch = faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         faq.answer.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === "all" || faq.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const toggleFAQ = (index: number, faq: FAQItem) => {
    const nextIndex = openIndex === index ? null : index;
    setOpenIndex(nextIndex);
    logEvent(EVENT_TYPES.HELP_FAQ_TOGGLED, {
      question: faq.question,
      category: faq.category,
      opened: nextIndex === index,
    });
  };

  const helpSections = [
    {
      icon: <BookOpen className="w-8 h-8" />,
      title: "Guides & Tutorials",
      description: "Step-by-step guides to help you get the most out of AutoDining.",
      link: "#",
    },
    {
      icon: <MessageCircle className="w-8 h-8" />,
      title: "Live Chat",
      description: "Chat with our support team in real-time for instant assistance.",
      link: "#",
    },
    {
      icon: <HelpCircle className="w-8 h-8" />,
      title: "Community Forum",
      description: "Connect with other users and share tips and experiences.",
      link: "#",
    },
    {
      icon: <Calendar className="w-8 h-8" />,
      title: "Video Tutorials",
      description: "Watch video guides to learn how to use all our features.",
      link: "#",
    },
  ];

  useEffect(() => {
    logEvent(EVENT_TYPES.HELP_PAGE_VIEW, {
      seed,
      fromSeedParam: hasSeedParam,
    });
  }, [seed, hasSeedParam]);

  return (
    dyn.v1.addWrapDecoy("help-page", (
      <main id={dyn.v3.getVariant("help-page", ID_VARIANTS_MAP, "help-page")}>
        <Navbar />
        {dyn.v1.addWrapDecoy("help-content", (
          <div className="max-w-6xl mx-auto px-4 py-8" id={dyn.v3.getVariant("help-content", ID_VARIANTS_MAP, "help-content")}>
        {/* Hero Section */}
        {dyn.v1.addWrapDecoy("help-hero", (
          <div className="mb-12 text-center" id={dyn.v3.getVariant("help-hero", ID_VARIANTS_MAP, "help-hero")}>
            <h1 className="text-5xl font-bold text-gray-900 mb-4" id={dyn.v3.getVariant("help-title", ID_VARIANTS_MAP, "help-title")}>
              {dyn.v3.getVariant("help_center", TEXT_VARIANTS_MAP, "How can we help you?")}
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto" id={dyn.v3.getVariant("help-subtitle", ID_VARIANTS_MAP, "help-subtitle")}>
              {dyn.v3.getVariant("help_description", TEXT_VARIANTS_MAP, "Find answers to common questions or get in touch with our support team. We're here to help make your dining experience seamless.")}
            </p>
          </div>
        ), "help-hero-wrap")}

        {/* Search Section */}
        {dyn.v1.addWrapDecoy("help-search-section", (
          <section className="mb-12" id={dyn.v3.getVariant("help-search-section", ID_VARIANTS_MAP, "help-search-section")}>
            <div className="relative max-w-2xl mx-auto">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                id={dyn.v3.getVariant("search-input-help", ID_VARIANTS_MAP, "search-input-help")}
                placeholder={dyn.v3.getVariant("search_help_placeholder", TEXT_VARIANTS_MAP, "Search for help...")}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className={dyn.v3.getVariant("input-text", CLASS_VARIANTS_MAP, "w-full pl-12 pr-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#46a758] focus:border-[#46a758] outline-none text-lg")}
              />
            </div>
          </section>
        ), "help-search-section-wrap")}

        {/* Help Sections */}
        {dyn.v1.addWrapDecoy("help-sections-grid", (
          <section className="mb-12" id={dyn.v3.getVariant("help-sections-grid", ID_VARIANTS_MAP, "help-sections-grid")}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {helpSections.map((section, index) => (
                dyn.v1.addWrapDecoy(`help-section-${index}`, (
                  <a
                    key={index}
                    href={section.link}
                    id={dyn.v3.getVariant(`help-section-${index === 0 ? "guides" : index === 1 ? "chat" : index === 2 ? "forum" : "videos"}`, ID_VARIANTS_MAP, `help-section-${index}`)}
                    className={dyn.v3.getVariant("card", CLASS_VARIANTS_MAP, "bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow duration-300 hover:border-[#46a758] text-center cursor-default")}
                  >
                    <div className="text-[#46a758] mb-4 flex justify-center">{section.icon}</div>
                    <h3 className={dyn.v3.getVariant("card-title", CLASS_VARIANTS_MAP, "text-lg font-semibold text-gray-900 mb-2")}>
                      {section.title}
                    </h3>
                    <p className="text-gray-600 text-sm">
                      {section.description}
                    </p>
                  </a>
                ), `help-section-wrap-${index}`)
              ))}
            </div>
          </section>
        ), "help-sections-grid-wrap")}

        {/* Category Filters */}
        {dyn.v1.addWrapDecoy("help-category-filters", (
          <section className="mb-8" id={dyn.v3.getVariant("help-category-filters", ID_VARIANTS_MAP, "help-category-filters")}>
            <div className="flex flex-wrap gap-3 justify-center">
              {categories.map((category) => (
                dyn.v1.addWrapDecoy(`help-category-${category}`, (
                  <button
                    key={category}
                    onClick={() => {
                      setSelectedCategory(category);
                      logEvent(EVENT_TYPES.HELP_CATEGORY_SELECTED, {
                        category,
                        seed,
                      });
                    }}
                    id={dyn.v3.getVariant(`help-category-${category}`, ID_VARIANTS_MAP, `help-category-${category}`)}
                    className={`px-6 py-2 rounded-full font-medium transition-colors ${
                      selectedCategory === category
                        ? "bg-[#46a758] text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </button>
                ), `help-category-wrap-${category}`)
              ))}
            </div>
          </section>
        ), "help-category-filters-wrap")}

        {/* FAQ Section */}
        {dyn.v1.addWrapDecoy("help-faq-section", (
          <section className="mb-12" id={dyn.v3.getVariant("help-faq-section", ID_VARIANTS_MAP, "help-faq-section")}>
            <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center" id={dyn.v3.getVariant("faq-section-title", ID_VARIANTS_MAP, "faq-section-title")}>
              {dyn.v3.getVariant("frequently_asked_questions", TEXT_VARIANTS_MAP, "Frequently Asked Questions")}
            </h2>
            <div className="space-y-4">
              {filteredFAQs.map((faq, index) => (
                dyn.v1.addWrapDecoy(`faq-item-${index}`, (
                  <div
                    key={index}
                    id={dyn.v3.getVariant(`faq-item-${index}`, ID_VARIANTS_MAP, `faq-item-${index}`)}
                    className="bg-white border border-gray-200 rounded-xl overflow-hidden hover:shadow-md transition-shadow"
                  >
                    <button
                      onClick={() => toggleFAQ(index, faq)}
                      className="w-full px-6 py-5 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex-1">
                        <span className="text-xs font-semibold text-[#46a758] uppercase tracking-wide mr-3">
                          {faq.category}
                        </span>
                        <span className="text-lg font-semibold text-gray-900" id={dyn.v3.getVariant(`faq-question-${index}`, ID_VARIANTS_MAP, `faq-question-${index}`)}>{faq.question}</span>
                      </div>
                      {openIndex === index ? (
                        <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0 ml-4" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0 ml-4" />
                      )}
                    </button>
                    {openIndex === index && (
                      <div className="px-6 pb-5 pt-0">
                        <div className="pl-0 border-l-4 border-[#46a758] pl-4">
                          <p className="text-gray-600 leading-relaxed" id={dyn.v3.getVariant(`faq-answer-${index}`, ID_VARIANTS_MAP, `faq-answer-${index}`)}>{faq.answer}</p>
                        </div>
                      </div>
                    )}
                  </div>
                ), `faq-item-wrap-${index}`)
              ))}
            </div>
            {filteredFAQs.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">
                  No results found. Try adjusting your search or category filter.
                </p>
              </div>
            )}
          </section>
        ), "help-faq-section-wrap")}

        {/* CTA Section */}
        {dyn.v1.addWrapDecoy("help-cta-section", (
          <section className="mb-12" id={dyn.v3.getVariant("help-cta-section", ID_VARIANTS_MAP, "help-cta-section")}>
            <div className="bg-gradient-to-r from-[#46a758] to-[#3d8f4e] rounded-2xl p-8 md:p-12 text-white text-center">
              <h2 className="text-3xl font-bold mb-4" id={dyn.v3.getVariant("still-need-help-title", ID_VARIANTS_MAP, "still-need-help-title")}>
                {dyn.v3.getVariant("still_need_help", TEXT_VARIANTS_MAP, "Still need help?")}
              </h2>
              <p className="text-lg mb-6 opacity-90" id={dyn.v3.getVariant("still-need-help-description", ID_VARIANTS_MAP, "still-need-help-description")}>
                {dyn.v3.getVariant("still_need_help_description", TEXT_VARIANTS_MAP, "Can't find what you're looking for? Our support team is ready to assist you.")}
              </p>
              {dyn.v1.addWrapDecoy("contact-support-button", (
                <a
                  href="/contact"
                  className={dyn.v3.getVariant("button-primary", CLASS_VARIANTS_MAP, "inline-block bg-white text-[#46a758] px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors")}
                  id={dyn.v3.getVariant("contact-support-button", ID_VARIANTS_MAP, "contact-support-button")}
                >
                  {dyn.v3.getVariant("contact_support", TEXT_VARIANTS_MAP, "Contact Support")}
                </a>
              ), "contact-support-button-wrap")}
            </div>
          </section>
        ), "help-cta-section-wrap")}
        </div>
        ), "help-content-wrap")}
      </main>
    ), "help-page-wrap")
  );
}
