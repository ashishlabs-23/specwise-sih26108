"use client";

import React, { createContext, useContext, useEffect, useMemo, useState } from "react";

export const languages = ["en", "hi", "kn", "ta", "te"] as const;
export type Language = (typeof languages)[number];
type Translations = Record<string, string>;

const english: Translations = {
  siteTitle: "SpecWise", tagline: "Right Standards. Safer Procurement.",
  heroHeading1: "Not sure which", heroHeading2: "Indian Standard applies?",
  heroSubtitle: "Describe your product or paste tender specifications. SpecWise helps you find the most relevant BIS standards with clear guidance and trusted sources.",
  enterDescription: "Enter Description", uploadDoc: "Upload Document (PDF)",
  searchPlaceholder: "e.g. openwell submersible pumpset for agricultural irrigation",
  findStandards: "Find Applicable Standards", analyzing: "Analyzing Standards...",
  examples: "Examples:", recentSearches: "Recent Searches:", clearHistory: "Clear",
  coldStartNotice: "Connecting to the analysis service. The first request may take a little longer while it starts.",
  officialPortal: "Official Portal", home: "Home", howItWorks: "How it works", resources: "Resources", about: "About",
  prototypeNotice: "Prototype · Not an official BIS portal", language: "Language", close: "Close",
  evidenceSupport: "Evidence-Grounded BIS Decision Support", bisEngine: "BIS Standards Engine", verifiedData: "Verified Data",
  informedProcurement: "Make informed procurement decisions", procurementDescription: "Avoid incorrect standard citations in tender documents and purchase orders.",
  indianStandards: "Based on Indian Standards & official sources", standardsDescription: "Every result is grounded in BIS committee evidence, guidelines, and published standards.",
  designedFor: "Designed for citizens, buyers and government users", designedDescription: "Plain-language summaries backed by deep technical compliance traceability.",
  enterTender: "Enter a product description or tender specification", uploadTender: "Upload Tender Document (PDF)",
  extractionWorkflow: "Document Extraction Workflow", browseFiles: "Browse Files", dragDrop: "Drag & drop tender PDF here",
  pdfSupport: "Supports technical specifications, RFP documents, schedule of requirements (.pdf up to 25MB)",
  cancel: "Cancel", processDocument: "Process Document", processing: "Processing…", connectionError: "Connection / API Error", retryAnalysis: "Retry Analysis",
  newSearch: "New Search", share: "Share", reportDownload: "Download Report (Audit HTML)", auditReport: "Audit Report",
  definitiveMatch: "Definitive Match", evaluationResult: "Evaluation Result", reviewRequired: "Technical Review Required",
  noPrimary: "No primary standard selected", outOfCorpus: "Out of Prototype Corpus", whyDecision: "Why this decision?", simpleTerms: "In simple terms",
  noPrimaryDescription: "The input is not specific enough to select a primary product standard.",
  outOfCorpusDescription: "Specification falls outside the verified MED 20 pump corpus",
  reviewDescription: "Review candidate standards and tender specifications",
  matchedEvidence: "Matched based on product keywords, application terms, and normative BIS scope evidence.",
  primaryStandard: "Primary Standard", recommendedCore: "Recommended core specification", standardNumber: "Standard No.", product: "Product", application: "Application", status: "Status", scope: "Scope", whyMatched: "Why it matched", bisPortal: "BIS Portal",
  contextStandards: "Matched Context Standards", contextOnly: "Context only — not a recommendation", noRecommendation: "No matching standard exists in the current prototype corpus (MED 20 pump sector).",
  notFormallyConfirmed: "Not Formally Confirmed", activeInForce: "Active (In Force)", revisionWarning: "Revision / Superseded Warning",
  certificationStatus: "Certification / QCO Status", notApplicable: "Not Applicable", notEvaluated: "Not Evaluated", regulatoryNotice: "Regulatory Notice", learnMore: "Learn more",
  noCertificationMapping: "No verified certification/QCO mapping available in the current prototype knowledge base.",
  reportTitle: "SpecWise Audit Report", print: "Print", download: "Download", noReport: "No report generated.",
  aboutTitle: "About SpecWise (SIH26108)", objective: "Objective", keyPrinciples: "Key Engineering Principles", closeDialog: "Close",
  recentClear: "Clear", loadingResources: "Loading verified corpus data from backend...", failedResources: "Failed to Load Corpus Resources",
  privacy: "Privacy", terms: "Terms", contactBis: "Contact BIS", verifiedBis: "Verified BIS", openSource: "Open Source URL", openDocument: "Open Official Document URL",
  relatedStandards: "Related Standards", evidenceSources: "Evidence Sources", viewAll: "View all", noEvidence: "No evidence records are available for this result.",
  retry: "Retry", shareCopied: "Page link copied to clipboard!", productName: "SpecWise",
  resourcesTitle: "Corpus Resources & Provenance", resourcesSubtitle: "Transparent repository of verified standards, evidence citations, normative relationships, and benchmark evaluation cases loaded live from the backend engine.",
  standards: "Standards", evidence: "Evidence", links: "Links", benchmarks: "Benchmarks", sources: "Sources", page: "Page", of: "of", totalItems: "total items", previous: "Previous", next: "Next",
  prototypeCorpus: "Prototype corpus", notFullCatalog: "Not the full BIS catalogue", verifiedStandards: "Verified Standards", evidenceRecords: "Evidence Records", relationships: "Relationships", benchmarkCases: "Benchmark Cases", sourceProvenance: "Source Provenance", searchIn: "Search in", roleFilter: "Role Filter", allTypes: "All Standard Types", primaryProductType: "Primary Product Standard", practiceCode: "Code of Practice", testMethod: "Test Method", relatedSpecification: "Related Specification",
};

