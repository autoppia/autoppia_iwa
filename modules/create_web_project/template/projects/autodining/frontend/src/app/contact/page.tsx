"use client";

import { useSeed } from "@/context/SeedContext";
import { useDynamicSystem } from "@/dynamic/shared";
import { ID_VARIANTS_MAP, CLASS_VARIANTS_MAP, TEXT_VARIANTS_MAP } from "@/dynamic/v3";
import Navbar from "@/components/Navbar";
import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { Mail, Phone, MapPin, Clock, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EVENT_TYPES, logEvent } from "@/library/events";

export default function ContactPage() {
  const { seed, resolvedSeeds } = useSeed();
  const dyn = useDynamicSystem();
  const searchParams = useSearchParams();
  const hasSeedParam = Boolean(searchParams?.get("seed"));

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
  });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => {
      setFormData({ name: "", email: "", subject: "", message: "" });
      setSubmitted(false);
    }, 3000);

    logEvent(EVENT_TYPES.CONTACT_FORM_SUBMIT, {
      ...formData,
      seed,
    });
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const contactInfo = [
    {
      icon: <Mail className="w-6 h-6" />,
      title: "Email Us",
      content: "support@autodining.com",
      link: "mailto:support@autodining.com",
    },
    {
      icon: <Phone className="w-6 h-6" />,
      title: "Call Us",
      content: "+1 (555) 123-4567",
      link: "tel:+15551234567",
    },
    {
      icon: <MapPin className="w-6 h-6" />,
      title: "Visit Us",
      content: "123 Food Street, Dining City, DC 12345",
      link: "#",
    },
    {
      icon: <Clock className="w-6 h-6" />,
      title: "Business Hours",
      content: "Mon - Fri: 9:00 AM - 6:00 PM",
      link: "#",
    },
  ];

  useEffect(() => {
    logEvent(EVENT_TYPES.CONTACT_PAGE_VIEW, {
      seed,
      fromSeedParam: hasSeedParam,
    });
  }, [seed, hasSeedParam]);

  return (
    dyn.v1.addWrapDecoy("contact-page", (
      <main id={dyn.v3.getVariant("contact-page", ID_VARIANTS_MAP, "contact-page")}>
        <Navbar />
        {dyn.v1.addWrapDecoy("contact-content", (
          <div className="max-w-6xl mx-auto px-4 py-8" id={dyn.v3.getVariant("contact-content", ID_VARIANTS_MAP, "contact-content")}>
        {/* Hero Section */}
        {dyn.v1.addWrapDecoy("contact-hero", (
          <div className="mb-12 text-center" id={dyn.v3.getVariant("contact-hero", ID_VARIANTS_MAP, "contact-hero")}>
            <h1 className="text-5xl font-bold text-gray-900 mb-4" id={dyn.v3.getVariant("contact-title", ID_VARIANTS_MAP, "contact-title")}>
              {dyn.v3.getVariant("get_in_touch", TEXT_VARIANTS_MAP, "Get in Touch")}
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto" id={dyn.v3.getVariant("contact-subtitle", ID_VARIANTS_MAP, "contact-subtitle")}>
              {dyn.v3.getVariant("contact_description", TEXT_VARIANTS_MAP, "Have questions or feedback? We'd love to hear from you! Reach out to us and we'll get back to you as soon as possible.")}
            </p>
          </div>
        ), "contact-hero-wrap")}

        {/* Main Content: Contact Info + Form */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
          {/* Contact Information */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Contact Information
            </h2>
            <p className="text-gray-600 mb-8">
              Feel free to reach out through any of these channels. We're here
              to help!
            </p>
            <div className="space-y-4">
              {contactInfo.map((info, index) => (
                <a
                  key={index}
                  href={info.link}
                  className="flex items-start gap-4 p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md hover:border-[#46a758] transition-all duration-300 group cursor-default"
                  onClick={() =>
                    logEvent(EVENT_TYPES.CONTACT_CARD_CLICK, {
                      type: info.title,
                      seed,
                    })
                  }
                >
                  <div className="text-[#46a758] group-hover:scale-110 transition-transform">
                    {info.icon}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {info.title}
                    </h3>
                    <p className="text-gray-600">{info.content}</p>
                  </div>
                </a>
              ))}
            </div>
          </div>

          {/* Contact Form */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Send us a Message
            </h2>
            <div className="bg-white border border-gray-200 rounded-2xl p-8">
              {submitted && (
                <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800">
                  Thank you for your message! We'll get back to you soon.
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Name */}
                <div>
                  <label
                    htmlFor="name"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Name *
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    required
                    value={formData.name}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#46a758] focus:border-[#46a758] outline-none transition-colors"
                    placeholder={dyn.v3.getVariant("name_placeholder", TEXT_VARIANTS_MAP, "Your full name")}
                  />
                </div>

                {/* Email */}
                <div>
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Email *
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    required
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#46a758] focus:border-[#46a758] outline-none transition-colors"
                    placeholder={dyn.v3.getVariant("email_placeholder", TEXT_VARIANTS_MAP, "your.email@example.com")}
                  />
                </div>

                {/* Subject */}
                <div>
                  <label
                    htmlFor="subject"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Subject *
                  </label>
                  <input
                    type="text"
                    id="subject"
                    name="subject"
                    required
                    value={formData.subject}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#46a758] focus:border-[#46a758] outline-none transition-colors"
                    placeholder={dyn.v3.getVariant("subject_placeholder", TEXT_VARIANTS_MAP, "What's this about?")}
                  />
                </div>

                {/* Message */}
                <div>
                  <label
                    htmlFor="message"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Message *
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    required
                    value={formData.message}
                    onChange={handleChange}
                    rows={6}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#46a758] focus:border-[#46a758] outline-none resize-none transition-colors"
                    placeholder={dyn.v3.getVariant("message_placeholder", TEXT_VARIANTS_MAP, "Tell us more about your inquiry...")}
                  />
                </div>

                {/* Submit Button */}
                <div className="pt-2">
                  {dyn.v1.addWrapDecoy("send-message-button", (
                    <Button
                      type="submit"
                      id={dyn.v3.getVariant("send-message-button", ID_VARIANTS_MAP, "send-message-button")}
                      className={dyn.v3.getVariant("button-primary", CLASS_VARIANTS_MAP, "w-full bg-[#46a758] hover:bg-[#3d8f4e] text-white px-6 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-colors")}
                    >
                      <Send className="w-5 h-5" />
                      {dyn.v3.getVariant("send_message", TEXT_VARIANTS_MAP, "Send Message")}
                    </Button>
                  ), "send-message-button-wrap")}
                </div>
              </form>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="bg-gray-50 rounded-2xl p-8 md:p-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">
            Frequently Asked Questions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                title: "How do I make a reservation?",
                description:
                  "Search for a restaurant, pick a date and time, and complete the booking in seconds.",
              },
              {
                title: "Can I cancel my reservation?",
                description:
                  "Yes—up to 24 hours before your booking time. Details are in your confirmation email.",
              },
              {
                title: "Is there a booking fee?",
                description:
                  "No, our service is free. You only pay the restaurant when you dine.",
              },
            ].map((item) => (
              <div
                key={item.title}
                className="bg-white rounded-lg p-6 shadow-sm"
              >
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {item.title}
                </h3>
                <p className="text-gray-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
        </div>
        ), "contact-content-wrap")}
      </main>
    ), "contact-page-wrap")
  );
}
