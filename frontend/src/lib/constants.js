export const TECH_CATEGORIES = [
  { value: "ai_ml", label: "AI / ML" },
  { value: "automation", label: "Automation" },
  { value: "business_process", label: "Business process" },
  { value: "other", label: "Other" },
];

export const TECH_CATEGORY_LABELS = TECH_CATEGORIES.reduce((acc, cat) => {
  acc[cat.value] = cat.label;
  return acc;
}, {});
