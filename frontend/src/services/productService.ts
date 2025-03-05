import axios from 'axios';
import { DensityHeatmap, EmptyColumnDistribution, Product, ProductDistribution, ProductScatter, TemporalTrend } from '../models/product';

const API_URL = 'http://localhost:5000/products';

export const fetchProductDistribution = async (): Promise<ProductDistribution[]> => {
  try {
    const response = await axios.get<ProductDistribution[]>(`${API_URL}/distribution`);
    if (!Array.isArray(response.data)) {
      throw new Error('Response data is not an array');
    }
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(`Failed to fetch product distribution: ${error.response?.status} ${error.response?.data?.message || error.message}`);
    }
    throw error instanceof Error ? error : new Error('Unknown error occurred');
  }
};

export const fetchScatterDistribution = async (): Promise<ProductScatter[]> => {
  try {
    const response = await axios.get<ProductScatter[]>(`${API_URL}/scatter-distribution`);
    if (!Array.isArray(response.data)) {
      throw new Error('Response data is not an array');
    }
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(`Failed to fetch scatter distribution: ${error.response?.status} ${error.response?.data?.message || error.message}`);
    }
    throw error instanceof Error ? error : new Error('Unknown error occurred');
  }
};

export const fetchEmptyColumnsDistribution = async (): Promise<EmptyColumnDistribution[]> => {
  try {
    const response = await axios.get<EmptyColumnDistribution[]>(`${API_URL}/empty-columns`);
    if (!Array.isArray(response.data)) {
      throw new Error('Response data is not an array');
    }
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(`Failed to fetch empty columns distribution: ${error.response?.status} ${error.response?.data?.message || error.message}`);
    }
    throw error instanceof Error ? error : new Error('Unknown error occurred');
  }
};

export const fetchProductsByEmpty = async (category: string, page: number = 1, pageSize: number = 50): Promise<{ data: Product[]; total: number }> => {
  try {
    const response = await axios.get<{ data: Product[]; total: number }>(
      `${API_URL}/products-by-empty?category=${encodeURIComponent(category)}&page=${page}&pageSize=${pageSize}`
    );
    if (!Array.isArray(response.data.data)) {
      throw new Error('Response data is not an array');
    }
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(`Failed to fetch products by empty category: ${error.response?.status} ${error.response?.data?.message || error.message}`);
    }
    throw error instanceof Error ? error : new Error('Unknown error occurred');
  }
};

export const fetchTemporalTrend = async (): Promise<TemporalTrend[]> => {
  try {
    const response = await axios.get<TemporalTrend[]>(`${API_URL}/temporal-trend`);
    if (!Array.isArray(response.data)) {
      throw new Error('Response data is not an array');
    }
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(`Failed to fetch temporal trend: ${error.response?.status} ${error.response?.data?.message || error.message}`);
    }
    throw error instanceof Error ? error : new Error('Unknown error occurred');
  }
};

export const fetchDensityHeatmap = async (): Promise<DensityHeatmap[]> => {
  try {
    const response = await axios.get<DensityHeatmap[]>(`${API_URL}/density-heatmap`);
    if (!Array.isArray(response.data)) {
      throw new Error('Response data is not an array');
    }
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(`Failed to fetch density heatmap: ${error.response?.status} ${error.response?.data?.message || error.message}`);
    }
    throw error instanceof Error ? error : new Error('Unknown error occurred');
  }
};