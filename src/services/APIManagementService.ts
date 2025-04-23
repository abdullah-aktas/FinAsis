import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import axios from 'axios';
import { createLogger } from '../utils/logger';
import { create } from 'zustand';

const logger = createLogger('APIManagementService');

// Zustand store tanımlaması
interface APIState {
    loading: boolean;
    error: string | null;
    data: any;
    setLoading: (loading: boolean) => void;
    setError: (error: string | null) => void;
    setData: (data: any) => void;
}

export const useAPIStore = create<APIState>((set) => ({
    loading: false,
    error: null,
    data: null,
    setLoading: (loading) => set({ loading }),
    setError: (error) => set({ error }),
    setData: (data) => set({ data }),
}));

export class APIManagementService {
    private static instance: APIManagementService;
    private apolloClient: ApolloClient<any>;
    private axiosInstance: any;
    private apiConfig: any;

    private constructor() {
        this.apiConfig = {
            graphql: {
                uri: process.env.REACT_APP_GRAPHQL_URI || 'http://localhost:4000/graphql',
                headers: {
                    'Content-Type': 'application/json',
                },
            },
            rest: {
                baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:4000/api',
                timeout: 5000,
                headers: {
                    'Content-Type': 'application/json',
                },
            },
        };

        // Apollo Client kurulumu
        const httpLink = createHttpLink({
            uri: this.apiConfig.graphql.uri,
        });

        const authLink = setContext((_, { headers }) => {
            const token = localStorage.getItem('token');
            return {
                headers: {
                    ...headers,
                    authorization: token ? `Bearer ${token}` : '',
                },
            };
        });

        this.apolloClient = new ApolloClient({
            link: authLink.concat(httpLink),
            cache: new InMemoryCache(),
        });

        // Axios instance kurulumu
        this.axiosInstance = axios.create(this.apiConfig.rest);
        this.setupAxiosInterceptors();
    }

    public static getInstance(): APIManagementService {
        if (!APIManagementService.instance) {
            APIManagementService.instance = new APIManagementService();
        }
        return APIManagementService.instance;
    }

    // Axios interceptor'ları kur
    private setupAxiosInterceptors(): void {
        // İstek interceptor'u
        this.axiosInstance.interceptors.request.use(
            (config) => {
                useAPIStore.getState().setLoading(true);
                const token = localStorage.getItem('token');
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
                return config;
            },
            (error) => {
                useAPIStore.getState().setLoading(false);
                useAPIStore.getState().setError(error.message);
                return Promise.reject(error);
            }
        );

        // Yanıt interceptor'u
        this.axiosInstance.interceptors.response.use(
            (response) => {
                useAPIStore.getState().setLoading(false);
                return response;
            },
            (error) => {
                useAPIStore.getState().setLoading(false);
                useAPIStore.getState().setError(error.message);
                return Promise.reject(error);
            }
        );
    }

    // GraphQL sorgusu çalıştır
    public async executeGraphQLQuery<T>(
        query: any,
        variables?: any
    ): Promise<T> {
        try {
            useAPIStore.getState().setLoading(true);
            const { data } = await this.apolloClient.query({
                query,
                variables,
                fetchPolicy: 'network-only',
            });
            useAPIStore.getState().setData(data);
            return data;
        } catch (error: any) {
            logger.error('GraphQL sorgu hatası:', error);
            useAPIStore.getState().setError(error.message);
            throw new Error('GraphQL sorgusu başarısız oldu');
        } finally {
            useAPIStore.getState().setLoading(false);
        }
    }

    // REST API isteği gönder
    public async executeRESTRequest<T>(
        method: 'get' | 'post' | 'put' | 'delete',
        url: string,
        data?: any
    ): Promise<T> {
        try {
            useAPIStore.getState().setLoading(true);
            const response = await this.axiosInstance[method](url, data);
            useAPIStore.getState().setData(response.data);
            return response.data;
        } catch (error: any) {
            logger.error('REST istek hatası:', error);
            useAPIStore.getState().setError(error.message);
            throw new Error('REST isteği başarısız oldu');
        } finally {
            useAPIStore.getState().setLoading(false);
        }
    }

    // API yapılandırmasını güncelle
    public updateAPIConfig(newConfig: any): void {
        try {
            this.apiConfig = {
                ...this.apiConfig,
                ...newConfig,
            };

            // Apollo Client'ı güncelle
            this.apolloClient = new ApolloClient({
                link: createHttpLink({
                    uri: this.apiConfig.graphql.uri,
                }),
                cache: new InMemoryCache(),
            });

            // Axios instance'ı güncelle
            this.axiosInstance = axios.create(this.apiConfig.rest);
            this.setupAxiosInterceptors();

            logger.info('API yapılandırması güncellendi');
        } catch (error) {
            logger.error('API yapılandırma güncelleme hatası:', error);
            throw new Error('API yapılandırması güncellenemedi');
        }
    }

    // API durumunu kontrol et
    public async checkAPIStatus(): Promise<{
        graphql: boolean;
        rest: boolean;
    }> {
        try {
            const [graphqlStatus, restStatus] = await Promise.all([
                this.apolloClient.query({
                    query: `
                        query {
                            __typename
                        }
                    `,
                }),
                this.axiosInstance.get('/health'),
            ]);

            return {
                graphql: !!graphqlStatus,
                rest: restStatus.status === 200,
            };
        } catch (error) {
            logger.error('API durum kontrolü hatası:', error);
            throw new Error('API durum kontrolü başarısız oldu');
        }
    }

    // API önbelleğini temizle
    public clearAPICache(): void {
        try {
            this.apolloClient.cache.reset();
            logger.info('API önbelleği temizlendi');
        } catch (error) {
            logger.error('API önbellek temizleme hatası:', error);
            throw new Error('API önbelleği temizlenemedi');
        }
    }
} 