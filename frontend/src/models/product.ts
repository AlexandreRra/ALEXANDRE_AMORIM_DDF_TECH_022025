export interface ProductDistribution {
  product_type_id: number;
  count: number;
}

export interface ProductScatter {
  product_length: number;
  product_type_id: number;
}

export interface EmptyColumnDistribution {
  category: string;
  count: number;
}

export interface Product {
  product_id: string;
  title: string | null;
  bullet_points: string | null;
  description: string | null;
  product_type_id: number | null;
  product_length: number | null;
  empty_cols: string | null;
}

export interface PaginatedProducts {
  data: Product[];
  total: number;
}

export interface TemporalTrend {
  product_type_id: number;
  count: number;
}

export interface DensityHeatmap {
  length_bucket: number;
  product_type_id: number;
  count: number;
}