const dictionary: Record<Language, Translations> = {
  en: english,
  hi: {
    ...english,
    siteTitle: "स्पेकवाइज़", tagline: "सही मानक। सुरक्षित खरीद।",
    heroHeading1: "पता नहीं कौन सा", heroHeading2: "भारतीय मानक लागू होता है?",
    heroSubtitle: "अपने उत्पाद का विवरण दें या निविदा विनिर्देश पेस्ट करें। स्पेकवाइज़ विश्वसनीय स्रोतों के साथ प्रासंगिक बीआईएस मानक खोजने में मदद करता है।",
    enterDescription: "विवरण दर्ज करें", uploadDoc: "दस्तावेज़ अपलोड करें (PDF)", searchPlaceholder: "उदा. कृषि सिंचाई के लिए ओपनवेल सबमर्सिबल पंपसेट",
    findStandards: "लागू मानक खोजें", analyzing: "मानकों का विश्लेषण हो रहा है...", examples: "उदाहरण:", recentSearches: "हाल की खोजें:", clearHistory: "साफ़ करें",
    coldStartNotice: "विश्लेषण सेवा से जुड़ रहे हैं। शुरू होने के दौरान पहला अनुरोध थोड़ा अधिक समय ले सकता है।",
    officialPortal: "आधिकारिक पोर्टल", home: "मुख्य पृष्ठ", howItWorks: "यह कैसे काम करता है", resources: "संसाधन", about: "परिचय",
    prototypeNotice: "प्रोटोटाइप · आधिकारिक BIS पोर्टल नहीं", language: "भाषा", close: "बंद करें",
    evidenceSupport: "साक्ष्य-आधारित BIS निर्णय सहायता", bisEngine: "BIS मानक इंजन", verifiedData: "सत्यापित डेटा",
    informedProcurement: "सूचित खरीद निर्णय लें", procurementDescription: "निविदा दस्तावेज़ों और खरीद आदेशों में गलत मानक उद्धरण से बचें।", indianStandards: "भारतीय मानकों और आधिकारिक स्रोतों पर आधारित", standardsDescription: "हर परिणाम BIS समिति के साक्ष्य, दिशानिर्देशों और प्रकाशित मानकों पर आधारित है।", designedFor: "नागरिकों, खरीदारों और सरकारी उपयोगकर्ताओं के लिए", designedDescription: "सरल भाषा में सारांश, तकनीकी अनुपालन के स्पष्ट संदर्भों के साथ।",
    enterTender: "उत्पाद विवरण या निविदा विनिर्देश दर्ज करें", uploadTender: "निविदा दस्तावेज़ अपलोड करें (PDF)", extractionWorkflow: "दस्तावेज़ निष्कर्षण प्रक्रिया",
    browseFiles: "फ़ाइलें चुनें", dragDrop: "निविदा PDF यहाँ खींचकर छोड़ें", pdfSupport: "तकनीकी विनिर्देश, RFP और आवश्यकताओं की सूची समर्थित (.pdf, अधिकतम 25MB)",
    cancel: "रद्द करें", processDocument: "दस्तावेज़ संसाधित करें", processing: "प्रक्रिया जारी…", connectionError: "कनेक्शन / API त्रुटि", retryAnalysis: "विश्लेषण फिर करें",
    newSearch: "नई खोज", share: "साझा करें", reportDownload: "रिपोर्ट डाउनलोड करें (Audit HTML)", auditReport: "ऑडिट रिपोर्ट",
    definitiveMatch: "निश्चित मिलान", evaluationResult: "मूल्यांकन परिणाम", reviewRequired: "तकनीकी समीक्षा आवश्यक", noPrimary: "कोई प्राथमिक मानक नहीं चुना गया", outOfCorpus: "प्रोटोटाइप डेटासेट से बाहर", whyDecision: "इस निर्णय का कारण", simpleTerms: "सरल शब्दों में",
    noPrimaryDescription: "प्राथमिक उत्पाद मानक चुनने के लिए दिया गया विवरण पर्याप्त विशिष्ट नहीं है।", outOfCorpusDescription: "विनिर्देश सत्यापित MED 20 पंप डेटासेट के बाहर है", reviewDescription: "उम्मीदवार मानकों और निविदा विनिर्देशों की समीक्षा करें", matchedEvidence: "उत्पाद के शब्दों, उपयोग और BIS दायरे के साक्ष्य के आधार पर मिलान।",
    primaryStandard: "प्राथमिक मानक", recommendedCore: "अनुशंसित मुख्य विनिर्देश", standardNumber: "मानक संख्या", product: "उत्पाद", application: "उपयोग", status: "स्थिति", scope: "दायरा", whyMatched: "मिलान का कारण", bisPortal: "BIS पोर्टल",
    contextStandards: "संदर्भ के लिए मिले मानक", contextOnly: "केवल संदर्भ — अनुशंसा नहीं", noRecommendation: "वर्तमान प्रोटोटाइप डेटासेट (MED 20 पंप क्षेत्र) में कोई मेल खाता मानक नहीं मिला।",
    notFormallyConfirmed: "औपचारिक पुष्टि नहीं", activeInForce: "लागू (प्रवर्तन में)", revisionWarning: "संशोधन / प्रतिस्थापन चेतावनी",
    certificationStatus: "प्रमाणन / QCO स्थिति", notApplicable: "लागू नहीं", notEvaluated: "मूल्यांकन नहीं हुआ", regulatoryNotice: "नियामक सूचना", learnMore: "और जानें",
    noCertificationMapping: "वर्तमान प्रोटोटाइप ज्ञान-आधार में सत्यापित प्रमाणन/QCO मिलान उपलब्ध नहीं है।", reportTitle: "स्पेकवाइज़ ऑडिट रिपोर्ट", print: "प्रिंट करें", download: "डाउनलोड करें", noReport: "कोई रिपोर्ट तैयार नहीं हुई।",
    aboutTitle: "स्पेकवाइज़ के बारे में (SIH26108)", objective: "उद्देश्य", keyPrinciples: "मुख्य इंजीनियरिंग सिद्धांत", closeDialog: "बंद करें", loadingResources: "बैकएंड से सत्यापित डेटासेट लोड हो रहा है...", failedResources: "डेटासेट संसाधन लोड नहीं हो सके",
    privacy: "गोपनीयता", terms: "उपयोग की शर्तें", contactBis: "BIS से संपर्क करें", verifiedBis: "सत्यापित BIS", openSource: "स्रोत URL खोलें", openDocument: "आधिकारिक दस्तावेज़ URL खोलें", relatedStandards: "संबंधित मानक", evidenceSources: "साक्ष्य स्रोत", viewAll: "सभी देखें", noEvidence: "इस परिणाम के लिए कोई साक्ष्य रिकॉर्ड उपलब्ध नहीं है।", retry: "पुनः प्रयास करें", shareCopied: "पृष्ठ का लिंक कॉपी हो गया!",
  },
  kn: {
    ...english,
    siteTitle: "ಸ್ಪೆಕ್‌ವೈಸ್", tagline: "ಸರಿಯಾದ ಮಾನದಂಡಗಳು. ಸುರಕ್ಷಿತ ಖರೀದಿ.",
    heroHeading1: "ಯಾವ ಭಾರತೀಯ", heroHeading2: "ಮಾನದಂಡ ಅನ್ವಯಿಸುತ್ತದೆ ಎಂದು ತಿಳಿದಿಲ್ಲವೇ?",
    heroSubtitle: "ನಿಮ್ಮ ಉತ್ಪನ್ನವನ್ನು ವಿವರಿಸಿ ಅಥವಾ ಟೆಂಡರ್ ವಿಶೇಷಣಗಳನ್ನು ಅಂಟಿಸಿ. ವಿಶ್ವಾಸಾರ್ಹ ಮೂಲಗಳೊಂದಿಗೆ ಸಂಬಂಧಿತ BIS ಮಾನದಂಡಗಳನ್ನು ಹುಡುಕಲು ಸ್ಪೆಕ್‌ವೈಸ್ ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
    enterDescription: "ವಿವರಣೆ ನಮೂದಿಸಿ", uploadDoc: "ದಾಖಲೆ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ (PDF)", searchPlaceholder: "ಉದಾ. ಕೃಷಿ ನೀರಾವರಿಗಾಗಿ ಓಪನ್‌ವೆಲ್ ಸಬ್‌ಮರ್ಸಿಬಲ್ ಪಂಪ್‌ಸೆಟ್",
    findStandards: "ಅನ್ವಯಿಸುವ ಮಾನದಂಡಗಳನ್ನು ಹುಡುಕಿ", analyzing: "ಮಾನದಂಡಗಳನ್ನು ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...", examples: "ಉದಾಹರಣೆಗಳು:", recentSearches: "ಇತ್ತೀಚಿನ ಹುಡುಕಾಟಗಳು:", clearHistory: "ಅಳಿಸಿ",
    coldStartNotice: "ವಿಶ್ಲೇಷಣಾ ಸೇವೆಗೆ ಸಂಪರ್ಕಿಸಲಾಗುತ್ತಿದೆ. ಸೇವೆ ಪ್ರಾರಂಭವಾಗುವಾಗ ಮೊದಲ ವಿನಂತಿಗೆ ಸ್ವಲ್ಪ ಹೆಚ್ಚು ಸಮಯ ಬೇಕಾಗಬಹುದು.", officialPortal: "ಅಧಿಕೃತ ಪೋರ್ಟಲ್", home: "ಮುಖಪುಟ", howItWorks: "ಇದು ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ", resources: "ಸಂಪನ್ಮೂಲಗಳು", about: "ಪರಿಚಯ",
    prototypeNotice: "ಮಾದರಿ · ಅಧಿಕೃತ BIS ಪೋರ್ಟಲ್ ಅಲ್ಲ", language: "ಭಾಷೆ", close: "ಮುಚ್ಚಿ", evidenceSupport: "ಸಾಕ್ಷ್ಯಾಧಾರಿತ BIS ನಿರ್ಧಾರ ಸಹಾಯ", bisEngine: "BIS ಮಾನದಂಡಗಳ ಎಂಜಿನ್", verifiedData: "ಪರಿಶೀಲಿಸಿದ ಮಾಹಿತಿ",
    informedProcurement: "ಮಾಹಿತಿಯುಕ್ತ ಖರೀದಿ ನಿರ್ಧಾರಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ", procurementDescription: "ಟೆಂಡರ್ ದಾಖಲೆಗಳು ಮತ್ತು ಖರೀದಿ ಆದೇಶಗಳಲ್ಲಿ ತಪ್ಪಾದ ಮಾನದಂಡ ಉಲ್ಲೇಖಗಳನ್ನು ತಪ್ಪಿಸಿ.",
    indianStandards: "ಭಾರತೀಯ ಮಾನದಂಡಗಳು ಮತ್ತು ಅಧಿಕೃತ ಮೂಲಗಳ ಆಧಾರಿತ", standardsDescription: "ಪ್ರತಿ ಫಲಿತಾಂಶವೂ BIS ಸಮಿತಿಯ ಸಾಕ್ಷ್ಯ, ಮಾರ್ಗಸೂಚಿಗಳು ಮತ್ತು ಪ್ರಕಟಿತ ಮಾನದಂಡಗಳನ್ನು ಆಧರಿಸಿದೆ.",
    designedFor: "ನಾಗರಿಕರು, ಖರೀದಿದಾರರು ಮತ್ತು ಸರ್ಕಾರಿ ಬಳಕೆದಾರರಿಗಾಗಿ", designedDescription: "ತಾಂತ್ರಿಕ ಅನುಸರಣೆ ಸಾಕ್ಷ್ಯಗಳೊಂದಿಗೆ ಸರಳ ಭಾಷೆಯ ಸಾರಾಂಶಗಳು.",
    enterTender: "ಉತ್ಪನ್ನ ವಿವರಣೆ ಅಥವಾ ಟೆಂಡರ್ ವಿಶೇಷಣವನ್ನು ನಮೂದಿಸಿ", uploadTender: "ಟೆಂಡರ್ ದಾಖಲೆಯನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ (PDF)", extractionWorkflow: "ದಾಖಲೆ ಪಠ್ಯ ಹೊರತೆಗೆಯುವ ಪ್ರಕ್ರಿಯೆ", browseFiles: "ಕಡತಗಳನ್ನು ಆಯ್ಕೆಮಾಡಿ", dragDrop: "ಟೆಂಡರ್ PDF ಅನ್ನು ಇಲ್ಲಿ ಎಳೆದು ಬಿಡಿ", pdfSupport: "ತಾಂತ್ರಿಕ ವಿಶೇಷಣಗಳು, RFP ಮತ್ತು ಅಗತ್ಯಗಳ ಪಟ್ಟಿ ಬೆಂಬಲಿತ (.pdf, ಗರಿಷ್ಠ 25MB)", cancel: "ರದ್ದುಮಾಡಿ", processDocument: "ದಾಖಲೆಯನ್ನು ಸಂಸ್ಕರಿಸಿ", processing: "ಸಂಸ್ಕರಿಸಲಾಗುತ್ತಿದೆ…",
    connectionError: "ಸಂಪರ್ಕ / API ದೋಷ", retryAnalysis: "ವಿಶ್ಲೇಷಣೆಯನ್ನು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ", newSearch: "ಹೊಸ ಹುಡುಕಾಟ", share: "ಹಂಚಿಕೊಳ್ಳಿ", reportDownload: "ವರದಿ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ (Audit HTML)", auditReport: "ಆಡಿಟ್ ವರದಿ", definitiveMatch: "ನಿಖರ ಹೊಂದಾಣಿಕೆ", evaluationResult: "ಮೌಲ್ಯಮಾಪನ ಫಲಿತಾಂಶ", reviewRequired: "ತಾಂತ್ರಿಕ ಪರಿಶೀಲನೆ ಅಗತ್ಯ", noPrimary: "ಪ್ರಾಥಮಿಕ ಮಾನದಂಡ ಆಯ್ಕೆಯಾಗಿಲ್ಲ", outOfCorpus: "ಮಾದರಿ ಡೇಟಾಸೆಟ್‌ನ ಹೊರಗೆ", whyDecision: "ಈ ನಿರ್ಧಾರಕ್ಕೆ ಕಾರಣವೇನು?", simpleTerms: "ಸರಳವಾಗಿ ಹೇಳುವುದಾದರೆ",
    noPrimaryDescription: "ಪ್ರಾಥಮಿಕ ಉತ್ಪನ್ನ ಮಾನದಂಡವನ್ನು ಆಯ್ಕೆ ಮಾಡಲು ನೀಡಿದ ವಿವರಣೆ ಸಾಕಷ್ಟು ನಿರ್ದಿಷ್ಟವಾಗಿಲ್ಲ.", outOfCorpusDescription: "ವಿಶೇಷಣವು ಪರಿಶೀಲಿಸಿದ MED 20 ಪಂಪ್ ಡೇಟಾಸೆಟ್‌ನ ಹೊರಗಿದೆ", reviewDescription: "ಸಂಭಾವ್ಯ ಮಾನದಂಡಗಳು ಮತ್ತು ಟೆಂಡರ್ ವಿಶೇಷಣಗಳನ್ನು ಪರಿಶೀಲಿಸಿ", matchedEvidence: "ಉತ್ಪನ್ನ ಪದಗಳು, ಬಳಕೆ ಮತ್ತು BIS ವ್ಯಾಪ್ತಿ ಸಾಕ್ಷ್ಯಗಳನ್ನು ಆಧರಿಸಿದ ಹೊಂದಾಣಿಕೆ.",
    primaryStandard: "ಪ್ರಾಥಮಿಕ ಮಾನದಂಡ", recommendedCore: "ಶಿಫಾರಸು ಮಾಡಲಾದ ಮುಖ್ಯ ವಿಶೇಷಣ", standardNumber: "ಮಾನದಂಡ ಸಂಖ್ಯೆ", product: "ಉತ್ಪನ್ನ", application: "ಬಳಕೆ", status: "ಸ್ಥಿತಿ", scope: "ವ್ಯಾಪ್ತಿ", whyMatched: "ಹೊಂದಾಣಿಕೆಯ ಕಾರಣ", bisPortal: "BIS ಪೋರ್ಟಲ್", contextStandards: "ಸಂದರ್ಭಕ್ಕೆ ಹೊಂದಿದ ಮಾನದಂಡಗಳು", contextOnly: "ಸಂದರ್ಭಕ್ಕಾಗಿ ಮಾತ್ರ — ಶಿಫಾರಸು ಅಲ್ಲ", noRecommendation: "ಪ್ರಸ್ತುತ ಮಾದರಿ ಡೇಟಾಸೆಟ್‌ನಲ್ಲಿ (MED 20 ಪಂಪ್ ಕ್ಷೇತ್ರ) ಹೊಂದುವ ಮಾನದಂಡ ಕಂಡುಬಂದಿಲ್ಲ.",
    notFormallyConfirmed: "ಔಪಚಾರಿಕವಾಗಿ ದೃಢೀಕರಿಸಿಲ್ಲ", activeInForce: "ಜಾರಿಯಲ್ಲಿದೆ", revisionWarning: "ಪರಿಷ್ಕರಣೆ / ಬದಲಾವಣೆ ಎಚ್ಚರಿಕೆ", certificationStatus: "ಪ್ರಮಾಣೀಕರಣ / QCO ಸ್ಥಿತಿ", notApplicable: "ಅನ್ವಯಿಸುವುದಿಲ್ಲ", notEvaluated: "ಮೌಲ್ಯಮಾಪನವಾಗಿಲ್ಲ", regulatoryNotice: "ನಿಯಂತ್ರಣ ಸೂಚನೆ", learnMore: "ಇನ್ನಷ್ಟು ತಿಳಿಯಿರಿ", noCertificationMapping: "ಪ್ರಸ್ತುತ ಮಾದರಿ ಜ್ಞಾನ ಸಂಗ್ರಹದಲ್ಲಿ ಪರಿಶೀಲಿಸಿದ ಪ್ರಮಾಣೀಕರಣ/QCO ಹೊಂದಾಣಿಕೆ ಲಭ್ಯವಿಲ್ಲ.", reportTitle: "ಸ್ಪೆಕ್‌ವೈಸ್ ಆಡಿಟ್ ವರದಿ", print: "ಮುದ್ರಿಸಿ", download: "ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ", noReport: "ವರದಿ ರಚಿಸಲಾಗಿಲ್ಲ.", aboutTitle: "ಸ್ಪೆಕ್‌ವೈಸ್ ಕುರಿತು (SIH26108)", objective: "ಉದ್ದೇಶ", keyPrinciples: "ಮುಖ್ಯ ಎಂಜಿನಿಯರಿಂಗ್ ತತ್ವಗಳು", closeDialog: "ಮುಚ್ಚಿ", loadingResources: "ಬ್ಯಾಕೆಂಡ್‌ನಿಂದ ಪರಿಶೀಲಿಸಿದ ಡೇಟಾವನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ...", failedResources: "ಡೇಟಾ ಸಂಪನ್ಮೂಲಗಳನ್ನು ಲೋಡ್ ಮಾಡಲು ವಿಫಲವಾಗಿದೆ", privacy: "ಗೌಪ್ಯತೆ", terms: "ಬಳಕೆಯ ನಿಯಮಗಳು", contactBis: "BIS ಸಂಪರ್ಕ", verifiedBis: "ಪರಿಶೀಲಿಸಿದ BIS", openSource: "ಮೂಲ URL ತೆರೆಯಿರಿ", openDocument: "ಅಧಿಕೃತ ದಾಖಲೆ URL ತೆರೆಯಿರಿ", relatedStandards: "ಸಂಬಂಧಿತ ಮಾನದಂಡಗಳು", evidenceSources: "ಸಾಕ್ಷ್ಯ ಮೂಲಗಳು", viewAll: "ಎಲ್ಲವನ್ನೂ ನೋಡಿ", noEvidence: "ಈ ಫಲಿತಾಂಶಕ್ಕೆ ಯಾವುದೇ ಸಾಕ್ಷ್ಯ ದಾಖಲೆಗಳಿಲ್ಲ.", retry: "ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ", shareCopied: "ಪುಟದ ಲಿಂಕ್ ನಕಲಿಸಲಾಗಿದೆ!",
  },
  ta: {
    ...english,
    siteTitle: "ஸ்பெக்‌வைஸ்", tagline: "சரியான தரநிலைகள். பாதுகாப்பான கொள்முதல்.",
    heroHeading1: "எந்த இந்திய", heroHeading2: "தரநிலை பொருந்தும் எனத் தெரியவில்லையா?",
    heroSubtitle: "உங்கள் தயாரிப்பை விவரிக்கவும் அல்லது டெண்டர் விவரக்குறிப்புகளை ஒட்டவும். நம்பகமான ஆதாரங்களுடன் தொடர்புடைய BIS தரநிலைகளைக் கண்டறிய ஸ்பெக்‌வைஸ் உதவுகிறது.",
    enterDescription: "விவரத்தை உள்ளிடுக", uploadDoc: "ஆவணத்தைப் பதிவேற்றுக (PDF)", searchPlaceholder: "எ.கா. விவசாய நீர்ப்பாசனத்திற்கான ஓபன்வெல் நீர்மூழ்கி பம்ப்",
    findStandards: "பொருந்தும் தரநிலைகளைக் கண்டறிக", analyzing: "தரநிலைகள் பகுப்பாய்வு செய்யப்படுகின்றன...", examples: "எடுத்துக்காட்டுகள்:", recentSearches: "சமீபத்திய தேடல்கள்:", clearHistory: "அழி",
    coldStartNotice: "பகுப்பாய்வு சேவையுடன் இணைக்கப்படுகிறது. சேவை தொடங்கும்போது முதல் கோரிக்கை சிறிது நேரம் கூடுதலாக எடுக்கலாம்.", officialPortal: "அதிகாரப்பூர்வ தளம்", home: "முகப்பு", howItWorks: "செயல்முறை", resources: "வளங்கள்", about: "எங்களைப் பற்றி",
    prototypeNotice: "முன்மாதிரி · அதிகாரப்பூர்வ BIS தளம் அல்ல", language: "மொழி", close: "மூடு", evidenceSupport: "ஆதார அடிப்படையிலான BIS முடிவு உதவி", bisEngine: "BIS தரநிலை அமைப்பு", verifiedData: "சரிபார்க்கப்பட்ட தரவு",
    informedProcurement: "தகவலறிந்த கொள்முதல் முடிவுகளை எடுக்கவும்", procurementDescription: "டெண்டர் ஆவணங்கள் மற்றும் கொள்முதல் ஆணைகளில் தவறான தரநிலை மேற்கோள்களைத் தவிர்க்கவும்.",
    indianStandards: "இந்திய தரநிலைகள் மற்றும் அதிகாரப்பூர்வ ஆதாரங்களை அடிப்படையாகக் கொண்டது", standardsDescription: "ஒவ்வொரு முடிவும் BIS குழு ஆதாரங்கள், வழிகாட்டுதல்கள் மற்றும் வெளியிடப்பட்ட தரநிலைகளை அடிப்படையாகக் கொண்டது.",
    designedFor: "குடிமக்கள், வாங்குவோர் மற்றும் அரசு பயனர்களுக்காக", designedDescription: "தொழில்நுட்ப இணக்கத்தைக் கண்டறிய உதவும் எளிய மொழிச் சுருக்கங்கள்.",
    enterTender: "தயாரிப்பு விவரம் அல்லது டெண்டர் விவரக்குறிப்பை உள்ளிடுக", uploadTender: "டெண்டர் ஆவணத்தைப் பதிவேற்றுக (PDF)", extractionWorkflow: "ஆவண உரை பிரித்தெடுக்கும் செயல்முறை", browseFiles: "கோப்புகளைத் தேர்ந்தெடுக்கவும்", dragDrop: "டெண்டர் PDF-ஐ இங்கே இழுத்து விடவும்", pdfSupport: "தொழில்நுட்ப விவரக்குறிப்புகள், RFP மற்றும் தேவைகள் பட்டியல் ஆதரிக்கப்படும் (.pdf, அதிகபட்சம் 25MB)", cancel: "ரத்து செய்", processDocument: "ஆவணத்தைச் செயலாக்கு", processing: "செயலாக்கப்படுகிறது…",
    connectionError: "இணைப்பு / API பிழை", retryAnalysis: "பகுப்பாய்வை மீண்டும் முயற்சி செய்", newSearch: "புதிய தேடல்", share: "பகிர்", reportDownload: "அறிக்கையைப் பதிவிறக்கு (Audit HTML)", auditReport: "தணிக்கை அறிக்கை", definitiveMatch: "உறுதியான பொருத்தம்", evaluationResult: "மதிப்பீட்டு முடிவு", reviewRequired: "தொழில்நுட்ப ஆய்வு தேவை", noPrimary: "முதன்மை தரநிலை தேர்ந்தெடுக்கப்படவில்லை", outOfCorpus: "முன்மாதிரி தரவுத்தொகுப்பிற்கு வெளியே", whyDecision: "இந்த முடிவுக்கான காரணம்?", simpleTerms: "எளிய சொற்களில்",
    noPrimaryDescription: "முதன்மை தயாரிப்பு தரநிலையைத் தேர்ந்தெடுக்க உள்ளீடு போதுமான விவரத்துடன் இல்லை.", outOfCorpusDescription: "விவரக்குறிப்பு சரிபார்க்கப்பட்ட MED 20 பம்ப் தரவுத்தொகுப்பிற்கு வெளியே உள்ளது", reviewDescription: "பரிந்துரைக்கப்பட்ட தரநிலைகள் மற்றும் டெண்டர் விவரக்குறிப்புகளை ஆய்வு செய்யவும்", matchedEvidence: "தயாரிப்பு சொற்கள், பயன்பாடு மற்றும் BIS வரம்பு ஆதாரங்களின் அடிப்படையில் பொருத்தப்பட்டது.",
    primaryStandard: "முதன்மை தரநிலை", recommendedCore: "பரிந்துரைக்கப்பட்ட முக்கிய விவரக்குறிப்பு", standardNumber: "தரநிலை எண்", product: "தயாரிப்பு", application: "பயன்பாடு", status: "நிலை", scope: "வரம்பு", whyMatched: "பொருத்தத்திற்கான காரணம்", bisPortal: "BIS தளம்", contextStandards: "சூழல் தரநிலைகள்", contextOnly: "சூழலுக்காக மட்டும் — பரிந்துரை அல்ல", noRecommendation: "தற்போதைய முன்மாதிரி தரவுத்தொகுப்பில் (MED 20 பம்ப் துறை) பொருந்தும் தரநிலை இல்லை.",
    notFormallyConfirmed: "அதிகாரப்பூர்வமாக உறுதிப்படுத்தப்படவில்லை", activeInForce: "நடைமுறையில் உள்ளது", revisionWarning: "திருத்தம் / மாற்றீடு எச்சரிக்கை", certificationStatus: "சான்றிதழ் / QCO நிலை", notApplicable: "பொருந்தாது", notEvaluated: "மதிப்பிடப்படவில்லை", regulatoryNotice: "ஒழுங்குமுறை அறிவிப்பு", learnMore: "மேலும் அறிக", noCertificationMapping: "தற்போதைய முன்மாதிரி அறிவுத் தொகுப்பில் சரிபார்க்கப்பட்ட சான்றிதழ்/QCO பொருத்தம் இல்லை.", reportTitle: "ஸ்பெக்‌வைஸ் தணிக்கை அறிக்கை", print: "அச்சிடு", download: "பதிவிறக்கு", noReport: "அறிக்கை உருவாக்கப்படவில்லை.", aboutTitle: "ஸ்பெக்‌வைஸ் பற்றி (SIH26108)", objective: "நோக்கம்", keyPrinciples: "முக்கிய பொறியியல் கொள்கைகள்", closeDialog: "மூடு", loadingResources: "பின்தளத்திலிருந்து சரிபார்க்கப்பட்ட தரவு ஏற்றப்படுகிறது...", failedResources: "தரவுத்தொகுப்பு வளங்களை ஏற்ற முடியவில்லை", privacy: "தனியுரிமை", terms: "விதிமுறைகள்", contactBis: "BIS-ஐத் தொடர்புகொள்", verifiedBis: "சரிபார்க்கப்பட்ட BIS", openSource: "மூல URL-ஐத் திற", openDocument: "அதிகாரப்பூர்வ ஆவண URL-ஐத் திற", relatedStandards: "தொடர்புடைய தரநிலைகள்", evidenceSources: "ஆதார மூலங்கள்", viewAll: "அனைத்தையும் காண்க", noEvidence: "இந்த முடிவுக்கு ஆதாரப் பதிவுகள் இல்லை.", retry: "மீண்டும் முயற்சி செய்", shareCopied: "பக்க இணைப்பு நகலெடுக்கப்பட்டது!",
  },
  te: {
    ...english,
    siteTitle: "స్పెక్‌వైజ్", tagline: "సరైన ప్రమాణాలు. సురక్షిత కొనుగోలు.",
    heroHeading1: "ఏ భారతీయ", heroHeading2: "ప్రమాణం వర్తిస్తుందో తెలియదా?",
    heroSubtitle: "మీ ఉత్పత్తిని వివరించండి లేదా టెండర్ స్పెసిఫికేషన్‌లను అతికించండి. విశ్వసనీయ మూలాలతో సంబంధిత BIS ప్రమాణాలను కనుగొనడంలో స్పెక్‌వైజ్ సహాయపడుతుంది.",
    enterDescription: "వివరణ నమోదు చేయండి", uploadDoc: "పత్రాన్ని అప్‌లోడ్ చేయండి (PDF)", searchPlaceholder: "ఉదా. వ్యవసాయ నీటిపారుదల కోసం ఓపెన్‌వెల్ సబ్‌మెర్సిబుల్ పంప్‌సెట్",
    findStandards: "వర్తించే ప్రమాణాలను కనుగొనండి", analyzing: "ప్రమాణాలను విశ్లేషిస్తోంది...", examples: "ఉదాహరణలు:", recentSearches: "ఇటీవలి శోధనలు:", clearHistory: "తొలగించు",
    coldStartNotice: "విశ్లేషణ సేవకు కనెక్ట్ అవుతోంది. సేవ ప్రారంభమయ్యే సమయంలో మొదటి అభ్యర్థనకు కొంత అదనపు సమయం పట్టవచ్చు.", officialPortal: "అధికారిక పోర్టల్", home: "హోమ్", howItWorks: "ఇది ఎలా పనిచేస్తుంది", resources: "వనరులు", about: "గురించి",
    prototypeNotice: "ప్రోటోటైప్ · అధికారిక BIS పోర్టల్ కాదు", language: "భాష", close: "మూసివేయండి", evidenceSupport: "ఆధారాలతో BIS నిర్ణయ సహాయం", bisEngine: "BIS ప్రమాణాల ఇంజిన్", verifiedData: "ధృవీకరించిన డేటా",
    informedProcurement: "సమాచారంతో కూడిన కొనుగోలు నిర్ణయాలు తీసుకోండి", procurementDescription: "టెండర్ పత్రాలు, కొనుగోలు ఆర్డర్లలో తప్పు ప్రమాణాల సూచనలను నివారించండి.",
    indianStandards: "భారతీయ ప్రమాణాలు, అధికారిక మూలాల ఆధారంగా", standardsDescription: "ప్రతి ఫలితం BIS కమిటీ ఆధారాలు, మార్గదర్శకాలు, ప్రచురించిన ప్రమాణాలపై ఆధారపడి ఉంటుంది.",
    designedFor: "పౌరులు, కొనుగోలుదారులు, ప్రభుత్వ వినియోగదారుల కోసం", designedDescription: "సాంకేతిక అనుసరణ ఆధారాలతో సరళమైన భాషలో సారాంశాలు.",
    enterTender: "ఉత్పత్తి వివరణ లేదా టెండర్ స్పెసిఫికేషన్ నమోదు చేయండి", uploadTender: "టెండర్ పత్రాన్ని అప్‌లోడ్ చేయండి (PDF)", extractionWorkflow: "పత్రం నుంచి వివరాల వెలికితీత ప్రక్రియ", browseFiles: "ఫైళ్లను ఎంచుకోండి", dragDrop: "టెండర్ PDFను ఇక్కడికి లాగి వదలండి", pdfSupport: "సాంకేతిక స్పెసిఫికేషన్‌లు, RFP, అవసరాల జాబితా మద్దతు (.pdf, గరిష్ఠం 25MB)", cancel: "రద్దు చేయండి", processDocument: "పత్రాన్ని ప్రాసెస్ చేయండి", processing: "ప్రాసెస్ అవుతోంది…",
    connectionError: "కనెక్షన్ / API లోపం", retryAnalysis: "విశ్లేషణను మళ్లీ ప్రయత్నించండి", newSearch: "కొత్త శోధన", share: "షేర్ చేయండి", reportDownload: "నివేదికను డౌన్‌లోడ్ చేయండి (Audit HTML)", auditReport: "ఆడిట్ నివేదిక", definitiveMatch: "ఖచ్చితమైన సరిపోలిక", evaluationResult: "మూల్యాంకన ఫలితం", reviewRequired: "సాంకేతిక సమీక్ష అవసరం", noPrimary: "ప్రాథమిక ప్రమాణం ఎంచుకోలేదు", outOfCorpus: "ప్రోటోటైప్ డేటాసెట్ పరిధికి వెలుపల", whyDecision: "ఈ నిర్ణయానికి కారణం?", simpleTerms: "సరళంగా చెప్పాలంటే",
    noPrimaryDescription: "ప్రాథమిక ఉత్పత్తి ప్రమాణాన్ని ఎంచుకోవడానికి ఇచ్చిన వివరణలో తగిన వివరాలు లేవు.", outOfCorpusDescription: "స్పెసిఫికేషన్ ధృవీకరించిన MED 20 పంప్ డేటాసెట్ పరిధికి వెలుపల ఉంది", reviewDescription: "సూచించిన ప్రమాణాలు, టెండర్ స్పెసిఫికేషన్‌లను సమీక్షించండి", matchedEvidence: "ఉత్పత్తి పదాలు, వినియోగం, BIS పరిధి ఆధారాలతో సరిపోల్చబడింది.",
    primaryStandard: "ప్రాథమిక ప్రమాణం", recommendedCore: "సిఫార్సు చేసిన ప్రధాన స్పెసిఫికేషన్", standardNumber: "ప్రమాణ సంఖ్య", product: "ఉత్పత్తి", application: "వినియోగం", status: "స్థితి", scope: "పరిధి", whyMatched: "సరిపోలిన కారణం", bisPortal: "BIS పోర్టల్", contextStandards: "సందర్భ ప్రమాణాలు", contextOnly: "సందర్భం కోసం మాత్రమే — సిఫార్సు కాదు", noRecommendation: "ప్రస్తుత ప్రోటోటైప్ డేటాసెట్‌లో (MED 20 పంప్ విభాగం) సరిపోలే ప్రమాణం లేదు.",
    notFormallyConfirmed: "అధికారికంగా నిర్ధారించబడలేదు", activeInForce: "అమల్లో ఉంది", revisionWarning: "సవరణ / భర్తీ హెచ్చరిక", certificationStatus: "ధృవీకరణ / QCO స్థితి", notApplicable: "వర్తించదు", notEvaluated: "మూల్యాంకనం చేయలేదు", regulatoryNotice: "నియంత్రణ సమాచారం", learnMore: "మరింత తెలుసుకోండి", noCertificationMapping: "ప్రస్తుత ప్రోటోటైప్ పరిజ్ఞాన భాండాగారంలో ధృవీకరించిన సర్టిఫికేషన్/QCO మ్యాపింగ్ లేదు.", reportTitle: "స్పెక్‌వైజ్ ఆడిట్ నివేదిక", print: "ముద్రించండి", download: "డౌన్‌లోడ్ చేయండి", noReport: "నివేదిక రూపొందించలేదు.", aboutTitle: "స్పెక్‌వైజ్ గురించి (SIH26108)", objective: "లక్ష్యం", keyPrinciples: "ముఖ్య ఇంజినీరింగ్ సూత్రాలు", closeDialog: "మూసివేయండి", loadingResources: "బ్యాకెండ్ నుంచి ధృవీకరించిన డేటా లోడ్ అవుతోంది...", failedResources: "డేటాసెట్ వనరులను లోడ్ చేయలేకపోయాం", privacy: "గోప్యత", terms: "నిబంధనలు", contactBis: "BISను సంప్రదించండి", verifiedBis: "ధృవీకరించిన BIS", openSource: "మూల URL తెరవండి", openDocument: "అధికారిక పత్ర URL తెరవండి", relatedStandards: "సంబంధిత ప్రమాణాలు", evidenceSources: "ఆధార మూలాలు", viewAll: "అన్నీ చూడండి", noEvidence: "ఈ ఫలితానికి ఆధార రికార్డులు అందుబాటులో లేవు.", retry: "మళ్లీ ప్రయత్నించండి", shareCopied: "పేజీ లింక్ కాపీ అయింది!",
  },
};

