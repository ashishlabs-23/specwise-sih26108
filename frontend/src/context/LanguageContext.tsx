"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export type Language = "en" | "hi";

interface Translations {
  siteTitle: string;
  tagline: string;
  heroHeading1: string;
  heroHeading2: string;
  heroSubtitle: string;
  enterDescription: string;
  uploadDoc: string;
  searchPlaceholder: string;
  findStandards: string;
  analyzing: string;
  examples: string;
  recentSearches: string;
  clearHistory: string;
  coldStartNotice: string;
  officialPortal: string;
  home: string;
  howItWorks: string;
  resources: string;
  about: string;
}

const dictionary: Record<Language, Translations> = {
  en: {
    siteTitle: "SpecWise",
    tagline: "Right Standards. Safer Procurement.",
    heroHeading1: "Not sure which",
    heroHeading2: "Indian Standard applies?",
    heroSubtitle: "Describe your product or paste tender specifications. SpecWise helps you find the most relevant BIS standards with clear guidance and trusted sources.",
    enterDescription: "Enter Description",
    uploadDoc: "Upload Document (PDF)",
    searchPlaceholder: "e.g. openwell submersible pumpset for agricultural irrigation",
    findStandards: "Find Applicable Standards",
    analyzing: "Analyzing Standards...",
    examples: "Examples:",
    recentSearches: "Recent Searches:",
    clearHistory: "Clear",
    coldStartNotice: "Connecting to secure engine on Render (free tier instance waking up, ~15-30s on cold start)...",
    officialPortal: "Official Portal",
    home: "Home",
    howItWorks: "How it works",
    resources: "Resources",
    about: "About",
  },
  hi: {
    siteTitle: "स्पेकवाइज़",
    tagline: "सही मानक। सुरक्षित खरीद।",
    heroHeading1: "पता नहीं कौन सा",
    heroHeading2: "भारतीय मानक (IS) लागू होता है?",
    heroSubtitle: "अपने उत्पाद का विवरण दें या निविदा विनिर्देश पेस्ट करें। स्पेकवाइज़ आपको विश्वसनीय स्रोतों के साथ सबसे प्रासंगिक बीआईएस मानक खोजने में मदद करता है।",
    enterDescription: "विवरण दर्ज करें",
    uploadDoc: "दस्तावेज़ अपलोड करें (PDF)",
    searchPlaceholder: "उदा. कृषि सिंचाई के लिए ओपनवेल सबमर्सिबल पंपसेट",
    findStandards: "लागू मानक खोजें",
    analyzing: "मानकों का विश्लेषण हो रहा है...",
    examples: "उदाहरण:",
    recentSearches: "हाल की खोजें:",
    clearHistory: "साफ़ करें",
    coldStartNotice: "रेंडर पर बैकएंड इंजन से जुड़ रहे हैं (कोल्ड स्टार्ट में ~15-30 सेकंड लग सकते हैं)...",
    officialPortal: "आधिकारिक पोर्टल",
    home: "मुख्य पृष्ठ",
    howItWorks: "कार्यप्रणाली",
    resources: "संसाधन",
    about: "के बारे में",
  },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: Translations;
}

const LanguageContext = createContext<LanguageContextType>({
  language: "en",
  setLanguage: () => {},
  t: dictionary.en,
});

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>("en");

  useEffect(() => {
    try {
      const saved = localStorage.getItem("specwise_lang") as Language;
      if (saved && (saved === "en" || saved === "hi")) {
        setLanguageState(saved);
      }
    } catch {
      // ignore in non-browser env
    }
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    try {
      localStorage.setItem("specwise_lang", lang);
    } catch {
      // ignore
    }
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t: dictionary[language] }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
