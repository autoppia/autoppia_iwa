"use client";

import { useSeed } from "@/context/SeedContext";
import Navbar from "@/components/Navbar";
import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { SeedLink } from "@/components/ui/SeedLink";

interface FAQItem {
  question: string;
  answer: string;
}

export default function FaqsPage() {
  const { seed, resolvedSeeds } = useSeed();
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const faqs: FAQItem[] = [
    {
      question: "How do I make a reservation?",
      answer: "Browse our restaurant listings, select a restaurant, choose your preferred date and time, specify the number of guests, and complete the booking. You'll receive a confirmation email with all the details.",
    },
    {
      question: "Can I cancel my reservation?",
      answer: "Yes, you can cancel your reservation up to 24 hours before your booking time. Check your confirmation email for details on how to cancel, or visit 'My Reservations' in your account.",
    },
    {
      question: "Is there a booking fee?",
      answer: "No, our service is completely free. We don't charge any booking fees to our customers. The only charges you'll see are from the restaurant itself for your meal.",
    },
    {
      question: "Do I pay through AutoDining?",
      answer: "No, payment is handled directly by the restaurant. You'll pay for your meal at the restaurant when you dine. We simply facilitate the reservation process.",
    },
    {
      question: "How do I modify my reservation?",
      answer: "You can modify your reservation by accessing your booking history. Click on 'My Reservations' in your account, select the booking you want to modify, and make the necessary changes. Note that modifications depend on restaurant availability.",
    },
    {
      question: "What happens if I'm running late?",
      answer: "We recommend calling the restaurant directly if you're running late. Most restaurants will hold your table for 15-20 minutes. If you're significantly delayed, contact the restaurant to see if they can still accommodate you.",
    },
    {
      question: "Can I make a reservation for a large group?",
      answer: "Yes! When making a reservation, you can specify the number of guests. For large groups (typically 8+ people), we recommend calling the restaurant directly to ensure they can accommodate your party.",
    },
    {
      question: "How do I leave a review?",
      answer: "After dining at a restaurant, you can leave a review and rating. Visit the restaurant's page and click on 'Write a Review'. Your feedback helps other diners make informed decisions.",
    },
    {
      question: "I didn't receive a confirmation email",
      answer: "Check your spam or junk folder. If you still don't see it, verify that the email address in your account is correct. You can also view your reservations directly in your account dashboard.",
    },
    {
      question: "How are restaurants selected?",
      answer: "We carefully curate our restaurant listings based on quality, customer reviews, and dining experience. All restaurants go through a vetting process to ensure they meet our standards.",
    },
  ];

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <main>
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="mb-12 text-left">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Frequently Asked Questions
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Find quick answers to the most common questions about AutoDining.
            Can't find what you're looking for? <SeedLink href="/help" className="text-[#46a758] hover:underline">Visit our Help Center</SeedLink> or <SeedLink href="/contact" className="text-[#46a758] hover:underline">contact our support team</SeedLink>.
          </p>
        </div>

        {/* FAQ Section */}
        <div className="mb-12">
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div
                key={index}
                className="bg-white border border-gray-200 rounded-xl overflow-hidden hover:shadow-md transition-shadow"
              >
                <button
                  onClick={() => toggleFAQ(index)}
                  className="w-full px-6 py-5 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
                >
                  <span className="text-lg font-semibold text-gray-900 pr-8">{faq.question}</span>
                  {openIndex === index ? (
                    <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  )}
                </button>
                {openIndex === index && (
                  <div className="px-6 pb-5 pt-0">
                    <div className="pl-0 border-l-4 border-[#46a758] pl-4">
                      <p className="text-gray-600 leading-relaxed">{faq.answer}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Still Need Help Section */}
        <div className="mb-12">
          <div className="bg-gradient-to-r from-[#46a758] to-[#3d8f4e] rounded-2xl p-8 md:p-12 text-white text-center">
            <h2 className="text-3xl font-bold mb-4">Still have questions?</h2>
            <p className="text-lg mb-6 opacity-90">
              Our support team is here to help! Get in touch and we'll respond as soon as possible.
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <SeedLink
                href="/help"
                className="inline-block bg-white text-[#46a758] px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
              >
                Visit Help Center
              </SeedLink>
              <SeedLink
                href="/contact"
                className="inline-block bg-transparent border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors"
              >
                Contact Support
              </SeedLink>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