const extraTranslations: Partial<Record<Language, Translations>> = {
  hi: { resourcesTitle: "डेटासेट संसाधन और स्रोत", resourcesSubtitle: "सत्यापित मानकों, साक्ष्य उद्धरणों, मानक संबंधों और बेंचमार्क मामलों का पारदर्शी संग्रह।", standards: "मानक", evidence: "साक्ष्य", links: "लिंक", benchmarks: "बेंचमार्क", sources: "स्रोत", page: "पृष्ठ", of: "में से", totalItems: "कुल प्रविष्टियाँ", previous: "पिछला", next: "अगला", prototypeCorpus: "प्रोटोटाइप डेटासेट", notFullCatalog: "पूर्ण BIS सूची नहीं", verifiedStandards: "सत्यापित मानक", evidenceRecords: "साक्ष्य रिकॉर्ड", relationships: "संबंध", benchmarkCases: "बेंचमार्क मामले", sourceProvenance: "स्रोत विवरण", searchIn: "इसमें खोजें", roleFilter: "भूमिका फ़िल्टर", allTypes: "सभी मानक प्रकार", primaryProductType: "प्राथमिक उत्पाद मानक", practiceCode: "आचार संहिता", testMethod: "परीक्षण विधि", relatedSpecification: "संबंधित विनिर्देश" },
  kn: { resourcesTitle: "ಡೇಟಾ ಸಂಪನ್ಮೂಲಗಳು ಮತ್ತು ಮೂಲಗಳು", resourcesSubtitle: "ಪರಿಶೀಲಿಸಿದ ಮಾನದಂಡಗಳು, ಸಾಕ್ಷ್ಯ ಉಲ್ಲೇಖಗಳು, ಮಾನದಂಡ ಸಂಬಂಧಗಳು ಮತ್ತು ಮೌಲ್ಯಮಾಪನ ಪ್ರಕರಣಗಳ ಪಾರದರ್ಶಕ ಸಂಗ್ರಹ.", standards: "ಮಾನದಂಡಗಳು", evidence: "ಸಾಕ್ಷ್ಯ", links: "ಲಿಂಕ್‌ಗಳು", benchmarks: "ಮಾನದಂಡ ಪರೀಕ್ಷೆಗಳು", sources: "ಮೂಲಗಳು", page: "ಪುಟ", of: "ರಲ್ಲಿ", totalItems: "ಒಟ್ಟು ದಾಖಲೆಗಳು", previous: "ಹಿಂದಿನ", next: "ಮುಂದಿನ", prototypeCorpus: "ಮಾದರಿ ಡೇಟಾಸೆಟ್", notFullCatalog: "ಸಂಪೂರ್ಣ BIS ಪಟ್ಟಿ ಅಲ್ಲ", verifiedStandards: "ಪರಿಶೀಲಿಸಿದ ಮಾನದಂಡಗಳು", evidenceRecords: "ಸಾಕ್ಷ್ಯ ದಾಖಲೆಗಳು", relationships: "ಸಂಬಂಧಗಳು", benchmarkCases: "ಮೌಲ್ಯಮಾಪನ ಪ್ರಕರಣಗಳು", sourceProvenance: "ಮೂಲ ವಿವರಗಳು", searchIn: "ಇಲ್ಲಿ ಹುಡುಕಿ", roleFilter: "ಪಾತ್ರದ ಫಿಲ್ಟರ್", allTypes: "ಎಲ್ಲಾ ಮಾನದಂಡ ಪ್ರಕಾರಗಳು", primaryProductType: "ಪ್ರಾಥಮಿಕ ಉತ್ಪನ್ನ ಮಾನದಂಡ", practiceCode: "ಆಚರಣಾ ಸಂಹಿತೆ", testMethod: "ಪರೀಕ್ಷಾ ವಿಧಾನ", relatedSpecification: "ಸಂಬಂಧಿತ ವಿಶೇಷಣ" },
  ta: { resourcesTitle: "தரவுத்தொகுப்பு வளங்கள் மற்றும் ஆதாரங்கள்", resourcesSubtitle: "சரிபார்க்கப்பட்ட தரநிலைகள், ஆதார மேற்கோள்கள், தரநிலை உறவுகள் மற்றும் மதிப்பீட்டு நிகழ்வுகளின் வெளிப்படையான தொகுப்பு.", standards: "தரநிலைகள்", evidence: "ஆதாரங்கள்", links: "இணைப்புகள்", benchmarks: "அளவுகோல்கள்", sources: "மூலங்கள்", page: "பக்கம்", of: "இல்", totalItems: "மொத்தப் பதிவுகள்", previous: "முந்தையது", next: "அடுத்தது", prototypeCorpus: "முன்மாதிரி தரவுத்தொகுப்பு", notFullCatalog: "முழு BIS பட்டியல் அல்ல", verifiedStandards: "சரிபார்க்கப்பட்ட தரநிலைகள்", evidenceRecords: "ஆதாரப் பதிவுகள்", relationships: "உறவுகள்", benchmarkCases: "மதிப்பீட்டு நிகழ்வுகள்", sourceProvenance: "மூல விவரங்கள்", searchIn: "இதில் தேடு", roleFilter: "பங்கு வடிகட்டி", allTypes: "அனைத்து தரநிலை வகைகள்", primaryProductType: "முதன்மை தயாரிப்பு தரநிலை", practiceCode: "நடைமுறை குறியீடு", testMethod: "சோதனை முறை", relatedSpecification: "தொடர்புடைய விவரக்குறிப்பு" },
  te: { resourcesTitle: "డేటాసెట్ వనరులు, ఆధారాలు", resourcesSubtitle: "ధృవీకరించిన ప్రమాణాలు, ఆధార సూచనలు, ప్రమాణ సంబంధాలు, మూల్యాంకన కేసుల పారదర్శక సమాహారం.", standards: "ప్రమాణాలు", evidence: "ఆధారాలు", links: "లింకులు", benchmarks: "బెంచ్‌మార్క్‌లు", sources: "మూలాలు", page: "పేజీ", of: "లో", totalItems: "మొత్తం అంశాలు", previous: "మునుపటి", next: "తదుపరి", prototypeCorpus: "ప్రోటోటైప్ డేటాసెట్", notFullCatalog: "పూర్తి BIS జాబితా కాదు", verifiedStandards: "ధృవీకరించిన ప్రమాణాలు", evidenceRecords: "ఆధార రికార్డులు", relationships: "సంబంధాలు", benchmarkCases: "మూల్యాంకన కేసులు", sourceProvenance: "మూల వివరాలు", searchIn: "ఇందులో వెతకండి", roleFilter: "పాత్ర ఫిల్టర్", allTypes: "అన్ని ప్రమాణ రకాలు", primaryProductType: "ప్రాథమిక ఉత్పత్తి ప్రమాణం", practiceCode: "ఆచరణ నియమావళి", testMethod: "పరీక్షా పద్ధతి", relatedSpecification: "సంబంధిత స్పెసిఫికేషన్" },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: Translations;
}

const LanguageContext = createContext<LanguageContextType>({ language: "en", setLanguage: () => {}, t: english });

function isLanguage(value: string | null): value is Language {
  return !!value && (languages as readonly string[]).includes(value);
}

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>("en");

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("specwise_lang");
      if (isLanguage(saved)) setLanguageState(saved);
    } catch {
      // Storage can be unavailable in private browsing; English remains usable.
    }
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    try {
      localStorage.setItem("specwise_lang", lang);
    } catch {
      // Keep the selected language for this session even if storage is unavailable.
    }
  };

  const t = useMemo(() => new Proxy(dictionary[language], {
    get: (translations, key: string) => translations[key] ?? extraTranslations[language]?.[key] ?? english[key] ?? String(key),
  }), [language]);

  return <LanguageContext.Provider value={{ language, setLanguage, t }}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  return useContext(LanguageContext);
}
