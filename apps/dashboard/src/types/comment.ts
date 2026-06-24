export type SentimentLabel = "Positif" | "Negatif" | "Netral";

export interface LabeledComment {
  id: string;
  platform: string;
  sourceId: string;
  sourceType: string;
  text: string;
  sourceUrl?: string;
  postedAt?: string;
  labeling_review: SentimentLabel;
  authorDisplayName?: string;
}

export interface SocialComment {
  platform: string;
  source_type: string;
  source_id: string;
  text: string;
  source_url?: string;
}

export interface LabeledStats {
  total: number;
  labels: {
    Positif: number;
    Negatif: number;
    Netral: number;
  };
  platforms: {
    [platform: string]: {
      Positif: number;
      Negatif: number;
      Netral: number;
    };
  };
}
