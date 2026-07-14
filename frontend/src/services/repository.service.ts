import api from './api';
import type { IndexRequest, RepositoryIndexResponse } from '@/types';

export const repositoryService = {
  indexRepository: async (payload: IndexRequest): Promise<RepositoryIndexResponse> => {
    const { data } = await api.post<RepositoryIndexResponse>('/index', payload);
    return data;
  },
};
