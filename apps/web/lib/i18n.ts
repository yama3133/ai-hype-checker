export type Locale = "ja" | "en";

export const LOCALES: { code: Locale; label: string }[] = [
  { code: "ja", label: "日本語" },
  { code: "en", label: "English" },
];

export const DEFAULT_LOCALE: Locale = "ja";

interface Dict {
  appTitle: string;
  appDescription: string;
  placeholder: string;
  submit: string;
  submitting: string;
  scoreLabel: string;
  verdictHype: string;
  verdictExaggerated: string;
  verdictGrounded: string;
  verdictFailed: string;
  reasonsLabel: string;
  flaggedPhrasesLabel: string;
  errorGeneric: string;
  language: string;
}

export const DICTIONARIES: Record<Locale, Dict> = {
  ja: {
    appTitle: "AI驚き屋発見器",
    appDescription:
      "X（旧Twitter）のAI関連投稿を貼り付けると、誇張・扇動表現と技術的根拠を分析して「驚き屋度」を判定します。",
    placeholder: "判定したい投稿の本文をここに貼り付けてください",
    submit: "判定する",
    submitting: "判定中...",
    scoreLabel: "驚き屋度スコア",
    verdictHype: "驚き屋",
    verdictExaggerated: "やや誇張",
    verdictGrounded: "堅実",
    verdictFailed: "判定失敗",
    reasonsLabel: "判定理由",
    flaggedPhrasesLabel: "検出された煽り文句",
    errorGeneric: "判定に失敗しました",
    language: "言語",
  },
  en: {
    appTitle: "AI Hype Detector",
    appDescription:
      "Paste an AI-related post from X (formerly Twitter) to analyze exaggerated claims and technical evidence, and get a hype score.",
    placeholder: "Paste the post text you want to check here",
    submit: "Check",
    submitting: "Checking...",
    scoreLabel: "Hype score",
    verdictHype: "Hype",
    verdictExaggerated: "Somewhat exaggerated",
    verdictGrounded: "Grounded",
    verdictFailed: "Failed",
    reasonsLabel: "Reasons",
    flaggedPhrasesLabel: "Flagged phrases",
    errorGeneric: "Failed to check this post",
    language: "Language",
  },
};
